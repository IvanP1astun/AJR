import requests
import time
import random
import os
from dotenv import load_dotenv, set_key

# 1. Загрузка конфигурации
load_dotenv()


def get_current_config():
    """Всегда берет актуальные данные из переменных окружения"""
    return {
        'ACCESS_TOKEN': os.getenv('HH_TOKEN'),
        'REFRESH_TOKEN': os.getenv('HH_REFRESH_TOKEN'),
        'CLIENT_ID': os.getenv('HH_CLIENT_ID'),
        'CLIENT_SECRET': os.getenv('HH_CLIENT_SECRET'),
        'RESUME_ID': os.getenv('HH_RESUME_ID'),
        'USER_EMAIL': os.getenv('MY_EMAIL')
    }


# Настройки поиска
SEARCH_QUERIES = [
    'Python стажер', 'Python junior', 'Devops инженер', 
    'Python разработчик', 'Программист стажер'
]
STOP_WORDS = ['senior', 'middle', 'java', 'c#', 'опыт от 3 лет']


def get_headers():
    """Генерирует заголовки с актуальным токеном и корректным User-Agent"""
    conf = get_current_config()
    return {
        # Маскировка под реальное приложение для обхода 403 при поиске
        'User-Agent': f'Mozilla/5.0 (Windows NT 10.0; Win64; x64) HH-AutoApply-Python/{conf["USER_EMAIL"]}',
        'Authorization': f'Bearer {conf["ACCESS_TOKEN"]}',
        'Accept': 'application/json',
        'Accept-Language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7'
    }


def refresh_token():
    """Автоматически обновляет протухший access_token"""
    conf = get_current_config()
    print("🔄 Токен истек. Пытаюсь обновить...")
    url = "https://api.hh.ru/token"
    data = {
        'grant_type': 'refresh_token',
        'refresh_token': conf['REFRESH_TOKEN'],
        'client_id': conf['CLIENT_ID'],
        'client_secret': conf['CLIENT_SECRET']
    }
    try:
        res = requests.post(url, data=data, timeout=10)
        if res.status_code == 200:
            new_data = res.json()
            set_key(".env", "HH_TOKEN", new_data['access_token'])
            set_key(".env", "HH_REFRESH_TOKEN", new_data['refresh_token'])
            # Перезагружаем переменные в текущий сеанс
            load_dotenv(override=True)
            print("✅ Токены обновлены успешно!")
            return True
        else:
            print(f"❌ Ошибка рефреша ({res.status_code}): {res.text}")
            return False
    except Exception as e:
        print(f"🚨 Критическая ошибка при обновлении: {e}")
        return False


def get_vacancies(query):
    """Поиск вакансий с обработкой ошибок"""
    url = "https://api.hh.ru/vacancies"
    params = {
        'text': query,
        'area': 113,
        'per_page': 50,
        'experience': ['noExperience', 'between1And3'],
        'search_field': 'name'
    }
    try:
        r = requests.get(url, params=params, headers=get_headers(), timeout=10)
        if r.status_code == 401:
            if refresh_token(): return get_vacancies(query)
        if r.status_code == 403:
            print(f"⚠️ HH заблокировал поиск по запросу '{query}'. Возможно, нужна капча или пауза.")
            return []
        r.raise_for_status()
        items = r.json().get('items', [])
        print(f"🔎 По запросу '{query}' найдено: {len(items)}")
        return items
    except Exception as e:
        print(f"❌ Ошибка при поиске: {e}")
        return []


def apply_to_vacancy(vacancy):
    """Фильтрация и отправка отклика"""
    v_id = vacancy['id']
    v_title = vacancy['name']
    company = vacancy.get('employer', {}).get('name', 'компанию')
    if any(word in v_title.lower() for word in STOP_WORDS):

        return False

    conf = get_current_config()
    message = f"Здравствуйте! Меня заинтересовала вакансия {v_title} в {company}. Я специализируюсь на Python и готов выполнить тестовое задание."
    url = "https://api.hh.ru/negotiations"
    data = {
        'vacancy_id': v_id,
        'resume_id': conf['RESUME_ID'],
        'message': message
    }

    try:
        res = requests.post(url, data=data, headers=get_headers(), timeout=10)
        if res.status_code == 401:
            if refresh_token(): return apply_to_vacancy(vacancy)
        if res.status_code == 201:
            print(f"✅ Отклик отправлен: {v_title} ({company})")
            return True
        elif res.status_code == 403:
            # Ошибка 403 при отклике чаще всего означает "уже откликались"
            return False
        else:
            print(f"ℹ️ Пропуск {v_title}: {res.status_code}")
            return False
    except Exception as e:
        print(f"🚨 Ошибка отклика: {e}")
        return False


def main():
    conf = get_current_config()
    if not all([conf['ACCESS_TOKEN'], conf['RESUME_ID']]):
        print("❌ Ошибка: Заполни .env!")
        return

    print("🚀 Автокликер запущен...")
    processed_count = 0
    applied_ids = set()

    for query in SEARCH_QUERIES:
        print(f"\n--- Обработка запроса: {query} ---")
        vacancies = get_vacancies(query)
        for vac in vacancies:
            if vac['id'] in applied_ids:
                continue
            success = apply_to_vacancy(vac)
            applied_ids.add(vac['id'])
            if success:
                processed_count += 1
                # Случайная пауза, чтобы HH не забанил
                wait = random.uniform(20, 60)
                print(f"💤 Пауза {wait:.1f} сек...")
                time.sleep(wait)

    print(f"\n🎯 Готово! Новых откликов: {processed_count}")


if __name__ == '__main__':
    main()
