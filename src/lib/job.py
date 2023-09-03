import json
import datetime
import logging
import uuid

# Configure logging
logger = logging.getLogger(__name__)

class PrintJob:
    def __init__(self, path=None, msg_id=None, timestamp=None):
        # Initialize PrintJob attributes with provided or default values
        self.id = msg_id if msg_id else uuid.uuid4().hex
        self.timestamp = timestamp if timestamp else datetime.datetime.now().isoformat()
        self.path = path

    def serialize(self):
        # Serialize the PrintJob object to a JSON string
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
        # Deserialize a JSON string to a PrintJob object
        parsed = json.loads(message_str)
        logger.debug(f"Deserializing print job {parsed['header']['id']}")
        return cls(
            path=parsed["path"],
            msg_id=parsed["header"]["id"],
            timestamp=parsed["header"]["timestamp"]
        )
