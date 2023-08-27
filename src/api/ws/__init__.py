import asyncio
import logging
import websockets

from api.ws.handler import WebSocketConsoleHandler
from settings import settings_dict


# Configure logging
logger = logging.getLogger(__name__)


class WebSocketController:

    def __init__(self, queues, stop_event):
        self.eventloop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.eventloop)

        self.port = settings_dict['system']['wsc']['port']
        self.bind = settings_dict['system']['wsc']['bind']

        self.handler = WebSocketConsoleHandler(queues, stop_event)
        self.server = websockets.serve(self.handler, self.bind, self.port)
        self.run()

    def run(self):
        self.eventloop.run_until_complete(self.server)
        self.eventloop.run_forever()
