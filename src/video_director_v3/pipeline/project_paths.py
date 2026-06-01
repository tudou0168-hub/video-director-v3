"""Project path management - all output paths go through here."""
from pathlib import Path


# Project root: pipeline/ -> video_director_v3/ -> src/ -> project root
# So 4 levels up from this file
_PROJECT_ROOT = Path(__file__).parent.parent.parent.parent.resolve()


def get_project_dir(project_id: str, test_mode: bool = False) -> Path:
    """Get the project output directory."""
    if test_mode:
        return _PROJECT_ROOT / "test_outputs" / project_id
    return _PROJECT_ROOT / "outputs" / project_id


def get_combined_index(project_id: str, test_mode: bool = False) -> Path:
    """Get the combined/index.html path."""
    return get_project_dir(project_id, test_mode) / "combined" / "index.html"


def get_hyperframes_timeline_dir(project_id: str, test_mode: bool = False) -> Path:
    """Get the Studio-native HyperFrames project directory."""
    return get_project_dir(project_id, test_mode) / "hyperframes_timeline"


def get_audio_dir(project_id: str, test_mode: bool = False) -> Path:
    """Get the audio directory."""
    return get_project_dir(project_id, test_mode) / "audio"


def get_rendered_dir(project_id: str, test_mode: bool = False) -> Path:
    """Get the rendered directory."""
    return get_project_dir(project_id, test_mode) / "rendered"


def get_review_frames_dir(project_id: str, test_mode: bool = False) -> Path:
    """Get the review_frames directory."""
    return get_project_dir(project_id, test_mode) / "review_frames"


def get_combined_dir(project_id: str, test_mode: bool = False) -> Path:
    """Get the combined directory."""
    return get_project_dir(project_id, test_mode) / "combined"


def ensure_dirs(project_id: str, test_mode: bool = False) -> None:
    """Ensure all required directories exist for a project."""
    project_dir = get_project_dir(project_id, test_mode)
    (project_dir / "audio").mkdir(parents=True, exist_ok=True)
    (project_dir / "hyperframes_timeline" / "assets").mkdir(parents=True, exist_ok=True)
    (project_dir / "review_frames").mkdir(parents=True, exist_ok=True)
    (project_dir / "rendered" / "frames").mkdir(parents=True, exist_ok=True)
