# -*- encoding: utf-8 -*-
import requests as req # библиотека для взаимодействия с веб-содержимым
import bs4 as bs  # библиотека для выдергивания из html-разметки тэгов
from datetime import datetime  # встроенная библиотека для работы с датой и временем


# Класс для работы с OpenWeatherMap
class GetOpenMap:

    # конструктор
    def __init__(self, city):
        self.APPID = "e7f29c29239892b02213cf1af27952b7"  # apikey, который получается после регистрации на сайте openweathermap.org
        self.direction = ['С ', 'СВ', ' В', 'ЮВ', 'Ю ', 'ЮЗ', ' З', 'СЗ']  # список направлений ветра
        self.city = city  # переменная для города
        self.city_id = None  # переменная для id города
        self.data = None  # переменная для массива данных из result
        self.result = None  # переменная для результатов обработки
        self.final_list = []  # список для словарей данных

    # Получение направления ветра
    def get_wind_direction(self, deg):
        for i in range(0, 8):
            step = 45.
            minimal = i * step - 45 / 2.  # расчет ветра, чтобы понять куда он дует(в инете нашел)
            maximum = i * step + 45 / 2.
            if i == 0 and deg > 360 - 45 / 2.:
                deg = deg - 360
            if minimal <= deg <= maximum:
                res = self.direction[i]
                break
        return res

    # Проверка наличия в базе информации о нужном населенном пункте
    def get_city_id(self):
        try:  # конструкция для обработки исключений
            self.result = req.get("http://api.openweathermap.org/data/2.5/find",
                                       params={'q': self.city, 'type': 'like', 'units': 'metric', 'lang': 'ru',
                                               'APPID': self.APPID})  # поиск города в базе, для получения его id
            self.data = self.result.json()  # преобразование данных из result в json для удобства обработки
            cities = ["{} ({})".format(d['name'], d['sys']['country'])
                      for d in self.data['list']]  # список найденных городов
            if len(cities) > 1:  # если городов больше 1
                if self.data['list'][0] != self.city.split(',')[0]:  # если город с базы не совпадает с нашим городом
                    self.city_id = self.data['list'][1]['id']  # взятие id этого города
                else:
                    self.city_id = self.data['list'][0]['id']  # взятие id этого города
            else:
                self.city_id = self.data['list'][0]['id']
        except Exception as exc:  # если исключение есть, то вывод ошибки
            print("Exception (find):", exc)  # вывод на экран параметра ошибки

    # Запрос текущей погоды
    def request_current_weather(self):
        try:
            self.result = req.get("http://api.openweathermap.org/data/2.5/weather",
                                       params={'id': self.city_id, 'units': 'metric', 'lang': 'ru',
                                               'APPID': self.APPID})
            self.data = self.result.json()
            self.final_list.append({"City": self.data['name'],
                                    "Date": datetime.today().date(),
                                    "Condition": self.data['weather'][0]['description'],
                                    "Temperature": self.data['main']['temp'],
                                    "Wind_speed": self.data['wind']['speed'],
                                    "Wind_direction": self.get_wind_direction(self.data['wind']['deg'])})
        except Exception as exc:
            print("Exception (weather):", exc)
        return self.final_list

    # Прогноз
    def request_forecast(self):
        try:
            self.result = req.get("http://api.openweathermap.org/data/2.5/forecast",
                                       params={'id': self.city_id, 'units': 'metric', 'lang': 'ru',
                                               'APPID': self.APPID})
            self.data = self.result.json()
            for i in self.data['list']:
                self.final_list.append({"City": self.data['city']['name'],
                                        "Date_time": i['dt_txt'][:16],
                                        "Condition": i['weather'][0]['description'],
                                        "Temperature": i['main']['temp'],
                                        "Wind_speed": i['wind']['speed'],
                                        "Direction_wind": self.get_wind_direction(i['wind']['deg'])})
        except Exception as exc:
            print("Exception (forecast):", exc)
        return self.final_list

    #  основной блок
    def run(self, inp):
        self.get_city_id()
        if inp == '1':
            return self.request_current_weather()
        elif inp == '2':
            return self.request_forecast()


# Класс для работы с YandexWeather
class GetYandex:

    def __init__(self, user_city, range_date):
        self.range_date = range_date
        self.city_url = f'https://yandex.ru/pogoda/{user_city}'
        self.html = req.get(self.city_url).text
        self.final_list = []
        self.all_date = None
        self.all_weather = None
        self.all_condition = None
        self.city = None

    def parsing(self):
        soup = bs.BeautifulSoup(self.html, 'html.parser')
        self.all_date = soup.find_all('time', {'class': 'time forecast-briefly__date'})
        self.all_weather = soup.find_all('div',
                                         {'class': 'temp forecast-briefly__temp forecast-briefly__temp_day'})
        self.all_condition = soup.find_all('div', {'class': 'forecast-briefly__condition'})
        self.city = soup.find_all('span', {'class': 'breadcrumbs__title'})

    def conversion_for_dict(self):
        if '-' in self.range_date:
            self.range_date = [str(k) for k in
                               range(int(self.range_date.split('-')[0]), int(self.range_date.split('-')[1]) + 1)]
        elif '-' not in self.range_date:
            self.range_date = [self.range_date]
        for i, day_for_site in enumerate(self.all_date):
            for day_for_range in self.range_date:
                if day_for_range == day_for_site.contents[0].split(' ')[0]:
                    self.final_list.append({'day_month': day_for_site.contents[0],
                                            'temperature': self.all_weather[i].contents[1].contents[0],
                                            'state': self.all_condition[i].contents[0],
                                            'city': self.city[2].contents[0]})
                else:
                    continue
        return self.final_list

    def run(self):
        self.parsing()
        return self.conversion_for_dict()
