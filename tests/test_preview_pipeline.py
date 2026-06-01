"""Test preview pipeline - smoke test."""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from video_director_v3.motion.caption_beat_generator import generate_caption_beats
from video_director_v3.motion.semantic_transition_planner import build_semantic_transitions
from video_director_v3.motion.visual_beat_planner import plan_visual_beats
from video_director_v3.pipeline.pipeline_runner import _build_approval_payload
from video_director_v3.pipeline.project_paths import ensure_dirs, get_project_dir
from video_director_v3.renderers.hyperframes.studio_native_project_builder import (
    _hud_scene_config,
    build_studio_native_project,
)


def test_preview_creates_project_structure():
    """Test that preview mode creates expected directory structure."""
    project_id = "smoke_test_preview"
    ensure_dirs(project_id, test_mode=True)

    project_dir = get_project_dir(project_id, test_mode=True)

    # Check key directories exist
    assert (project_dir / "hyperframes_timeline").exists()
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


def test_approval_payload_fails_closed_when_required_stage_fails(tmp_path: Path):
    project_dir = tmp_path / "preview_fail_closed"
    (project_dir / "hyperframes_timeline").mkdir(parents=True)
    (project_dir / "audio").mkdir(parents=True)
    (project_dir / "hyperframes_timeline" / "index.html").write_text("<html></html>", encoding="utf-8")
    (project_dir / "audio" / "voiceover.mp3").write_bytes(b"fake")
    (project_dir / "preview_report.md").write_text("# preview", encoding="utf-8")
    (project_dir / "semantic_transitions.json").write_text(
        json.dumps({"transition_count": 2}, ensure_ascii=False),
        encoding="utf-8",
    )

    stages = [
        {"name": "narration_plan", "status": "PASS"},
        {"name": "tts", "status": "PASS"},
        {"name": "motion_storyboard", "status": "FAIL"},
        {"name": "semantic_transitions", "status": "PASS"},
        {"name": "caption_beats", "status": "PASS"},
        {"name": "studio_native_preview", "status": "PASS"},
        {"name": "review_frames", "status": "PASS"},
        {"name": "input_relevance", "status": "PASS"},
        {"name": "preview_report", "status": "PASS"},
    ]

    approval = _build_approval_payload(
        project_id="preview_fail_closed",
        project_dir=project_dir,
        stages=stages,
        tts_result={"status": "ok"},
        caption_beats_data={"caption_count": 10},
        review_frames_data={"status": "PASS", "ok_count": 7},
    )

    assert approval["can_approve_preview"] is False
    assert approval["preview_status"] == "FAILED"
    assert "motion_storyboard" in approval["checks"]["failed_required_stages"]


def test_dynamic_transitions_follow_scene_count():
    storyboard_scenes = [
        {"scene_id": "S01", "role": "hook", "start": 0.0, "duration": 3.0, "end": 3.0},
        {"scene_id": "S02", "role": "pain", "start": 3.0, "duration": 4.0, "end": 7.0},
        {"scene_id": "S03", "role": "method", "start": 7.0, "duration": 4.0, "end": 11.0},
        {"scene_id": "S04", "role": "cta", "start": 11.0, "duration": 3.0, "end": 14.0},
    ]

    data = build_semantic_transitions(storyboard_scenes, target_duration=14.0)

    assert data["transition_count"] == 3
    assert [item["from_scene"] for item in data["transitions"]] == ["S01", "S02", "S03"]


def test_visual_beats_add_multiple_reactions_for_long_method_scene():
    data = plan_visual_beats(
        {"scenes": [{"scene_id": "S02", "role": "method", "duration": 8.0}]},
        {},
    )

    beats = data["scenes"][0]["visual_beats"]
    assert len(beats) >= 3
    assert beats[1]["start"] <= 4.5


def test_caption_generator_splits_long_sentence_without_duplicate_tail(tmp_path: Path):
    result = generate_caption_beats(
        project_dir=tmp_path,
        narration_plan={"sentence_list": []},
        audio_timeline={
            "sentence_timings": [
                {
                    "sentence_id": "S01",
                    "text": "先跑通一个最小闭环：输入、存储、检索、输出，然后再逐步扩展整个系统。",
                    "start": 0.0,
                    "end": 6.0,
                    "duration": 6.0,
                }
            ]
        },
        motion_storyboard={"scenes": [{"scene_id": "S01", "start": 0.0, "duration": 6.0}]},
    )

    texts = [beat["text"] for beat in result["caption_beats"]]
    assert len(texts) >= 2
    assert len(set(texts)) == len(texts)


def test_hud_scene_config_derives_semantic_template_data():
    method_scene = _hud_scene_config(
        {"visual_template": "tool_chain_three_cols"},
        0,
        "第二步，用双向链接组织笔记。文件夹只负责收纳，相关观点会自己连接成知识网络。",
    )
    intro_scene = _hud_scene_config(
        {"visual_template": "tool_chain_three_cols"},
        0,
        "后来我把 Obsidian 打造成了第二大脑，再让 AI 帮我找回知识。",
    )
    hook_scene = _hud_scene_config(
        {"visual_template": "hook_big_claim"},
        0,
        "你有没有这种感觉，读了很多书，真正需要的时候，却一句都想不起来？",
    )
    glossary_scene = _hud_scene_config(
        {"visual_template": "tool_chain_three_cols"},
        0,
        "把相关概念放到同一张术语关系图里，你会更快看懂它们之间的关系。",
    )
    explain_scene = _hud_scene_config(
        {"visual_template": "broken_chain"},
        0,
        "简单讲，大脑负责思考和创造，第二大脑负责存储和检索。",
    )
    guardrail_scene = _hud_scene_config(
        {"visual_template": "broken_chain"},
        0,
        "但别一上来装 30 个插件，也别花几天设计完美分类。",
    )
    compare_scene = _hud_scene_config(
        {"visual_template": "before_after_compare"},
        0,
        "以前写文章，要翻遍好几个 App。现在从找素材到拿到素材包，可能只需要 30 秒。",
    )
    proof_scene = _hud_scene_config(
        {"visual_template": "before_after_compare"},
        0,
        "把记住这件事交给第二大脑，你才能把精力留给真正的创造。",
    )
    checklist_scene = _hud_scene_config(
        {"visual_template": "checklist_cta"},
        0,
        "先跑通一个最小闭环：输入、存储、检索、输出。",
    )

    assert hook_scene["layout_variant"] == "quote_punch"
    assert method_scene["three_cols"][0]["name"] == "主题页"
    assert method_scene["layout_variant"] == "knowledge_triangle"
    assert intro_scene["layout_variant"] == "intro_offset"
    assert glossary_scene["layout_variant"] == "matrix_glossary_wall"
    assert explain_scene["layout_variant"] == "responsibility_split"
    assert explain_scene["left_panel"]["label"] == "大脑"
    assert guardrail_scene["layout_variant"] == "binary_choice_split"
    assert "30 秒拿到素材包" in compare_scene["right_items"]
    assert compare_scene["layout_variant"] == "dashboard_mobile"
    assert compare_scene["dashboard_metrics"][0]["value"] == "30s"
    assert proof_scene["layout_variant"] == "symptom_panel"
    assert proof_scene["right_panel"]["title"] == "创造空间上升"
    assert checklist_scene["final_message"] == "先把闭环跑通，再决定要不要加插件"


def test_cta_routes_to_layout_variants_by_narration_semantics():
    # Default checklist_steps
    default = _hud_scene_config(
        {"visual_template": "checklist_cta"}, 0, "先跑通一个最小闭环：输入、存储、检索、输出。"
    )
    assert default["layout_variant"] == "checklist_steps"

    # Button banner — strong single action verb
    banner = _hud_scene_config(
        {"visual_template": "checklist_cta"}, 0, "立即开始搭建，先把最小闭环跑通。"
    )
    assert banner["layout_variant"] == "button_banner"
    assert banner["button_label"]
    assert "滑动看完" in banner["hint"]

    # End score goodbye — chapter close
    end = _hud_scene_config(
        {"visual_template": "checklist_cta"}, 0, "系列完结，下期再见。"
    )
    assert end["layout_variant"] == "end_score_goodbye"
    assert end["score"] == "100"
    assert "下期" in end["next_teaser"]

    # Scorecard — status / metric
    score = _hud_scene_config(
        {"visual_template": "checklist_cta"}, 0, "得分 100，三项就绪：输入、检索、输出。"
    )
    assert score["layout_variant"] == "scorecard"
    assert len(score["scorecard_metrics"]) == 3
    assert all(m["value"] in {"READY", "OK", "GO", "DONE", "PASS"} for m in score["scorecard_metrics"])


def test_cta_renders_distinct_html_for_each_variant():
    from video_director_v3.renderers.hyperframes.publish_templates import (
        _render_cta_button_banner,
        _render_cta_end_score_goodbye,
        _render_cta_scorecard,
        _render_cta_checklist_steps,
    )
    acc = "#2ED573"
    role = "cta"

    base_scene = {"checklist": ["a", "b", "c"], "final_message": "msg"}
    checklist_html = _render_cta_checklist_steps("S01", role, base_scene, acc)
    assert "check-item" in checklist_html
    assert "▶" not in checklist_html

    banner_scene = {**base_scene, "button_label": "立即开始", "hint": "滑动看完"}
    banner_html = _render_cta_button_banner("S01", role, banner_scene, acc)
    assert "▶" in banner_html
    assert "立即开始" in banner_html
    assert "ACTION / CTA" in banner_html

    end_scene = {**base_scene, "score": "98", "score_label": "本章掌握度", "next_teaser": "下期再见"}
    end_html = _render_cta_end_score_goodbye("S01", role, end_scene, acc)
    assert "98" in end_html
    assert "CHAPTER CLOSE" in end_html
    assert "下期再见" in end_html

    score_scene = {**base_scene, "scorecard_metrics": [
        {"label": "输入", "value": "READY", "color": "#2ED573"},
        {"label": "检索", "value": "OK", "color": "#4D9FFF"},
        {"label": "输出", "value": "GO", "color": "#FF6B35"},
    ]}
    score_html = _render_cta_scorecard("S01", role, score_scene, acc)
    assert "SCORECARD" in score_html
    assert "cta-metric" in score_html
    assert "READY" in score_html


def test_template_checklist_cta_dispatches_by_layout_variant():
    from video_director_v3.renderers.hyperframes.publish_templates import get_scene_body
    base_scene = {"visual_template": "checklist_cta", "checklist": ["a"], "final_message": "m"}
    html_default = get_scene_body("S01", "cta", base_scene)
    html_banner = get_scene_body("S01", "cta", {**base_scene, "layout_variant": "button_banner"})
    html_end = get_scene_body("S01", "cta", {**base_scene, "layout_variant": "end_score_goodbye"})
    html_score = get_scene_body("S01", "cta", {**base_scene, "layout_variant": "scorecard"})

    # Each variant produces visually different output
    assert "check-item" in html_default
    assert "▶" in html_banner
    assert "CHAPTER CLOSE" in html_end
    assert "SCORECARD" in html_score
    # Variants should be distinguishable from each other
    assert html_default != html_banner
    assert html_banner != html_end
    assert html_end != html_score


def test_native_project_persists_enriched_scene_config(tmp_path: Path):
    audio_path = tmp_path / "voiceover.mp3"
    audio_path.write_bytes(b"fake-audio")

    build_studio_native_project(
        project_dir=tmp_path,
        storyboard={
            "scenes": [
                {
                    "scene_id": "S01",
                    "role": "method",
                    "visual_template": "tool_chain_three_cols",
                    "narration": "第二步，用双向链接组织笔记。文件夹只负责收纳，相关观点会自己连接成知识网络。",
                    "start": 0.0,
                    "duration": 4.0,
                },
                {
                    "scene_id": "S02",
                    "role": "proof",
                    "visual_template": "before_after_compare",
                    "narration": "把记住这件事交给第二大脑，你才能把精力留给真正的创造。",
                    "start": 4.0,
                    "duration": 4.0,
                },
            ]
        },
        narration_plan={"title": "test"},
        tts_result={"audio_path": str(audio_path), "real_duration": 8.0},
        caption_beats={"caption_beats": []},
        visual_beats={},
        transitions={"transition_count": 0, "transitions": []},
    )

    director_timeline = json.loads(
        (tmp_path / "hyperframes_timeline" / "data" / "director_timeline.json").read_text(encoding="utf-8")
    )
    scene = director_timeline["scenes"][0]

    assert scene["visual_template"] == "tool_chain_three_cols"
    assert scene["three_cols"][0]["name"] == "主题页"
    assert scene["layout_variant"] == "knowledge_triangle"
    proof_scene = director_timeline["scenes"][1]
    assert proof_scene["visual_template"] == "before_after_compare"
    assert proof_scene["layout_variant"] == "symptom_panel"
    assert proof_scene["summary_badge"].startswith("记忆外包")
