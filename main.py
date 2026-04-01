import datetime as dt

# Ревью в двух словах: база хорошая, потенциал отличный.
# - Отлично разложены роли: есть Record, базовый Calculator и наследники.
# - Общая логика вынесена в родителя, а специфичная - в дочерние классы.
# - Что подтянуть: docstring'и и type annotations почти отсутствуют.
#       Почему это важно: код быстрее читается командой и проще проверяется линтерами.
# - Ниже оставил точечные комментарии: где именно и почему стоит поправить.


class Record:

    # С date='' решение в целом рабочее, но хрупое. Лучше использовать date=None.
    # Так не смешиваются типы, и обработка параметра становится
    # предсказуемой (строка всегда строка, "нет значения" - всегда None).
    def __init__(self, amount, comment, date=''):

        self.amount = amount
        # Условие разбито так, что читать его тяжеловато. Лучше сделать его более линейным.
        # Почему стоит упростить: чем проще конструкция, тем меньше времени на
        # разбор и меньше шансов ошибиться при доработках.

        self.date = (
            dt.datetime.now().date() if
            not
            date else dt.datetime.strptime(date, '%d.%m.%Y').date())
        
        # Переменным лучше держаться вместе, так им комфортнее, а нам - лучше ориентироваться в коде.
        # Можно переселить её выше к self.amount, чтобы она не затерялась среди логики с датой.
        self.comment = comment


class Calculator:
    def __init__(self, limit):
        self.limit = limit
        self.records = []

    def add_record(self, record):
        self.records.append(record)

    def get_today_stats(self):
        today_stats = 0
        # Переменная цикла Record перекрывает имя класса
        # и выбивается из snake_case.
        # Такие имена путают и мешают навигации по
        # коду (особенно в IDE).
        for Record in self.records:
            # dt.datetime.now().date() вызывается на каждой итерации.
            # Вряд-ли текущий цикл будет идти несколько дней, 
            # поэтому можно получить "сегодня" единожды - вынести получение 
            # сегодняшней даты в переменную до цикла.
            # Так будет меньше лишних вызовов и чище логика.
            if Record.date == dt.datetime.now().date():
                today_stats = today_stats + Record.amount
                
        return today_stats

    def get_week_stats(self):
        week_stats = 0
        today = dt.datetime.now().date()
        for record in self.records:
            # Расчёт разницы дней лучше сделать в отдельной переменной.
            # Сложночитаемое условие, тут можно сократить до 0 <= (today - record.date).days < 7.
            if (
                (today - record.date).days < 7 and
                (today - record.date).days >= 0
            ):
                week_stats += record.amount
        return week_stats


class CaloriesCalculator(Calculator):
    # Тут просится docstring вместо inline-комментария.
    # Почему это важно: docstring подхватят IDE/документация, а inline - нет.
    def get_calories_remained(self):  # Получает остаток калорий на сегодня
        # x - имя-загадка. Более подходящее тут calories_left - смысл считывается сразу.
        x = self.limit - self.get_today_stats()
        if x > 0:
            # Используется `\` для переноса строки, лучше скобки если хочешь разбить по строкам.
            # Так меньше хрупкости форматирования и проще
            # править длинные строки.
            return f'Сегодня можно съесть что-нибудь' \
                   f' ещё, но с общей калорийностью не более {x} кКал'
        else:
            # Если по условию return выше не сработает, без else код сработает так же,
            # как и без него. Он тут необязателен.
            
            # Скобки вокруг строки в return - лишний синтаксический груз. Можно просто вернуть строку.
            # Так будет проще и чище, без лишних символов.
            return('Хватит есть!')


class CashCalculator(Calculator):
    # float(60) и float(70) можно упростить до 60.0 и 70.0.
    # Будет меньше лишних действий и яснее намерение.
    # P.S. Курс очень хороший! :) 
    USD_RATE = float(60)  # Курс доллар США.
    EURO_RATE = float(70)  # Курс Евро.


    # Параметры по умолчанию `USD_RATE=USD_RATE` и `EURO_RATE=EURO_RATE`
    # дублируют атрибуты класса, т.е. к ним можно обратиться через self
    # без передачи в метод. Интерфейс метода станет проще, и
    # поддерживать такой код будет легче.
    def get_today_cash_remained(self, currency,
                                USD_RATE=USD_RATE, EURO_RATE=EURO_RATE):
        currency_type = currency
        cash_remained = self.limit - self.get_today_stats()
        # Для неподдерживаемой валюты нет явной ветки. При неверном коде валюты пользователь получит
        # странный ответ вместо понятной ошибки/сообщения.

        # Ветвление по валюте можно упростить, например, через словарь с курсами и названиями валют. 
        # Это сделает код более компактным и удобным для расширения (добавления новых валют).

        if currency == "usd":
            cash_remained /= USD_RATE
            currency_type = "USD"
        elif currency_type == "eur":
            cash_remained /= EURO_RATE
            currency_type = "Euro"
        elif currency_type == "rub":
            # Тут, похоже, опечатка:`== вместо нужного действия.
            cash_remained == 1.00
            currency_type = "руб"
        if cash_remained > 0:
            # В f-строке вызывается round(...).
            # В f-строку лучше подставлять уже готовые значения, без вычислений внутри.
            # Так строка будет чище, а вычисления - проще и понятнее.
            return (
                f'На сегодня осталось {round(cash_remained, 2)} '
                f'{currency_type}'
            )
        elif cash_remained == 0:
            return "Денег нет, держись"
        elif cash_remained < 0:
            # Снова используется `\` для переноса, и внутри форматирования
            # есть вычисление - сильно перегружена. Лучше использовать f-строку,
            # а вычисления вынести в отдельную переменную.
            return 'Денег нет, держись:' \
                   ' твой долг - {0:.2f} {1}'.format(-cash_remained,
                                                     currency_type)

    def get_week_stats(self):
        # Тут затаился баг: метод вызывает super(), но не возвращает
        # результат. Снаружи придёт None, и недельная статистика
        # "испарится", хотя данные в списке есть.
        super().get_week_stats()
