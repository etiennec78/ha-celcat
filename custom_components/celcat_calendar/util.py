"""Utils for Celcat Calendar"""


async def list_to_dict(lst: list[str]) -> dict[str, str]:
    """Convert a list of strings to a dictionary."""
    try:
        return {item.split(":")[0]: item.split(":")[1] for item in lst}
    except IndexError as exc:
        raise ValueError(
            "Invalid format: Each item must contain a ':' separating keys and value."
        ) from exc
