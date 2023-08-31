import logging
import websockets
from lib.job import PrintJob

# Setup logging
logger = logging.getLogger(__name__)

class WebSocketConsoleHandler:
    # Initialize WebSocket handler
    def __init__(self, queues, stop_event):
        self.queues = queues
        self.stopped = stop_event
        self.socket = None
        
        # Define supported commands
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
            # Process incoming messages
            async for message in websocket:
                logger.debug(f"Received message: {message}")
                tokens = message.split()
                command = tokens[0]
                
                # Execute corresponding command
                if command in self.commands:
                    try:
                        await self.commands[command](*tokens[1:])
                    except Exception as e:
                        logger.error(f"Error executing command '{command}': {e}")
                        await self.socket.send(f"Error executing command '{command}': {e}")
                else:
                    await self.socket.send(f"Unknown command '{command}'")
        
        # Handle connection errors
        except websockets.exceptions.ConnectionClosedError as e:
            logger.error(f"Connection closed unexpectedly: {e}")
        
        except Exception as e:
            logger.error(f"An unexpected error occurred: {e}")
    
    # Placeholder for 'print' command
    async def print(self, *args):
        pass
    
    # Handle 'load' command
    async def load(self, *args):
        try:
            if args and args[0] == 'zip' and args[1]:
                job = PrintJob(args[1])
                self.queues['print'].put(job.serialize())
        except Exception as e:
            logger.error(f"Error in load command: {e}")
    
    # Placeholder for 'status' command
    async def status(self, *args):
        pass
    
    # Placeholder for 'files' command
    async def files(self, *args):
        pass
    
    # Placeholder for 'exit' command
    async def exit(self, *args):
        pass
    
    # Placeholder for 'reboot' command
    async def reboot(self, *args):
        pass
