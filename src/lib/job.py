import json
import datetime
import logging
import uuid


# Configure logging
logger = logging.getLogger(__name__)


class PrintJob:
    def __init__(self, path=None, msg_id=None, timestamp=None):
        # Use provided ID or generate a new one
        self.id = msg_id if msg_id else uuid.uuid4()

        # Use provided timestamp or get the current time
        self.timestamp = timestamp if timestamp else datetime.datetime.now().isoformat()

        # Path to the directory holding the files to print
        self.path = path

    def serialize(self):
        """Converts the message into a JSON string."""
        return json.dumps({
            "header": {
                "id": str(self.id),
                "timestamp": self.timestamp,
            },
            "path": self.path
        })

    @classmethod
    def deserialize(cls, message_str):
        """Converts a JSON string back into a Message object."""
        parsed = json.loads(message_str)
        # Construct a new TaskMessage object using parsed data
        return cls(
            path=parsed["path"],
            msg_id=uuid.UUID(parsed["header"]["id"]),  # Convert string to UUID
            timestamp=parsed["header"]["timestamp"]
        )
