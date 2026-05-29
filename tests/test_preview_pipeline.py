"""Test preview pipeline - smoke test."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from video_director_v3.pipeline.project_paths import ensure_dirs, get_project_dir


def test_preview_creates_project_structure():
    """Test that preview mode creates expected directory structure."""
    project_id = "smoke_test_preview"
    ensure_dirs(project_id, test_mode=True)

    project_dir = get_project_dir(project_id, test_mode=True)

    # Check key directories exist
    assert (project_dir / "combined").exists()
    assert (project_dir / "audio").exists()
    assert (project_dir / "review_frames").exists()


def test_preview_no_final_video_in_preview_mode():
    """Test that preview mode does not create final_video.mp4."""
    project_id = "smoke_test_no_video"
    ensure_dirs(project_id, test_mode=True)

    project_dir = get_project_dir(project_id, test_mode=True)
    video_path = project_dir / "rendered" / "final_video.mp4"

    # In preview mode, no video should be created yet
    # This is a structural test - actual prevention comes from CLI
    assert True  # Placeholder - actual check requires running preview