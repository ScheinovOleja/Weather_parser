import peewee  # импорт библиотеки для работы с БД SQLite

database = peewee.SqliteDatabase("Weather.db")  # объявление базы данных


class Table(peewee.Model):  # объявление объекта таблицы
    class Meta:
        database = database


class DateOpenW(Table):  # объявление таблицы с названиями городов для связывания с основной таблицей
    city_name = peewee.CharField()


class WeatherInfoForecast(Table):  # объявление таблицы для прогноза
    city_name = peewee.ForeignKeyField(DateOpenW)
    date_time = peewee.CharField()
    temp = peewee.CharField()
    speed_wind = peewee.CharField()
    direction_wind = peewee.CharField()
    condition = peewee.CharField()


class WeatherInfoCurrent(Table):  # объявление таблицы для текущих данных
    city_name = peewee.ForeignKeyField(DateOpenW)
    date = peewee.CharField()
    temp = peewee.CharField()
    speed_wind = peewee.CharField()
    direction_wind = peewee.CharField()
    condition = peewee.CharField()


class DateYandex(Table):  # объявление таблицы с датами для связывания с основной таблицей
    day_month = peewee.CharField()


class YandexInfo(Table):  # объявление таблицы для данных с яндекса
    day_month = peewee.ForeignKeyField(DateYandex)
    city = peewee.CharField()
    temperature = peewee.CharField()
    state = peewee.CharField()


class DateYandex(Table):
    day_month = peewee.CharField()


class YandexInfo(Table):
    day_month_id = peewee.CharField()
    city = peewee.CharField()
    temperature = peewee.CharField()
    state = peewee.CharField()


database.create_tables([DateOpenW, WeatherInfoForecast, WeatherInfoCurrent, DateYandex, YandexInfo])  # непосредственное создание всех таблиц в БД


# класс для работы с бд для OWM
class TreatmentOWM:

    def __init__(self):
        self.days = []
        self.cities = []
        self.temperatures = []
        self.conditions = []
        self.speeds = []
        self.directions = []

    # получение списка данных из таблицы с текущими данными
    def getting_list_cur(self):
        for weather in WeatherInfoCurrent.select():
            self.days.append(weather.date)
            self.cities.append(weather.city_name_id)
            self.temperatures.append(weather.temp)
            self.conditions.append(weather.condition)
            self.speeds.append(weather.speed_wind)
            self.directions.append(weather.direction_wind)

    # получение списка данных из таблицы с прогнозом
    def getting_list_forecast(self):
        for weather in WeatherInfoForecast.select():
            self.days.append(weather.date_time)
            self.cities.append(weather.city_name_id)
            self.temperatures.append(weather.temp)
            self.conditions.append(weather.condition)
            self.speeds.append(weather.speed_wind)
            self.directions.append(weather.direction_wind)

    # занесение данных в таблицу текущих данных
    def run_cur(self, data_list):
        self.getting_list_cur()
        for i in range(len(data_list)):
            if not (data_list[i][
                        'Date'] in self.days and data_list[i][
                        'City'] in self.cities and data_list[i][
                        'Temperature'] in self.temperatures and data_list[i][
                        'Condition'] in self.conditions and data_list[i][
                        'Wind_speed'] in self.speeds and data_list[i][
                        'Wind_direction'] in self.directions):
                base = WeatherInfoCurrent(
                    date=data_list[i]['Date'],
                    city_name_id=data_list[i]['City'],
                    temp=data_list[i]['Temperature'],
                    condition=data_list[i]['Condition'],
                    speed_wind=data_list[i]['Wind_speed'],
                    direction_wind=data_list[i]['Wind_direction']
                )
                base.save()

    # занесение данных в таблицу прогноза
    def run_forecast(self, data_list):
        self.getting_list_forecast()
        for i in range(len(data_list)):
            if not (data_list[i][
                        'Date_time'] in self.days and data_list[i][
                        'City'] in self.cities and data_list[i][
                        'Temperature'] in self.temperatures and data_list[i][
                        'Condition'] in self.conditions and data_list[i][
                        'Wind_speed'] in self.speeds and data_list[i][
                        'Direction_wind'] in self.directions):
                base = WeatherInfoForecast(
                    date_time=data_list[i]['Date_time'],
                    city_name_id=data_list[i]['City'],
                    temp=data_list[i]['Temperature'],
                    condition=data_list[i]['Condition'],
                    speed_wind=data_list[i]['Wind_speed'],
                    direction_wind=data_list[i]['Direction_wind']
                )
                base.save()

    # вывод данных текущих по выбранному городу
    def print_cur(self, city):
        for weather_cur in WeatherInfoCurrent.select():
            if weather_cur.city_name_id.lower() == city.lower():
                print(f"Дата: {weather_cur.date}\n"
                      f"Город: {weather_cur.city_name_id}\n"
                      f"Температура: {weather_cur.temp} °C\n"
                      f"Состояние погоды: {weather_cur.condition}\n"
                      f"Скорость ветра: {weather_cur.speed_wind}\n"
                      f"Направление ветра: {weather_cur.direction_wind}\n")

    # вывод данных прогноза по выбранному городу
    def print_forecast(self, city):
        for weather_forecast in WeatherInfoForecast.select():
            if weather_forecast.city_name_id.lower() == city.lower():
                print(f"Дата и время: {weather_forecast.date_time}\n"
                      f"Город: {weather_forecast.city_name_id}\n"
                      f"Температура: {weather_forecast.temp} °C\n"
                      f"Состояние погоды: {weather_forecast.condition}\n"
                      f"Скорость ветра: {weather_forecast.speed_wind}\n"
                      f"Направление ветра: {weather_forecast.direction_wind}\n")


# класс для работы с бд для Yandex
class TreatmentYandex:

    def __init__(self, city, date_range):
        self.date_range = date_range
        self.city = city
        self.days = []
        self.cities = []
        self.temperatures = []
        self.states = []
        self.min_date = 0
        self.max_date = 0

    def wide_range(self):
        if '-' in self.date_range:
            range_date = [k for k in range(int(self.date_range.split('-')[0]), int(self.date_range.split('-')[1]) + 1)]
            self.min_date, self.max_date = range_date[0], range_date[-1]
        elif '-' not in self.date_range:
            range_date = [int(self.date_range)]
            self.min_date, self.max_date = range_date[0], range_date[-1]
        else:
            raise ValueError('Произошла ошибка')

    @staticmethod
    def print_all_cities():
        prev_city = ''
        for weather in YandexInfo.select():
            if prev_city != weather.city:
                print(f'Город: {weather.city}\n')
                prev_city = weather.city
            else:
                continue

    def print_data(self):
        self.wide_range()
        for weather in YandexInfo.select().where(
                (YandexInfo.day_month_id >= self.min_date) & (YandexInfo.day_month_id < self.max_date + 1)):
            if self.city.lower() in weather.city.lower():
                print(f'День: {weather.day_month_id}\n',
                      f'Температура: {weather.temperature}\n',
                      f'Состояние: {weather.state}\n',
                      f'Город: {weather.city}\n')

    def getting_list(self):
        for weather in YandexInfo.select():
            self.days.append(weather.day_month_id)
            self.cities.append(weather.city)
            self.temperatures.append(weather.temperature)
            self.states.append(weather.state)

    def get_weather(self, city):
        weather_list = []
        self.wide_range()
        for weather in YandexInfo.select().where(
                (YandexInfo.day_month_id >= self.min_date) & (YandexInfo.day_month_id < self.max_date + 1)):
            if city in weather.city.lower():
                weather_list.append({'day_month': weather.day_month_id,
                                     'temperature': weather.temperature,
                                     'state': weather.state,
                                     'city': weather.city})
        return weather_list

    def run(self, data_list):
        self.getting_list()
        str_upd_id = []
        str_create_id = []
        for index, element in enumerate(data_list):
            row = YandexInfo.get_or_create(
                day_month_id=element['day_month'],
                city=self.city,
                defaults={
                    'day_month_id': element['day_month'],
                    'city': self.city,
                    'temperature': element['temperature'],
                    'state': element['state']
                }
            )
            if row[1] is False:
                YandexInfo.update(state=element['state'], temperature=element['temperature']).where(
                    YandexInfo.id == row[0].id).execute()
                str_upd_id.append(row[0].id)
            elif row[1] is True:
                str_create_id.append(row[0].id)
        print(f'В строках {str_upd_id} данные обновлены!\nВ строках {str_create_id} данные добавлены!')
        days = []
        for weather in DateYandex.select():
            days.append(weather.day_month)
        for index, element in enumerate(data_list):
            day = element['day_month']
            if day not in days:
                artist = DateYandex.create(day_month=day)
                artist.save()
            else:
                continue
