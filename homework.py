import os
import requests
import telegram
import time
from dotenv import load_dotenv

load_dotenv()


PRACTICUM_TOKEN = os.getenv("PRACTICUM_TOKEN")
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')
API_URL = 'https://praktikum.yandex.ru/api/user_api/homework_statuses/'


def parse_homework_status(homework):
    homework_name = homework.get('homework_name')
    if homework_name is None:
        return 'Не удалось получить данные по работе!'
    elif homework['status'] == 'rejected':
        verdict = 'К сожалению в работе нашлись ошибки.'
    elif homework['status'] == 'approved':
        verdict = 'Ревьюеру всё понравилось, можно приступать к следующему уроку.'
    else:
        verdict = 'Но у работы неизвестный статус.'
    return f'У вас проверили работу "{homework_name}"!\n\n{verdict}'


def get_homework_statuses(current_timestamp):
    headers = {'Authorization': f'OAuth {PRACTICUM_TOKEN}'}
    if current_timestamp is None:
        current_timestamp = int(time.time())
    params = {'from_date': current_timestamp}

    try:
        homework_statuses = requests.get(API_URL, headers=headers,
                                         params=params)
    except requests.exceptions.ConnectionError as e:
        print('Connection error!')
        raise SystemExit(e)
    except requests.exceptions.Timeout:
        print('Connection timeout!')
    except requests.exceptions.TooManyRedirects as e:
        print('Too many redirects!')
        raise SystemExit(e)
    except requests.exceptions.RequestException as e:
        raise SystemExit(e)

    return homework_statuses.json()


def send_message(message):
    bot = telegram.Bot(token=TELEGRAM_TOKEN)
    return bot.send_message(chat_id=CHAT_ID, text=message)


def main():
    current_timestamp = int(time.time())

    while True:
        try:
            new_homework = get_homework_statuses(current_timestamp)
            if new_homework.get('homeworks'):
                send_message(parse_homework_status(new_homework.get('homeworks')[0]))
            current_timestamp = new_homework.get('current_date')
            time.sleep(1200)

        except Exception as e:
            print(f'Бот упал с ошибкой: {e}')
            time.sleep(5)
            continue


if __name__ == '__main__':
    main()
