"""Test that all outputs go to outputs/ or test_outputs/, never src/outputs."""
from pathlib import Path
import sys

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from video_director_v3.pipeline.project_paths import (
    get_project_dir,
    get_audio_dir,
    get_review_frames_dir,
    get_rendered_dir,
)


def test_outputs_dir_uses_outputs():
    """Test that get_project_dir uses outputs/ for test_mode=False."""
    result = get_project_dir("test_project", test_mode=False)
    assert "outputs" in result.parts, f"Expected outputs/ in path, got {result}"
    assert "test_outputs" not in result.parts, f"Did not expect test_outputs/ in path, got {result}"


def test_test_outputs_dir_uses_test_outputs():
    """Test that get_project_dir uses test_outputs/ for test_mode=True."""
    result = get_project_dir("test_project", test_mode=True)
    assert "test_outputs" in result.parts, f"Expected test_outputs/ in path, got {result}"


def test_audio_dir_in_project():
    """Test that audio dir is under project dir."""
    result = get_audio_dir("my_project", test_mode=False)
    assert "my_project" in result.parts
    assert "audio" in result.parts


def test_review_frames_dir_in_project():
    """Test that review_frames dir is under project dir."""
    result = get_review_frames_dir("my_project", test_mode=False)
    assert "my_project" in result.parts
    assert "review_frames" in result.parts


def test_rendered_dir_in_project():
    """Test that rendered dir is under project dir."""
    result = get_rendered_dir("my_project", test_mode=False)
    assert "my_project" in result.parts
    assert "rendered" in result.parts


def test_no_src_outputs_in_path():
    """Verify src/outputs is never used."""
    result = get_project_dir("p", test_mode=False)
    path_str = str(result)
    assert "src/outputs" not in path_str, f"Found src/outputs in {path_str}"
    assert "src" not in result.parts or "outputs" not in result.parts, f"Found src/outputs in {result}"