import datetime
import os
import unittest
from copy import deepcopy
from unittest import TestCase
from unittest.mock import patch, Mock
from handlers import flights_dispatcher
from pony.orm import db_session, rollback

from generate_ticket import generate_ticket
from vk_api.bot_longpoll import VkBotMessageEvent

from bot import Bot

import settings


def isolate_db(test_func):
    def wrapper(*args, **kwargs):
        with db_session():
            test_func(*args, **kwargs)
            rollback()

    return wrapper


class Test1(TestCase):
    RAW_EVENT = {'type': 'message_new', 'object':
        {'date': 1606149305, 'from_id': 343189612, 'id': 52, 'out': 0, 'peer_id': 343189612,
         'text': 'Привет бот!', 'conversation_message_id': 52, 'fwd_messages': [],
         'important': False, 'random_id': 0, 'attachments': [], 'is_hidden': False},
                 'group_id': 200364100, 'event_id': 'f0a4b696b25611e5bab8b8627ccc4565604f5456'}

    def test_run(self):
        count = 5
        obj = {'a': 1}
        events = [obj] * count
        long_poller_mock = Mock(return_value=events)
        long_poller_listen_mock = Mock()
        long_poller_listen_mock.listen = long_poller_mock
        with patch('bot.VkApi'):
            with patch('bot.VkBotLongPoll', return_value=long_poller_listen_mock):
                bot = Bot('', '')
                bot.on_event = Mock()
                bot.send_image = Mock()
                bot.run()

                bot.on_event.assert_called()
                bot.on_event.assert_any_call(obj)
                assert bot.on_event.call_count == 5

    city_departure = 'Москва'
    city_arrive = 'Париж'
    email = 'random_email@email.com'
    date_now = datetime.datetime.now() + datetime.timedelta(days=1)
    date_now_str = f'{date_now.day}-{date_now.month}-{date_now.year}'
    fake_context = dict(
        date=date_now_str,
        city_departure=city_departure,
        city_arrive=city_arrive,
        email=email,
        passengers='1',
        choice_int='3')
    dispatcher_func_result = flights_dispatcher(fake_context)
    fake_context.update(
        choice=fake_context['flight_list'][int(fake_context['choice_int']) - 1])
    INPUTS = [
        'Курс рубля',
        'Привет',
        '/help',
        '/ticket',
        fake_context['city_departure'],
        'Нижний Новгород',
        fake_context['city_arrive'],
        '12.12.2020',
        '12-12-2020',
        fake_context['date'],
        fake_context['choice_int'],
        fake_context['passengers'],
        'Любой комментарий',
        'да',
        '48797329',
        '+94734543875',
        'Олег',
        fake_context['email']
    ]

    EXPECTED_OUTPUTS = [
        settings.DEFAULT_ANSWER,
        settings.INTENTS[0]['answer'].format(**fake_context),
        settings.INTENTS[0]['answer'].format(**fake_context),
        settings.SCENARIOS['registration']['steps']['step1']['text'].format(**fake_context),
        settings.SCENARIOS['registration']['steps']['step2']['text'].format(**fake_context),
        settings.SCENARIOS['registration']['steps']['step2']['failure_text'].format(**fake_context),
        settings.SCENARIOS['registration']['steps']['step3']['text'].format(**fake_context),
        settings.SCENARIOS['registration']['steps']['step3']['failure_text'].format(**fake_context),
        settings.SCENARIOS['registration']['steps']['step3']['failure_text'].format(**fake_context),
        dispatcher_func_result,
        settings.SCENARIOS['registration']['steps']['step4']['text'].format(**fake_context),
        settings.SCENARIOS['registration']['steps']['step5']['text'].format(**fake_context),
        settings.SCENARIOS['registration']['steps']['step6']['text'].format(**fake_context),
        settings.SCENARIOS['registration']['steps']['step7']['text'].format(**fake_context),
        settings.SCENARIOS['registration']['steps']['step8']['text'].format(**fake_context),
        settings.SCENARIOS['registration']['steps']['step8']['failure_text'].format(**fake_context),
        settings.SCENARIOS['registration']['steps']['step9']['text'].format(**fake_context),
        settings.SCENARIOS['registration']['steps']['step10']['text'].format(**fake_context),
        settings.SCENARIOS['registration']['steps']['step11']['text'].format(**fake_context),
    ]

    @isolate_db
    def test_run_ok(self):
        send_mock = Mock()
        api_mock = Mock()
        api_mock.messages.send = send_mock

        events = []
        for input_text in self.INPUTS:
            event = deepcopy(self.RAW_EVENT)
            event['object']['text'] = input_text
            events.append(VkBotMessageEvent(event))

        long_poller_mock = Mock()
        long_poller_mock.listen = Mock(return_value=events)

        with patch('bot.VkBotLongPoll', return_value=long_poller_mock):
            bot = Bot('', '')
            bot.api = api_mock
            bot.send_image = Mock()
            bot.run()

        real_outputs = []
        for call in send_mock.call_args_list:
            args, kwargs = call
            real_outputs.append(kwargs['message'])

        assert send_mock.call_count == len(self.EXPECTED_OUTPUTS)
        assert real_outputs == self.EXPECTED_OUTPUTS

    def test_image_generation(self):
        ticket_file = generate_ticket('Виталий', 'random_email@email.com', 'Москва', 'Париж', '12-12-2020 10:00',
                                      random_avatars=False)

        with open(os.path.normpath('files/ticket_example.png'), 'rb') as expected_file:
            expected_bytes = expected_file.read()
        assert ticket_file.read() == expected_bytes


if __name__ == '__main__':
    unittest.main()
