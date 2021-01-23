import random
import vk_api
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType
import logging
try:
    import settings
except ImportError:
    exit("Do cp settings.py.default settings.py and set token!")


log = logging.getLogger('bot')


def configure_logging():
    stream_handler = logging.StreamHandler()
    stream_handler.setLevel(logging.DEBUG)
    stream_handler.setFormatter(logging.Formatter("%(levelname)s %(message)s"))
    log.addHandler(stream_handler)

    file_handler = logging.FileHandler('bot.log')
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(message)s", datefmt="%d-%m-%Y %H:%M"))
    log.addHandler(file_handler)

    log.setLevel(logging.DEBUG)


class Bot:
    """
    Echo bot to vk.com
    Use python3.8
    """

    def __init__(self, group_id, token):
        """
        :param group_id: group id from group in vk
        :param token: secret token
        """
        self.group_id = group_id
        self.token = token

        self.vk = vk_api.VkApi(token=token)
        self.vk_long_poller = VkBotLongPoll(self.vk, self.group_id)

        self.api = self.vk.get_api()

    def run(self):
        """
        Run bot
        """
        for event in self.vk_long_poller.listen():
            try:
                self.on_event(event)
            except Exception:
                log.exception('Error processing event')

    def on_event(self, event):
        """
        Receive message back if the message is text
        :param event: VkBotMessageEvent object
        :return: None
        """
        if event.type == VkBotEventType.MESSAGE_NEW:
            # print(event.object.message['text'])
            log.debug("Receive message back")
            self.api.messages.send(message=event.object.message['text'],
                                   random_id=random.randint(0, 2**20),
                                   peer_id=event.object.message['peer_id'],
                                   )
        else:
            log.info("This part isn't work %s", event.type)


if __name__ == '__main__':
    configure_logging()
    bot = Bot(settings.GROUP_ID, settings.TOKEN)
    bot.run()
