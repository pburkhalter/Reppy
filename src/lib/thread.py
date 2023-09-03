import threading
import queue


class ThreadManager:
    """Class for managing multiple threads and their communication queues."""

    def __init__(self):
        """Initialize the ThreadManager instance with empty dictionaries for queues, threads, and stop events."""
        self.queues = {}  # Dictionary holding all the queues
        self.threads = {}  # Dictionary to store threads
        self.stop_events = {}  # Dictionary to store stop events for threads

        # Initialize print and system queues
        self.queues['print'] = queue.Queue()
        self.queues['cmd'] = queue.Queue()

    def register(self, name, func, **kwargs):
        """Register a new thread with its function, name, and optional arguments.

        Parameters:
            name (str): The name of the thread.
            func (callable): The function that the thread will execute.
            **kwargs: Optional keyword arguments to pass to the thread function.
        """
        # Register stop event for the thread
        self.stop_events[name] = threading.Event()

        # Register the thread
        self.threads[name] = threading.Thread(
            target=func,
            name=name,
            args=(self.queues, self.stop_events[name]),
            kwargs=kwargs)

    def start(self):
        """Start all registered threads."""
        # Start threads
        for _, thread in self.threads.items():
            thread.start()

    def stop(self):
        """Gracefully stop all registered threads."""
        # Signal each thread to stop by setting their respective stop events
        for key, event in self.stop_events.items():
            event.set()
