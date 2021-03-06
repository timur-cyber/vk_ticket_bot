
INTENTS = [
    {
        'name': 'Помощь',
        'tokens': ('привет', '/help', 'помоги', 'помощь'),
        'scenario': None,
        'answer': 'Привет!\nЯ бот для оформления билетов.\n'
                  'Для того чтобы начать оформление билетов напишите /ticket'
    },
    {
        'name': 'Регистрация билетов',
        'tokens': ('/ticket', 'зарегистр', 'билет', 'дату'),
        'scenario': 'registration',
        'answer': None
    }
]

CITIES = [
    'Москва',
    'Париж',
    'Лондон',
    'Берлин',
    'Рим',
    'Мадрид'
]
SCENARIOS = {
    'registration': {
        'first_step': 'step1',
        'steps': {
            'step1': {
                'text': 'Чтобы зарегистрироваться, введите город отправления',
                'failure_text': 'Города нет в списке рейсов. Вот доступные города:\n'
                                'Москва, Париж, Лондон, Берлин, Рим, Мадрид',
                'handler': 'handler_city_departure',
                'next_step': 'step2'
            },
            'step2': {
                'text': 'Отлично город отправления - {city_departure}. Теперь введите город назначения',
                'failure_text': 'Города нет в списке рейсов. Вот доступные города:\n'
                                'Москва, Париж, Лондон, Берлин, Рим, Мадрид',
                'handler': 'handler_city_arrive',
                'next_step': 'step3'
            },
            'step3': {
                'text': 'Теперь введите приблизительную дату отправления',
                'failure_text': 'Введён некорректный формат даты. '
                                'Пожалуйста введите корректный формат. (ДД-ММ-ГГ)\n'
                                'Также учтите, что оформление билетов осуществляется только '
                                'на будущие даты. На прошедшие даты купить нельзя.',
                'handler': 'handler_date',
                'next_step': 'step4'
            },
            'step4': {
                'text': 'Теперь выберите из списка рейсов',
                'failure_text': 'Вы ввели недопустимый вариант. Повторите свой выбор',
                'handler': 'handler_choice',
                'dispatcher': 'flights_dispatcher',
                'next_step': 'step5'
            },
            'step5': {
                'text': 'Уточните кол-во мест (от 1 до 5)',
                'failure_text': 'Недопустимое число мест. Повторите попытку',
                'handler': 'handler_passengers',
                'next_step': 'step6'
            },
            'step6': {
                'text': 'Напишите комментарий к заказу',
                'failure_text': 'Что-то пошло не так. Попробуйте снова...',
                'handler': 'handler_comment',
                'next_step': 'step7'
            },
            'step7': {
                'text': 'Уточните свой выбор:\n'
                        '{choice}\n'
                        'Кол-во мест: {passengers}\n'
                        'Потвердите (Да/Нет)',
                'failure_text': 'Некорректный ответ. Введите да/нет',
                'handler': 'handler_accept',
                'next_step': 'step8'
            },
            'step8': {
                'text': 'Введите номер телефона',
                'failure_text': 'Неверный формат телефона. '
                                'Пожалуйста введите корректный формат. (+7...номер телефона)',
                'handler': 'handler_phone',
                'choice': 'choice',
                'next_step': 'step9'
            },
            'step9': {
                'text': 'Введите свое имя',
                'failure_text': 'Некорректное имя. Попробуйте снова.',
                'handler': 'handler_name',
                'next_step': 'step10'
            },
            'step10': {
                'text': 'Введите электронную почту',
                'failure_text': 'Некорректный формат почты. Попробуйте снова.',
                'handler': 'handler_email',
                'next_step': 'step11'
            },
            'step11': {
                'text': 'Спасибо за регистрацию. Ваш билет ниже.\n'
                        'Копию мы отправили на email\n'
                        '{email}\n'
                        'Не забудьте его распечатать.',
                'image': 'ticket_generator',
                'failure_text': None,
                'handler': None,
                'next_step': None
            }
        }
    }
}

DEFAULT_ANSWER = 'Не знаю как ответить.\n' \
                 'Могу оформить вам билет по команде /ticket.'

DB_CONFIG = dict(
    provider='postgres',
    user='postgres',
    password='postgres',
    host='localhost',
    database='vk_chat_bot'
)
