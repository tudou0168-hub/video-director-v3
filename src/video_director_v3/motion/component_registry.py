"""Component registry - registers and manages visual components."""
from typing import Dict, Any, List


COMPONENT_REGISTRY: Dict[str, Dict[str, Any]] = {}


def register_component(name: str, spec: Dict[str, Any]) -> None:
    """Register a visual component."""
    COMPONENT_REGISTRY[name] = spec


def get_component(name: str) -> Dict[str, Any]:
    """Get a registered component."""
    return COMPONENT_REGISTRY.get(name, {})


def list_components() -> List[str]:
    """List all registered components."""
    return list(COMPONENT_REGISTRY.keys())