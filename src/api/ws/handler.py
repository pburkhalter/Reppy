import logging
import websockets


# Setup logging
logger = logging.getLogger(__name__)


class WebSocketConsoleHandler:
    # Initialize WebSocket handler
    def __init__(self, queues, stop_event):
        self.queues = queues
        self.stopped = stop_event
        self.socket = None

    async def __call__(self, websocket, path):
        self.socket = websocket
        
        try:
            # Process incoming messages
            async for message in websocket:
                logger.debug(f"Received message: {message}")
                tokens = message.split()
                command = tokens[0]

                arguments = {}
                for i in range(1, len(tokens), 2):  # Assuming key-value pairs
                    if i + 1 < len(tokens):
                        arguments[tokens[i]] = tokens[i + 1]

                # Execute corresponding command
                await self.queues['cmd'].put([command, arguments])

        # Handle connection errors
        except websockets.ConnectionClosedError as e:
            logger.error(f"Connection closed unexpectedly: {e}")
        
        except Exception as e:
            logger.error(f"An unexpected error occurred: {e}")
