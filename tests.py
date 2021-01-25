from copy import deepcopy
from unittest import TestCase
from unittest.mock import patch, Mock, ANY

from vk_api.bot_longpoll import VkBotMessageEvent

import settings
from bot import Bot


class Test1(TestCase):
    RAW_EVENT = {
        'type': 'message_new',
        'object': {
            'message': {
                'date': 1611433190, 'from_id': 635421073, 'id': 84,
                'out': 0, 'peer_id': 635421073, 'text': 'Hello Bot',
                'conversation_message_id': 84, 'fwd_messages': [],
                'important': False, 'random_id': 0, 'attachments': [],
                'is_hidden': False
            },
            'client_info': {
                'button_actions': [
                    'text', 'vkpay', 'open_app', 'location', 'open_link',
                    'intent_subscribe', 'intent_unsubscribe'
                ],
                'keyboard': True, 'inline_keyboard': True,
                'carousel': False, 'lang_id': 0
            }
        },
        'group_id': 202004037, 'event_id': 'ccb3124150a869267eb06decb907820cfa88e1fe'
    }

    def test_run(self):
        count = 5
        obj = {}
        events = [obj] * count  # [obj, obj ...]
        long_poller_mock = Mock(return_value=events)
        long_poller_listen_mock = Mock()
        long_poller_listen_mock.listen = long_poller_mock
        with patch("bot.vk_api.VkApi"):
            with patch("bot.VkBotLongPoll", return_value=long_poller_listen_mock):
                bot = Bot("", "")
                bot.on_event = Mock()

                bot.run()

                bot.on_event.assert_called()
                bot.on_event.assert_any_call(obj)
                assert bot.on_event.call_count == count

    INPUTS = [
        "Привет",
        "А когда?",
        "Где будет конференция?",
        "Зарегистрируй меня",
        "Вениамин Эдуардович",
        "мой адрес cherviak@true",
        "cherviak@true.fru",
    ]
    EXPECTED_OUTPUTS = [
        settings.DEFAULT_ANSWER,
        settings.INTENTS[0]['answer'],
        settings.INTENTS[1]['answer'],
        settings.SCENARIOS['registration']['steps']['step1']['text'],
        settings.SCENARIOS['registration']['steps']['step2']['text'],
        settings.SCENARIOS['registration']['steps']['step2']['failure_text'],
        settings.SCENARIOS['registration']['steps']['step3']['text'].format(name="Вениамин Эдуардович", email="cherviak@true.fru")
    ]
    def test_run_ok(self):
        send_mock = Mock()
        api_mock = Mock()
        api_mock.messages.send = send_mock

        events = []
        for input_text in self.INPUTS:
            event = deepcopy(self.RAW_EVENT)
            event['object']['message']['text'] = input_text
            events.append(VkBotMessageEvent(event))
        long_poller_mock = Mock()
        long_poller_mock.listen = Mock(return_value=events)

        with patch('bot.VkBotLongPoll', return_value=long_poller_mock):
            bot = Bot('', '')
            bot.api = api_mock
            bot.run()

        assert send_mock.call_count == len(self.INPUTS)

        real_outputs = []
        for call in send_mock.call_args_list:
            args, kwargs = call
            real_outputs.append(kwargs['message'])
        assert real_outputs == self.EXPECTED_OUTPUTS
