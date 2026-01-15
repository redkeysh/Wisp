"""Discord-specific utilities including object serialization."""

from typing import Any, Dict


def serialize_discord_object(obj: Any) -> Dict[str, Any]:
    """Serialize a Discord object to a dictionary.

    Args:
        obj: Discord object to serialize

    Returns:
        Dictionary representation of the object
    """
    if obj is None:
        return {}

    if hasattr(obj, "__dict__"):
        result: Dict[str, Any] = {}
        for key, value in obj.__dict__.items():
            if not key.startswith("_"):
                if hasattr(value, "__dict__"):
                    result[key] = serialize_discord_object(value)
                elif isinstance(value, (list, tuple)):
                    result[key] = [
                        serialize_discord_object(item) if hasattr(item, "__dict__") else item
                        for item in value
                    ]
                else:
                    result[key] = value
        return result

    return {"__str__": str(obj)}
