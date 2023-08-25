import os
import threading
import queue
import logging
import time

from lib.job import PrintJob
from lib.layer import LayerManager
from lib.mask import MaskError
from lib.model import Model, ModelError
from lib.stepper import StepperDriverError
from lib.unpack import UnpackerError

from settings import system_dict
from settings import settings_dict


# Configure logging
logger = logging.getLogger(__name__)


class PrintLoop:

    def __init__(self, queues, stop_event):
        self.queues = queues
        self.stopped = stop_event

        self.paused = threading.Event()
        self.paused.set()

        self.model = Model()
        self.layer_manager = LayerManager()

        self.loop()

    def loop(self):
        while True:
            try:
                sjob = self.queues['print'].get(timeout=2)
                if sjob:
                    job = PrintJob()
                    print("THEJOB")
                    job.deserialize(sjob)
                    print(job.path)
                    self.model.load(job.path)
                    self.layer_manager.load(self.model)

                    if self.stopped.is_set() or self.paused.is_set():
                        continue

                    logger.info("Print started...")
                    while self.layer_manager.current_layer < self.layer_manager.total_layers:
                        self.layer_manager.next()
                    else:
                        logger.info("Print ended...")
                        self.layer_manager.stepper.up(100000)

            except queue.Empty:
                time.sleep(1)
            except ModelError as e:
                logger.error(f"Error while loading the model. Cannot start print. Reason: {e}")
                self.stopped.set()
            except UnpackerError as e:
                logger.error(f"Error while unpacking the zip. Cannot start print. Reason: {e}")
                self.stopped.set()
            except MaskError as e:
                logger.error(f"Mask Error while Processing layer. Stopping print. Reason: {e}")
                self.stopped.set()
            except StepperDriverError as e:
                logger.error(f"StepperDriver Error while Processing layer. Stopping print. Reason: {e}")
                self.stopped.set()
            except Exception as e:
                logger.error(f"Unhandled Error while Processing layer. Stopping print. Reason: {e}")
                raise
                self.stopped.set()

    @property
    def progress(self):
        return self.layer_manager.current_layer / self.layer_manager.total_layers
