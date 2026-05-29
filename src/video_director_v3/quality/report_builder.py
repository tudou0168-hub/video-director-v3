"""Report builder - builds quality and preview reports."""
from typing import Dict, Any


def build_preview_report(
    project_dir: str,
    checks: Dict[str, Any],
) -> str:
    """Build preview report markdown."""
    return "# Preview Report\n\nStub - implementation pending"


def build_quality_report(
    checks: Dict[str, Any],
    scores: Dict[str, float],
) -> Dict[str, Any]:
    """Build quality report JSON."""
    return {"passed": False, "checks": [], "scores": scores}