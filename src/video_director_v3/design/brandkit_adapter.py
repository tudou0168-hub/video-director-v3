"""Brandkit adapter - loads and adapts brand colors/fonts."""
from typing import Dict, Any, Optional


def load_brandkit(brandkit_path: Optional[str] = None) -> Dict[str, Any]:
    """Load brandkit configuration."""
    return {}


def adapt_brandkit(brandkit: Dict[str, Any]) -> Dict[str, Any]:
    """Adapt brandkit for video output."""
    return brandkit