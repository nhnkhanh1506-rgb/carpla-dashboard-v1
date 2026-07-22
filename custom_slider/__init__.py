from pathlib import Path
import streamlit.components.v1 as components

_FRONTEND_DIR = Path(__file__).parent / "frontend"

_slider_component = components.declare_component(
    "carpla_styled_slider",
    path=str(_FRONTEND_DIR),
)


def carpla_slider(
    *,
    value: int,
    min_value: int = 0,
    max_value: int = 100,
    step: int = 1,
    key: str | None = None,
) -> int:
    """Interactive slider styled to match the original Carpla progress bar."""
    result = _slider_component(
        value=int(value),
        min_value=int(min_value),
        max_value=int(max_value),
        step=int(step),
        key=key,
        default=int(value),
    )

    try:
        return int(result)
    except (TypeError, ValueError):
        return int(value)
