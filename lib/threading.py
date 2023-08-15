import threading
import queue
import logging

from settings import settings_dict


class ThreadManager:
    def __init__(self):
        self.queues = {} # Dictionary to store queues
        self.threads = {}  # Dictionary to store threads
        self.stop_events = {}  # Dictionary to store stop events for threads

    def register(self, name, func, **kwargs):
        # register queue
        self.queues[name] = queue.Queue()

        # register stop event
        self.stop_events[name] = threading.Event()

        # register thread
        self.threads[name] = threading.Thread(
            target=func,
            name=name,
            args=(self.queues[name],),
            kwargs=kwargs)

    def start(self):
        # Start threads
        for _, thread in self.threads.items():
            thread.start()

    def stop(self):
        # Gracefully stop all threads.
        for key, event in self.stop_events.items():
            event.set()  # Signal each thread to stop


