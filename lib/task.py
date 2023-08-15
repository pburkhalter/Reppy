import json
import datetime
import uuid


# Usage for message transport between threads (via message queue):
# task = TaskMessage(recipient, command, message, msg_id, timestamp)
# serialized_task = task.serialize()
# received_task = TaskMessage.deserialize(serialized_task)


class TaskMessage:
    def __init__(self, recipient, command, message=None, msg_id=None, timestamp=None):
        # Use provided ID or generate a new one
        self.id = msg_id if msg_id else uuid.uuid4()

        # Use provided timestamp or get the current time
        self.timestamp = timestamp if timestamp else datetime.datetime.now().isoformat()

        self.data = message
        self.command = command
        self.recipient = recipient

    def serialize(self):
        """Converts the message into a JSON string."""
        return json.dumps({
            "header": {
                "id": str(self.id),
                "command": self.command,
                "recipient": self.recipient,
                "timestamp": self.timestamp,
            },
            "body": self.data
        })

    @classmethod
    def deserialize(cls, message_str):
        """Converts a JSON string back into a Message object."""
        parsed = json.loads(message_str)
        # Construct a new TaskMessage object using parsed data
        return cls(
            recipient=parsed["header"]["recipient"],
            command=parsed["header"]["command"],
            message=parsed["body"],
            msg_id=uuid.UUID(parsed["header"]["id"]),  # Convert string to UUID
            timestamp=parsed["header"]["timestamp"]
        )
