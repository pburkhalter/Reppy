import logging
import websockets

from lib.job import PrintJob

# Configure logging
logger = logging.getLogger(__name__)


class WebSocketConsoleHandler:
    def __init__(self, queues, stop_event):
        self.queues = queues
        self.stopped = stop_event
        self.socket = None
        self.commands = {
            "print": self.print,
            "load": self.load,
            "status": self.status,
            "cache": self.files,
            "exit": self.exit,
            "reboot": self.reboot,
        }

    async def __call__(self, websocket, path):
        self.socket = websocket
        try:
            async for message in websocket:
                logger.debug(f"Received message: {message}")
                tokens = message.split()
                command = tokens[0]

                if command in self.commands:
                    try:
                        # Pass the arguments to the method
                        await self.commands[command](*tokens[1:])
                    except Exception as e:
                        logger.error(f"Error executing command '{command}': {e}")
                        await self.socket.send(f"Error executing command '{command}': {e}")
                else:
                    await self.socket.send(f"Unknown command '{command}'")

        except websockets.exceptions.ConnectionClosedError as e:
            logger.error(f"Connection closed unexpectedly: {e}")

        except Exception as e:
            logger.error(f"An unexpected error occurred: {e}")

    async def print(self, *args):
        # Implement your logic here
        pass

    async def load(self, *args):
        try:
            # Check if the 'file' argument is passed
            if args and args[0] == 'zip' and args[1]:
                job = PrintJob(args[1])
                self.queues['print'].put(job.serialize())
        except Exception as e:
            logger.error(f"Error in load command: {e}")

    async def status(self, *args):
        # Implement your logic here
        pass

    async def files(self, *args):
        try:
            # Implement your logic here
            pass
        except Exception as e:
            logger.error(f"Error in files command: {e}")

    async def exit(self, *args):
        # Implement your logic here
        pass

    async def reboot(self, *args):
        # Implement your logic here
        pass
