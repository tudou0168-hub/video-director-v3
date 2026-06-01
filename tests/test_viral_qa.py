"""Test V3-P3.6: Viral QA evaluator — 6-dimension scoring + A/B manifest."""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from video_director_v3.qa.viral_qa_evaluator import (
    HOOK_SIGNALS,
    PROMISE_SIGNALS,
    SAVEABLE_SIGNALS,
    COMMENT_SIGNALS,
    _count_signal_hits,
    _score_hook,
    _score_promise,
    _score_saveable,
    _score_comment,
    _score_visual_rhythm,
    _score_sync_reliability,
    build_viral_quality_report,
)


# ─── Signal counting primitives ───

def test_signal_counting_returns_zero_for_empty_text():
    assert _count_signal_hits("", HOOK_SIGNALS) == 0


def test_signal_counting_finds_overlap():
    text = "为什么需要记住？真相是：先跑通"
    hits = _count_signal_hits(text, HOOK_SIGNALS)
    assert hits >= 3  # 为什么 / 记住 / 真相


def test_signal_counting_deduplicates_overlapping_signals():
    text = "为什么为什么为什么"
    hits = _count_signal_hits(text, HOOK_SIGNALS)
    assert hits == 1  # each signal in the tuple counts once


# ─── Per-dimension scoring ───

def test_hook_scores_high_with_impact_keyword_and_short_first_sentence():
    plan = {"sentence_list": [
        {"text": "为什么记住的总是金句？", "emphasis_words": ["金句"]},
    ]}
    storyboard = {"scenes": [{"visual_template": "hook_big_claim"}]}
    result = _score_hook(plan, storyboard)
    assert result["score"] >= 7


def test_hook_scores_low_with_no_impact_keyword():
    plan = {"sentence_list": [{"text": "今天我们聊一聊笔记的事情。", "emphasis_words": []}]}
    storyboard = {"scenes": [{"visual_template": "hook_big_claim"}]}
    result = _score_hook(plan, storyboard)
    assert result["score"] < 5


def test_promise_scores_high_with_clear_method_signals():
    plan = {"sentence_list": [
        {"text": "开篇短句"},
        {"text": "今天我会告诉你三个步骤，怎么用 AI 找回笔记。"},
        {"text": "看完你就会掌握方法。"},
    ]}
    result = _score_promise(plan)
    assert result["score"] >= 7


def test_promise_scores_zero_without_method_signals():
    plan = {"sentence_list": [
        {"text": "开篇"},
        {"text": "这是后续。"},
        {"text": "这是更多。"},
    ]}
    result = _score_promise(plan)
    assert result["score"] == 0


def test_saveable_scores_high_with_reusable_structure_keywords():
    plan = {"sentence_list": [
        {"text": f"今天讲 {len(SAVEABLE_SIGNALS) + 2} 个步骤，第一步建库，第二步建结构，第三步建流程"},
    ]}
    result = _score_saveable(plan)
    assert result["score"] >= 9


def test_saveable_scores_zero_without_keywords():
    plan = {"sentence_list": [{"text": "我想说一些事情。"}]}
    result = _score_saveable(plan)
    assert result["score"] == 0


def test_comment_scores_high_with_natural_questions():
    plan = {"sentence_list": [
        {"text": "你愿意先做哪一步？评论区告诉我你的现状。"},
    ]}
    result = _score_comment(plan)
    assert result["score"] >= 9


def test_comment_penalizes_mechanical_cta_keywords():
    plan = {"sentence_list": [
        {"text": "点赞关注订阅三连，别错过！"},
    ]}
    result = _score_comment(plan)
    # Mechanical CTA should be penalized
    assert result["score"] < 6


def test_visual_rhythm_scores_zero_with_no_scenes():
    assert _score_visual_rhythm({"scenes": []})["score"] == 0


def test_visual_rhythm_scores_proportional_to_unique_templates():
    storyboard = {"scenes": [
        {"visual_template": "hook_big_claim"},
        {"visual_template": "tool_chain_three_cols"},
        {"visual_template": "checklist_cta"},
    ]}
    result = _score_visual_rhythm(storyboard)
    # 3 unique / 3 scenes = 1.0 → score 10 (with bonus capped)
    assert result["score"] >= 8


def test_visual_rhythm_rewards_high_variance():
    storyboard = {"scenes": [
        {"visual_template": f"t{i}"} for i in range(10)
    ]}
    result = _score_visual_rhythm(storyboard)
    assert result["score"] == 10


def test_sync_reliability_scores_zero_when_no_report(tmp_path: Path):
    result = _score_sync_reliability(tmp_path)
    assert result["score"] == 0
    assert "sync_report" in result["details"]


def test_sync_reliability_scores_ten_for_zero_drift(tmp_path: Path):
    smoke = tmp_path / "rendered_smoke"
    smoke.mkdir()
    (smoke / "sync_report.json").write_text(
        json.dumps({
            "status": "PASS",
            "checks": {"max_drift_seconds": 0.0},
        }),
        encoding="utf-8",
    )
    result = _score_sync_reliability(tmp_path)
    assert result["score"] == 10


def test_sync_reliability_scores_seven_for_drift_under_one_second(tmp_path: Path):
    smoke = tmp_path / "rendered_smoke"
    smoke.mkdir()
    (smoke / "sync_report.json").write_text(
        json.dumps({
            "status": "PASS",
            "checks": {"max_drift_seconds": 0.8},
        }),
        encoding="utf-8",
    )
    result = _score_sync_reliability(tmp_path)
    assert 7 <= result["score"] <= 9


def test_sync_reliability_scores_zero_for_failed_sync(tmp_path: Path):
    smoke = tmp_path / "rendered_smoke"
    smoke.mkdir()
    (smoke / "sync_report.json").write_text(
        json.dumps({"status": "FAIL", "checks": {"max_drift_seconds": 5.0}}),
        encoding="utf-8",
    )
    result = _score_sync_reliability(tmp_path)
    assert result["score"] == 0


def test_sync_reliability_accepts_rendered_smoke_subdir(tmp_path: Path):
    # Pass a path that already points at rendered_smoke (not the project root)
    smoke_dir = tmp_path / "rendered_smoke"
    smoke_dir.mkdir()
    (smoke_dir / "sync_report.json").write_text(
        json.dumps({"status": "PASS", "checks": {"max_drift_seconds": 0.0}}),
        encoding="utf-8",
    )
    result = _score_sync_reliability(smoke_dir)
    assert result["score"] == 10


# ─── Full report builder ───

def test_full_report_passes_for_ideal_script(tmp_path: Path):
    smoke = tmp_path / "rendered_smoke"
    smoke.mkdir()
    (smoke / "sync_report.json").write_text(
        json.dumps({"status": "PASS", "checks": {"max_drift_seconds": 0.0}}),
        encoding="utf-8",
    )
    plan = {
        "sentence_list": [
            {"text": "为什么记住的总是金句？真相是：先跑通最小闭环。", "emphasis_words": ["金句"]},
            {"text": "今天我会告诉你三个步骤，让你彻底掌握方法。"},
            {"text": f"步骤一：建库 / 步骤二：建结构 / 步骤三：跑通检索，这是三个清单。"},
            {"text": "你愿意先做哪一步？评论区告诉我你的现状。"},
        ]
    }
    storyboard = {"scenes": [
        {"visual_template": "hook_big_claim"},
        {"visual_template": "framework_quadrant"},
        {"visual_template": "metric_dashboard"},
        {"visual_template": "comment_invite"},
    ]}
    report = build_viral_quality_report(
        project_id="ideal_test",
        project_dir=tmp_path,
        narration_plan=plan,
        storyboard=storyboard,
    )
    assert report["status"] == "PASS"
    assert report["total_score"] >= 42
    assert len(report["failed_dimensions"]) == 0
    assert report["project_id"] == "ideal_test"


def test_full_report_fails_for_minimal_script(tmp_path: Path):
    plan = {"sentence_list": [{"text": "hi"}]}
    storyboard = {"scenes": []}
    report = build_viral_quality_report(
        project_id="minimal_test",
        project_dir=tmp_path,
        narration_plan=plan,
        storyboard=storyboard,
    )
    assert report["status"] == "FAIL"
    assert report["total_score"] < 42


def test_full_report_includes_ab_variant_manifest(tmp_path: Path):
    plan = {"sentence_list": [{"text": "为什么记住？"}]}
    storyboard = {"scenes": [{"visual_template": "hook_big_claim"}]}
    report = build_viral_quality_report(
        project_id="ab_test",
        project_dir=tmp_path,
        narration_plan=plan,
        storyboard=storyboard,
    )
    ab = report["ab_variants"]
    assert "current_hook" in ab
    assert "hook_variants" in ab
    assert "method_variants" in ab
    assert "evidence_variants" in ab
    assert "cta_variants" in ab
    # Variants should not include the current hook
    assert ab["current_hook"] not in ab["hook_variants"]
    assert len(ab["hook_variants"]) == 2


def test_full_report_includes_notes_disclaiming_algorithm(tmp_path: Path):
    plan = {"sentence_list": [{"text": "x"}]}
    storyboard = {"scenes": []}
    report = build_viral_quality_report(
        project_id="x",
        project_dir=tmp_path,
        narration_plan=plan,
        storyboard=storyboard,
    )
    assert "不冒充" in report["notes"] or "不承诺" in report["notes"]


def test_full_report_lists_passed_and_failed_dimensions(tmp_path: Path):
    plan = {"sentence_list": [{"text": "为什么记住？"}]}
    storyboard = {"scenes": [{"visual_template": "hook_big_claim"}]}
    report = build_viral_quality_report(
        project_id="dim_test",
        project_dir=tmp_path,
        narration_plan=plan,
        storyboard=storyboard,
    )
    assert isinstance(report["passed_dimensions"], list)
    assert isinstance(report["failed_dimensions"], list)
    assert len(report["passed_dimensions"]) + len(report["failed_dimensions"]) == 6


# ─── End-to-end on real demo data ───

def test_real_demo_v3_preview_evaluates_against_real_artifacts():
    project_dir = Path("/Users/muzi/video-director-v3/outputs/demo_v3_preview")
    if not (project_dir / "narration_plan.json").exists():
        # Skip if real preview hasn't been generated yet
        return
    narration_plan = json.loads((project_dir / "narration_plan.json").read_text(encoding="utf-8"))
    storyboard = json.loads((project_dir / "motion_storyboard.json").read_text(encoding="utf-8"))
    sync_report_path = project_dir / "rendered_smoke" / "sync_report.json"
    if not sync_report_path.exists():
        # Sync reliability dimension will score 0; this is expected for fresh projects
        pass
    report = build_viral_quality_report(
        project_id="demo_v3_preview",
        project_dir=project_dir,
        narration_plan=narration_plan,
        storyboard=storyboard,
        sync_report_path=sync_report_path,
    )
    # Real demo is allowed to be FAIL — we only assert structure
    assert "status" in report
    assert report["total_score"] <= report["max_score"]
    # All 6 dimensions present
    assert set(report["dimensions"].keys()) == {
        "hook", "promise", "saveable_value", "comment_trigger",
        "visual_rhythm", "sync_reliability",
    }
