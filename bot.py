import requests
from pony.orm import db_session
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType
from vk_api import VkApi

from random import randint
import logging
import handlers
from models import UserState, Registration

try:
    import settings
except ImportError:
    exit('DO cp settings.py.default settings.py and set token!')

log = logging.getLogger('bot')


def configure_logging():
    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(logging.Formatter('%(levelname)s %(message)s'))
    stream_handler.setLevel(logging.INFO)
    log.addHandler(stream_handler)

    file_handler = logging.FileHandler('bot.log.txt')
    file_handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)s %(message)s', datefmt='%Y-%m-%d %H:%M'))
    file_handler.setLevel(logging.DEBUG)
    log.addHandler(file_handler)

    log.setLevel(logging.DEBUG)


class Bot:
    """
    Бот для оформления билетов.

    Echo bot для vk.com
    Use python 3.7
    """

    def __init__(self, group_id, token):
        """
        :param group_id: id из группы vk
        :param token: секретный токен
        """
        self.group_id = group_id
        self.token = token
        self.vk = VkApi(token=token)
        self.long_poller = VkBotLongPoll(self.vk, self.group_id)

        self.api = self.vk.get_api()

    def run(self):
        """Запуск бота."""
        for event in self.long_poller.listen():
            try:
                self.on_event(event)
            except Exception:
                log.exception('Ошибка в обработке события')

    def send_text(self, text_to_send, user_id):
        self.api.messages.send(message=text_to_send,
                               random_id=randint(0, 2 ** 20),
                               peer_id=user_id)

    def send_image(self, image, user_id):
        upload_url = self.api.photos.getMessagesUploadServer()['upload_url']
        upload_data = requests.post(url=upload_url,
                                    files={'photo': ('image.png', image, 'image/png')}).json()
        image_data = self.api.photos.saveMessagesPhoto(**upload_data)
        owner_id = image_data[0]['owner_id']
        media_id = image_data[0]['id']
        attachment = f'photo{owner_id}_{media_id}'

        self.api.messages.send(attachment=attachment,
                               random_id=randint(0, 2 ** 20),
                               peer_id=user_id)

    def send_step(self, step, context, user_id, state):
        if 'dispatcher' in step:
            dispatcher = getattr(handlers, step['dispatcher'])
            result = dispatcher(context=context)
            if result:
                self.send_text(result, user_id)
            else:
                text = 'К сожалению рейсов не нашлось.'
                self.send_text(text, user_id)
                return False
        if 'choice' in step:
            handler = getattr(handlers, step['choice'])
            answer = handler(context=context)
            if not answer:
                text = 'Регистрация завершена.'
                self.send_text(text, user_id)
                return False
        if 'text' in step:
            self.send_text(step['text'].format(**context), user_id)
        if 'image' in step:
            handler = getattr(handlers, step['image'])
            image = handler(context=context)
            self.send_image(image, user_id)

    @db_session
    def on_event(self, event):
        """
        Отправляет сообщение назад, если это текст
        :param event: VkBotMessageEvent object
        :return: None
        """
        if event.type != VkBotEventType.MESSAGE_NEW:
            return

        user_id = event.object.peer_id
        text = event.object.text

        state = UserState.get(user_id=str(user_id))
        if state is not None:
            self.continue_scenario(text, state, user_id)
        else:
            for intent in settings.INTENTS:
                log.debug(f'User gets {intent}')
                if any(token in text.lower() for token in intent['tokens']):
                    if intent['answer']:
                        self.send_text(intent['answer'], user_id)
                    else:
                        self.start_scenario(user_id, intent['scenario'], state)
                    break
            else:
                self.send_text(settings.DEFAULT_ANSWER, user_id)

    def start_scenario(self, user_id, scenario_name, state):
        scenario = settings.SCENARIOS[scenario_name]
        first_step = scenario['first_step']
        step = scenario['steps'][first_step]
        self.send_step(step=step, context={}, user_id=user_id, state=state)
        UserState(user_id=str(user_id), scenario_name=scenario_name, step_name=first_step, context={})

    def continue_scenario(self, text, state, user_id):
        steps = settings.SCENARIOS[state.scenario_name]['steps']
        step = steps[state.step_name]
        handler = getattr(handlers, step['handler'])
        if handler(text=text, context=state.context):
            next_step = steps[step['next_step']]
            if self.send_step(next_step, state.context, user_id, state) is False:
                state.delete()
            else:
                if next_step['next_step']:
                    state.step_name = step['next_step']
                else:
                    log.info(
                        'Зарегистрирован:\n{choice}\n{phone}'.format(**state.context))
                    Registration(name=state.context['name'],
                                 email=state.context['email'],
                                 phone_num=state.context['phone'],
                                 departure=state.context['city_departure'],
                                 arrive=state.context['city_arrive'],
                                 date=state.context['departure_date'],
                                 comment=state.context['comment'],
                                 passengers=state.context['passengers']
                                 )
                    state.delete()
        else:
            self.send_text(step['failure_text'], user_id)


if __name__ == '__main__':
    configure_logging()
    bot = Bot(settings.GROUP_ID, settings.TOKEN)
    bot.run()

