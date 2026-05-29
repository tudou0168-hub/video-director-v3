"""Design profile builder - combines dials, brandkit, design.md into profile."""
from typing import Dict, Any, Optional


def build_design_profile(
    semantics: Dict[str, Any],
    dials: Dict[str, Any],
    brandkit: Optional[Dict[str, Any]] = None,
    design_md: Optional[str] = None,
) -> Dict[str, Any]:
    """Build visual style profile."""
    return {
        "aspect_ratio": "9:16",
        "design_variance": dials.get("design_variance", 7),
        "motion_intensity": dials.get("motion_intensity", 6),
        "visual_density": dials.get("visual_density", 8),
        "layout_strategy": "centered",
        "hook_strategy": "metrics_focus",
        "caption_style": {},
        "color_tokens": {},
        "component_preferences": [],
        "transition_style": "fade",
        "density_rules": {},
    }