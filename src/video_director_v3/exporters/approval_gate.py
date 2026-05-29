"""Approval gate - manages user approval before render."""
from pathlib import Path
from typing import Dict, Any


def check_approval(project_dir: str) -> bool:
    """Check if project has been approved."""
    approval_file = Path(project_dir) / "approval_required.json"
    if not approval_file.exists():
        return False
    return True


def require_approval(project_dir: str) -> None:
    """Require approval before proceeding."""
    if not check_approval(project_dir):
        raise PermissionError("Project not approved - run hyperframes_preview first")


def mark_approved(project_dir: str) -> None:
    """Mark project as approved."""
    approval_file = Path(project_dir) / "approval_required.json"
    content = '{"status": "approved"}'
    approval_file.write_text(content, encoding="utf-8")