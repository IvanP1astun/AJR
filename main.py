import requests
import time
import random
import os
from dotenv import load_dotenv

load_dotenv()

ACCESS_TOKEN = os.getenv('HH_TOKEN')
RESUME_ID = os.getenv('HH_RESUME_ID')
USER_EMAIL = os.getenv('MY_EMAIL')

if not all([ACCESS_TOKEN, RESUME_ID, USER_EMAIL]):
    print("❌ Ошибка: Проверь файл .env! Не все переменные загружены.")
    exit()

# Настройки заголовков (User-Agent теперь тоже берет email из .env)
HEADERS = {
    'User-Agent': f'HH-AutoApply-Bot/1.0 ({USER_EMAIL})',
    'Authorization': f'Bearer {ACCESS_TOKEN}'
}

# Остальная логика фильтрации и поиска
SEARCH_QUERIES = ['Python стажер', 'Python junior', 'Devops инженер', 'Python', 'Python разработчик']
STOP_WORDS = ['senior', 'middle', 'lead', 'java', 'c#', 'опыт от 3 лет']


def get_vacancies(query):
    """Поиск вакансий через API HH"""
    url = "https://api.hh.ru/vacancies"
    params = {
        'text': query,
        'area': 113, # Москва - 1/Россия - 113
        'per_page': 50,
        'experience': ['noExperience', 'between1And3'],
        'search_field': 'name'
    }
    try:
        r = requests.get(url, params=params, headers=HEADERS, timeout=10)
        r.raise_for_status()
        return r.json().get('items', [])
    except Exception as e:
        print(f"Ошибка при поиске: {e}")
        return []


def apply_to_vacancy(vacancy):
    """Логика фильтрации и отправки отклика"""
    v_id = vacancy['id']
    v_title = vacancy['name']
    company_name = vacancy.get('employer', {}).get('name', 'вашу компанию')

    # Фильтр стоп-слов
    if any(word in v_title.lower() for word in STOP_WORDS):
        print(f"⏭️ Пропуск (стоп-слово): {v_title}")
        return False
    # Персонализированное сообщение
    message_text = f"""Здравствуйте!
Меня заинтересовала вакансия в {company_name}.
Я специализируюсь на Python-разработке и сейчас ищу позицию,
где смогу применить свои навыки и быстро расти как специалист.
Буду рад выполнить тестовое задание или пройти техническое интервью."""

    url = "https://api.hh.ru/negotiations"
    data = {
        'vacancy_id': v_id,
        'resume_id': RESUME_ID,
        'message': message_text
    }

    try:
        res = requests.post(url, data=data, headers=HEADERS)
        if res.status_code == 201:
            print(f"✅ Успешный отклик: {v_title} в {company_name}")
            return True
        elif res.status_code == 403:
            print(f"ℹ️ Уже откликались или лимит: {v_title}")
        else:
            print(f"❌ Ошибка {res.status_code} на {v_title}: {res.text}")
    except Exception as e:
        print(f"🚨 Критическая ошибка при отклике: {e}")
    return False


def main():
    print("🚀 Автокликер запущен...")
    processed_count = 0
    for query in SEARCH_QUERIES:
        print(f"\n--- Ищем по запросу: {query} ---")
        vacancies = get_vacancies(query)
        for vac in vacancies:
            success = apply_to_vacancy(vac)
            if success:
                processed_count += 1
                wait = random.uniform(15, 60)
                print(f"💤 Ждем {wait:.1f} сек...")
                time.sleep(wait)

    print(f"\n🎯 Работа завершена! Всего новых откликов: {processed_count}")


if __name__ == '__main__':
    main()
