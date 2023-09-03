import asyncio
import logging
import websockets
from api.ws.handler import WebSocketConsoleHandler
from settings import settings_dict


# Setup logging
logger = logging.getLogger(__name__)


class WebSocketController:
    # Handles WebSocket setup and events
    def __init__(self, queues, stop_event):
        # Create new event loop
        self.eventloop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.eventloop)

        # Get port and bind settings
        self.port = settings_dict['system']['wsc']['port']
        self.bind = settings_dict['system']['wsc']['bind']

        # Initialize message handler
        self.handler = WebSocketConsoleHandler(queues, stop_event)

        # Setup server
        self.server = websockets.serve(self.handler, self.bind, self.port)
        
        # Run the server
        self.run()

    def run(self):
        # Start the server
        self.eventloop.run_until_complete(self.server)
        self.eventloop.run_forever()
