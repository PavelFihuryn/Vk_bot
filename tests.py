from unittest import TestCase
from unittest.mock import patch, Mock, ANY

from vk_api.bot_longpoll import VkBotMessageEvent

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

    def test_on_event(self):
        event = VkBotMessageEvent(raw=self.RAW_EVENT)

        send_mock = Mock()

        with patch("bot.vk_api.VkApi"):
            with patch("bot.VkBotLongPoll"):
                bot = Bot("", "")
                bot.api = Mock()
                bot.api.messages.send = send_mock

                bot.on_event(event)

        send_mock.assert_called_once_with(
            message=self.RAW_EVENT['object']['message']['text'],
            random_id=ANY,
            peer_id=self.RAW_EVENT['object']['message']['peer_id'],)
