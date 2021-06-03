import calendar
import datetime
import re

from generate_ticket import generate_ticket
from settings import CITIES
import json

re_date = re.compile(r'^[\d]{1,2}-[\d]{1,2}-[\d]{4}$')
re_phone = re.compile(r'[+]\d+')
re_name = re.compile(r'^[\w\-\s]{3,40}$')
re_email = re.compile(r'^[a-z0-9]+[_]?[a-z0-9]+[@]\w+[.]\w{2,3}$')


def handler_name(text, context):
    text = text.capitalize()
    if text.isalpha():
        match = re.match(re_name, text)
        if match:
            context['name'] = text
            return True
        else:
            return False
    else:
        return False


def handler_email(text, context):
    match = re.match(re_email, text)
    if match:
        context['email'] = text
        return True
    else:
        return False


def handler_city_departure(text, context):
    text = text.capitalize()
    if text.isalpha():
        if text in CITIES:
            context['city_departure'] = text
            return True
        else:
            return False
    else:
        return False


def handler_city_arrive(text, context):
    text = text.capitalize()
    if text.isalpha():
        if text in CITIES:
            context['city_arrive'] = text
            return True
        else:
            return False
    else:
        return False


def handler_date(text, context):
    matched = re.findall(re_date, text)
    if matched:
        wrapped = text.split('-')
        if int(wrapped[0]) > 31 or int(wrapped[0]) <= 0 or int(wrapped[1]) <= 0 or int(wrapped[1]) > 12:
            return False
        else:
            date_obj = datetime.datetime.strptime(matched[0], '%d-%m-%Y')
            date_obj_now = datetime.datetime.now()
            if date_obj < date_obj_now:
                return False
            else:
                context['date'] = matched[0]
                return True
    else:
        return False


def handler_passengers(text, context):
    if text.isdigit():
        if 0 < int(text) <= 5:
            context['passengers'] = text
            return True
        else:
            return False
    else:
        return False


def handler_choice(text, context):
    if text.isdigit():
        if 0 < int(text) <= len(context['flight_list']):
            context['choice'] = context['flight_list'][int(text) - 1]
            context['departure_date'] = context['flight_dates'][int(text) - 1]
            return True
        else:
            return False
    else:
        return False


def handler_comment(text, context):
    if type(text) is str:
        context['comment'] = text
        return True
    else:
        return False


def handler_accept(text, context):
    if text.lower() == 'да':
        context['confirm'] = text.lower()
        return True
    elif text.lower() == 'нет':
        context['confirm'] = text.lower()
        return True
    else:
        return False


def handler_phone(text, context):
    match = re.match(re_phone, text)
    if match:
        context['phone'] = text
        return True
    else:
        return False


def choice(context):
    answer = context['confirm']
    if answer == 'да':
        return True
    else:
        return False


def ticket_generator(context):
    name = context['name']
    email = context['email']
    departure = context['city_departure']
    arrive = context['city_arrive']
    date = context['departure_date']
    return generate_ticket(name=name, email=email, departure=departure, arrive=arrive, date=date)


def get_from_calendar(departure_city, arrive_city, date_obj, week, time, flight_list, flight_dates):
    calendar_text = calendar.Calendar()
    i = 0
    for year, month, day, week_day in calendar_text.itermonthdays4(date_obj.year, date_obj.month):
        if year == date_obj.year and month == date_obj.month:
            if month != date_obj.month + 1:
                if week_day == int(week):
                    date = f'{day}-{month}-{year} {time}'
                    date_obj_new = datetime.datetime.strptime(date, '%d-%m-%Y %H:%M')
                    if date_obj_new < date_obj:
                        pass
                    else:
                        i += 1
                        flight_dates.append(date)
                        flight_list.append(
                            f'{departure_city.upper()} --> {arrive_city.upper()}\nДата: {date}')
    if i < 5:
        next_month = date_obj.month + 1 if date_obj.month != 12 else 1
        next_year = date_obj.year if date_obj.month != 12 else date_obj.year + 1
        for year, month, day, week_day in calendar_text.itermonthdays4(next_year, next_month):
            if year == next_year and month == next_month:
                if i >= 5:
                    break
                if week_day == int(week):
                    date = f'{day}-{month}-{year} {time}'
                    date_obj_new = datetime.datetime.strptime(date, '%d-%m-%Y %H:%M')
                    if date_obj_new < date_obj:
                        pass
                    else:
                        i += 1
                        flight_dates.append(date)
                        flight_list.append(
                            f'{departure_city.upper()} --> {arrive_city.upper()}\nДата: {date}')


def flights_dispatcher(context):
    file = 'flights.json'
    with open(file, 'r', encoding='utf8') as read_file:
        json_data = json.load(read_file)
    departure = context['city_departure']
    arrive = context['city_arrive']
    date = context['date']
    date_obj = datetime.datetime.strptime(date, '%d-%m-%Y')
    flight_dates = []
    flight_list = []
    for departure_city, inner_dict in json_data.items():
        if departure_city == departure:
            for arrive_city, info in inner_dict.items():
                if arrive == arrive_city:
                    week = info['week_day']
                    time = info['time']
                    get_from_calendar(
                        departure_city, arrive_city, date_obj, week, time, flight_list,
                        flight_dates)

    context['flight_dates'] = flight_dates
    context['flight_list'] = flight_list

    text_to_send = ''
    for i, element in enumerate(flight_list):
        line = f'[{i + 1}] {element}'
        if i < len(flight_list) - 1:
            line += '\n'
        text_to_send += line

    return text_to_send
