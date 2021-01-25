import random

import handlers
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


class UserState:
    """State user into scenario"""
    def __init__(self, scenario_name, step_name, context=None):
        self.scenario_name = scenario_name
        self.step_name = step_name
        self.context = context or {}


class Bot:
    """
    Script to registration on conference to vk.com
    Use python3.8

    Supported answers about date, place and registration
    - answer Name
    - answer email
    - tell about success registration
    If step not passed, answer clarifying question
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
        self.user_states = dict()  # user_id -> UserState

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
        if event.type != VkBotEventType.MESSAGE_NEW:
            log.info("This part isn't work %s", event.type)
            return

        user_id = event.object.message['peer_id']
        text = event.object.message['text']
        if user_id in self.user_states:
            text_to_send = self.continue_scenario(user_id=user_id, text=text)

        else:
            # search intent
            for intent in settings.INTENTS:
                log.debug(f'User gets {intent}')
                if any(token in text.lower() for token in intent['tokens']):
                    # run intent
                    if intent['answer']:
                        text_to_send = intent['answer']
                    else:
                        text_to_send = self.start_scenario(scenario_name=intent['scenario'], user_id=user_id)
                    break
                else:
                    text_to_send = settings.DEFAULT_ANSWER

        self.api.messages.send(message=text_to_send,
                               random_id=random.randint(0, 2 ** 20),
                               peer_id=user_id,
                               )

    def start_scenario(self, scenario_name, user_id):
        scenario = settings.SCENARIOS[scenario_name]
        first_step = scenario['first_step']
        step = scenario['steps'][first_step]
        text_to_send = step['text']
        self.user_states[user_id] = UserState(scenario_name=scenario_name, step_name=first_step)
        return text_to_send

    def continue_scenario(self, user_id, text):
        state = self.user_states[user_id]
        steps = settings.SCENARIOS[state.scenario_name]['steps']
        step = steps[state.step_name]

        handler = getattr(handlers, step['handler'])
        if handler(text=text, context=state.context):
            # next step
            next_step = steps[step['next_step']]
            text_to_send = next_step['text'].format(**state.context)
            if next_step['next_step']:
                # switch to next step
                state.step_name = step['next_step']
            else:
                # finish scenario
                self.user_states.pop(user_id)
                log.info('Registration {name}! Send email to {email}'.format(**state.context))
        else:
            # retry current step
            text_to_send = step['failure_text'].format(**state.context)
        return text_to_send

if __name__ == '__main__':
    configure_logging()
    bot = Bot(settings.GROUP_ID, settings.TOKEN)
    bot.run()
