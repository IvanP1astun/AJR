import requests
import time
import random
import os
from dotenv import load_dotenv

load_dotenv()

ACCESS_TOKEN = os.getenv('HH_TOKEN')
RESUME_ID = os.getenv('HH_RESUME_ID')
USER_EMAIL = os.getenv('MY_EMAIL')

# Настройки заголовков (User-Agent теперь тоже берет email из .env)
HEADERS = {
    'User-Agent': f'HH-AutoApply-Bot/1.0 ({USER_EMAIL})',
    'Authorization': f'Bearer {ACCESS_TOKEN}'
}

# Остальная логика фильтрации и поиска
SEARCH_QUERIES = ['Python стажер', 'Python junior', 'Devops инженер', 'Python', 'Python разработчик']
STOP_WORDS = ['senior', 'middle', 'lead', 'java', 'c#', 'опыт от 3 лет']


def get_vacancies(query):
    pass


def apply(v_id, v_title):
    pass


def main():
    pass


if __name__ == '__main__':
    main()
