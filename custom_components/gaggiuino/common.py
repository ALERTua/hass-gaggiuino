"""Common tools for Gaggiuino Integration."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from collections.abc import Callable


def get_status_attr(
    attr_name: str,
    transform_fn: Callable[[Any], Any] | None = None,
) -> Callable[[Any], Any]:
    """Create a function to safely get and optionally transform status attributes."""

    def get_value(coordinator: Any) -> Any:
        status = None
        if (
            coordinator.data is None
            or (status := coordinator.data.get("status", None)) is None
        ):
            return None

        value = getattr(status, attr_name, None)
        if value is not None and transform_fn is not None:
            return transform_fn(value)
        return value

    return get_value
