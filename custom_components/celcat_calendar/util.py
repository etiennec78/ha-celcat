"""Utils for Celcat Calendar"""

from .const import DOMAIN


async def list_to_dict(lst: list[str]) -> dict[str, str]:
    """Convert a list of strings to a dictionary."""
    try:
        return {item.split(":")[0]: item.split(":")[1] for item in lst}
    except IndexError as exc:
        raise ValueError(
            "Invalid format: Each item must contain a ':' separating keys and value."
        ) from exc


def get_translation(translations: dict[str, str], key: str) -> str:
    """Get translation with fallback to English."""
    return translations.get(
        f"component.{DOMAIN}.selector.title.options.{key}",
        key.capitalize(),
    )
