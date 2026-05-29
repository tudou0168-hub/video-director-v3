"""Design dials - three knobs to control visual output."""
from typing import Dict, Any


def create_design_dials(
    design_variance: int = 7,
    motion_intensity: int = 6,
    visual_density: int = 8,
) -> Dict[str, Any]:
    """Create design dial settings."""
    return {
        "design_variance": design_variance,
        "motion_intensity": motion_intensity,
        "visual_density": visual_density,
    }