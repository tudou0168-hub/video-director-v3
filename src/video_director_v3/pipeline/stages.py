"""Pipeline stages for video-director-v3."""
from enum import Enum


class OutputMode(str, Enum):
    HYPERFRAMES_PREVIEW = "hyperframes_preview"
    RENDER_MP4 = "render_mp4"


class PipelineStage(str, Enum):
    # Design
    DESIGN_DIALS = "design_dials"
    DESIGN_PROFILE = "design_profile"
    BRANDKIT = "brandkit"
    STITCH_DESIGN = "stitch_design"

    # Director
    SCRIPT_SEMANTIC = "script_semantic"
    INPUT_RELEVANCE = "input_relevance"
    NARRATION_PLAN = "narration_plan"
    STORYBOARD = "storyboard"

    # TTS
    TTS = "tts"
    AUDIO_TIMELINE = "audio_timeline"

    # Motion
    VISUAL_BEATS = "visual_beats"
    CAPTION_BEATS = "caption_beats"
    MOTION_EVENTS = "motion_events"
    SEMANTIC_TRANSITIONS = "semantic_transitions"

    # Render
    COMBINED_HTML = "combined_html"
    REVIEW_FRAMES = "review_frames"
    QUALITY_CHECK = "quality_check"

    # Gate
    APPROVAL = "approval"

    # Render MP4
    BROWSER_RENDER = "browser_render"
    RENDERED_OUTPUT = "rendered_output"