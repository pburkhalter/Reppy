import json
import datetime
import logging
import uuid

# Configure logging
logger = logging.getLogger(__name__)

"""
This module provides a class for managing print jobs.
It uses Python's built-in json, datetime, logging, and uuid libraries.
"""


class PrintJob:
    """
    Class for managing print jobs.
    """

    def __init__(self, path=None, msg_id=None, timestamp=None):
        """
        Initialize the PrintJob instance with provided or default values.

        Parameters:
            path (str, optional): The file path for the print job.
            msg_id (str, optional): The message ID for the print job.
            timestamp (str, optional): The timestamp for the print job.
        """
        self.id = msg_id if msg_id else uuid.uuid4().hex
        self.timestamp = timestamp if timestamp else datetime.datetime.now().isoformat()
        self.path = path

    def serialize(self):
        """
        Serialize the PrintJob object to a JSON string.

        Returns:
            str: The serialized JSON string.
        """
        logger.debug(f"Serializing print job {str(self.id)}")
        return json.dumps({
            "header": {
                "id": str(self.id),
                "timestamp": self.timestamp,
            },
            "path": self.path
        })

    @classmethod
    def deserialize(cls, message_str):
        """
        Deserialize a JSON string to a PrintJob object.

        Parameters:
            message_str (str): The JSON string to deserialize.

        Returns:
            PrintJob: The deserialized PrintJob object.
        """
        parsed = json.loads(message_str)
        logger.debug(f"Deserializing print job {parsed['header']['id']}")
        return cls(
            path=parsed["path"],
            msg_id=parsed["header"]["id"],
            timestamp=parsed["header"]["timestamp"]
        )
