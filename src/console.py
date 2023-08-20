import time


class ConsoleHandler:

    def __init__(self):
        self.commands = {
            "print": self.print,
            "status": self.status,
            "cache": self.cache,
            "exit": self.exit,
            "reboot": self.exit,
        }

    def run(self):
        try:
            time.sleep(2)
            while True:
                # Get user input and tokenize it
                user_input = input("Enter a command: ")
                tokens = user_input.split()

                if tokens:
                    cmd = tokens[0]
                    args = tokens[1:]

                    if cmd in self.commands:
                        # Pass the arguments to the method
                        self.commands[cmd](*args)
                    else:
                        print(f"Unknown command '{cmd}'")
        except KeyboardInterrupt:
            print("\nExiting the program. Goodbye!")
        except Exception as e:
            print(f"An error occurred: {e}")

    def print(self):
        pass

    def status(self):
        pass

    def exit(self):
        pass

    def reboot(self):
        pass

    def cache(self, *args):
        # Check if the 'file' argument is passed
        if args and args[0] == 'clear' and args[1] == 'upload':
            pass
        elif args and args[0] == 'clear' and args[1] == 'unpack':
            pass
        elif args and args[0] == 'clear' and args[1] == 'jobs':
            pass

