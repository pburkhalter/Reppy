import json
import datetime
import logging
import uuid


# Configure logging
logger = logging.getLogger(__name__)


class PrintJob:
    def __init__(self, path=None, msg_id=None, timestamp=None):
        self.id = msg_id if msg_id else uuid.uuid4()
        self.timestamp = timestamp if timestamp else datetime.datetime.now().isoformat()
        self.path = path

    def serialize(self):
        return json.dumps({
            "header": {
                "id": str(self.id),
                "timestamp": self.timestamp,
            },
            "path": self.path
        })

    @classmethod
    def deserialize(cls, message_str):
        parsed = json.loads(message_str)
        return cls(
            path=parsed["path"],
            msg_id=uuid.UUID(parsed["header"]["id"]),
            timestamp=parsed["header"]["timestamp"]
        )
