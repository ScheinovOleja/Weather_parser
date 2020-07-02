import argparse  # библиотека для обработки консоли
from parser_engine import GetOpenMap, GetYandex  # импорт движка
import DataBase  # импорт БД
from exception import *  # всех пользовательских ошибок

# формат ввода в консоль для OWM "python Weather_parser.py -s=1 -c=Moscow,RU -ch=[add/print]
# для вывода из базы данных название города пишется на Русскойм языке для обоих сайтов!!!!
# пример: python Weather_parser.py -s=[1/2] -c=Москва -ch=print
# формат ввода в консоль для Yandex "python Weather_parser.py -s=2 -r=[10-12/24] -c=Moscow -ch=[add/print]
parser = argparse.ArgumentParser()  # создание объекта консоли
parser.add_argument('-c', '--city', type=str, help='Ввод желаемого города(для получения данных - на русском языке,'
                                                   'для занесения данных - на английском)')
parser.add_argument('-s', '--site', type=str, help='Введите 1, чтобы брать данные с OpenWeatherMap.org'
                                                   'Введите 2, чтобы брать данные с Yandex.ru/pogoda')
parser.add_argument('-r', '--range', type=str, help='Ввод диапазона дат')
parser.add_argument('-ch', "--choice", type=str, help='Ваш выбор:'
                                                      '-ch=add - добавить в базу данных'
                                                      '-ch=print - вывести на консоль информацию о погоде в городе')
# объявление используемых аргументов для консоли
args = parser.parse_args()


# функция для получения данных
def get_from_open_weather(city, inp):
    open_weather = GetOpenMap(city=city)  # объявление класса для OWM
    open_list = open_weather.run(inp)  # запусак функции run из класса для OWM
    if inp == '1':
        data_base_owm.run_cur(open_list)  # запуск функции для занесения в БД
    elif inp == '2':
        data_base_owm.run_forecast(open_list)  # запуск функции для занесения в БД


def print_from_database_owm(city, inp):
    if inp == '1':
        data_base_owm.print_cur(city)  # запуск функции для вывода из БД
    elif inp == '2':
        data_base_owm.print_forecast(city)  # запуск функции для вывода из БД


def get_from_yandex(city, range):
    weather = GetYandex(user_city=city, range_date=range)  # Объявление класса для Yandex
    weather_list = weather.run()  # запусак функции run из класса для Yandex
    data_base_yan.run(weather_list)  # запуск функции для занесения в БД
    return weather_list


def print_from_database_yandex(date, city):
    data_base_yan.print_data(date_range=date, city=city)


# основной блок программы
if __name__ == '__main__':
    # *---Using Python 3.8.3---*
    city = args.city
    site = args.site
    choice = args.choice
    range_date = args.range
    data_base_yan = DataBase.TreatmentYandex(city, range_date)  # объявление базы данных
    data_base_owm = DataBase.TreatmentOWM()  # объявление базы данных
    if site == '1':
        inp = input('Что вы хотите получить?:\n'
                    '1 - Данные на весь день\n'
                    '2 - Прогноз по часам на ближайшие дни\n')
        if choice == 'add':
            get_from_open_weather(city, inp)
            print('Данные занесены в БД!')
        elif choice == 'print':
            print_from_database_owm(city, inp)
        else:
            raise GetExcept()  # Вывод ошибки
    elif site == '2':
        if choice == 'add':
            get_from_yandex(city, range_date)
            print('Данные занесены в БД!')
        elif choice == 'print':
            print_from_database_yandex(range_date, city)
        else:
            raise GetExcept()
