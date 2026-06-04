from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from video_director_v3.qa.semantic_quality_gate import build_semantic_quality_report


def _scene(
    scene_id: str,
    role: str,
    template_type: str,
    slots: dict,
    *,
    role_match: float = 1.0,
    slot_completeness: float = 1.0,
    readability_risk: float = 0.1,
) -> dict:
    return {
        "id": scene_id,
        "role": role,
        "template_type": template_type,
        "slots": slots,
        "semantic_score": {
            "role_match": role_match,
            "slot_completeness": slot_completeness,
            "visual_readability_risk": readability_risk,
        },
    }


def _write_preview_artifacts(tmp_path: Path, scenes: list[dict], *, contact_sheet: bool = True, fallback_ids: set[str] | None = None) -> None:
    review_dir = tmp_path / "review_frames"
    review_dir.mkdir(parents=True, exist_ok=True)
    if contact_sheet:
        (review_dir / "contact-sheet.jpg").write_bytes(b"fake")

    timeline_root = tmp_path / "hyperframes_timeline"
    timeline_dir = timeline_root / "data"
    timeline_dir.mkdir(parents=True, exist_ok=True)
    (timeline_root / "assets").mkdir(parents=True, exist_ok=True)
    (timeline_root / "meta.json").write_text(
        json.dumps(
            {
                "project": tmp_path.name,
                "project_id": tmp_path.name,
                "entry_point": "hyperframes_timeline/index.html",
                "entry_point_path": str(timeline_root / "index.html"),
                "audio_duration": 12.0,
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )
    (timeline_root / "index.html").write_text(
        """<!doctype html><html><body>
        <section data-duration=\"4.0\"></section>
        <section data-duration=\"4.0\"></section>
        <section data-duration=\"4.0\"></section>
        </body></html>""",
        encoding="utf-8",
    )
    (timeline_root / "assets" / "voiceover.mp3").write_bytes(b"fake")
    director_scenes = []
    for scene in scenes:
        director_scenes.append(
            {
                "id": scene["id"],
                "contract_template_id": scene["template_type"],
                "contract_source": "slots_only",
                "template_contract_status": "PASS",
                "template_contract_fallback_used": scene["id"] in (fallback_ids or set()),
            }
        )
    (timeline_dir / "director_timeline.json").write_text(
        json.dumps(
            {
                "scenes": director_scenes,
                "total_duration_sec": sum(float(scene.get("duration", 4.0) or 4.0) for scene in scenes),
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )


def _scene_pack(scenes: list[dict], *, contract_errors: list[str] | None = None) -> dict:
    return {
        "scenes": scenes,
        "lint": {
            "scene_pack_status": "PASS",
            "template_contracts_status": "PASS",
            "contract_errors": contract_errors or [],
        },
    }


def _report(tmp_path: Path, scenes: list[dict], *, contact_sheet: bool = True, fallback_ids: set[str] | None = None, contract_errors: list[str] | None = None, stage_status: dict[str, str] | None = None) -> dict:
    _write_preview_artifacts(tmp_path, scenes, contact_sheet=contact_sheet, fallback_ids=fallback_ids)
    return build_semantic_quality_report(
        project_dir=tmp_path,
        scene_pack=_scene_pack(scenes, contract_errors=contract_errors),
        review_frames_data={"status": "PASS", "ok_count": 7} if contact_sheet else {"status": "FAIL", "ok_count": 0},
        stage_status=stage_status or {"studio_native_preview": "PASS"},
    )


def test_score_never_exceeds_100_and_ready_band(tmp_path: Path):
    scenes = [
        _scene("S01", "hook", "hook", {
            "main_claim": "为什么很多人记了很多笔记，最后还是写不出来",
            "pain_point": "记了很多",
            "status_badge": "QUESTION",
            "visual_emphasis": "写不出来",
        }),
        _scene("S02", "problem", "problem_conflict", {
            "problem_title": "问题不是不努力，而是入口太散",
            "conflict_items": ["素材散", "路径散"],
            "consequence": "写的时候要重新拼",
            "warning_label": "ALERT",
        }),
        _scene("S03", "method", "method_steps", {
            "method_title": "先把入口收拢",
            "steps": ["统一入口", "建立索引", "直接调用"],
            "step_labels": ["1", "2", "3"],
            "final_result": "调用更快",
        }),
        _scene("S04", "proof", "case_study_card", {
            "case_title": "从 3 个入口收敛到 1 个",
            "situation": "以前入口散",
            "action": "先收拢再调用",
            "result": "检索更快",
            "lesson": "路径少了",
        }),
        _scene("S05", "offer", "framework_quadrant", {
            "framework_title": "四象限方法",
            "quadrants": ["输入", "组织", "调用", "输出"],
            "center_claim": "先做最小闭环",
            "usage_note": "按四步推进",
        }),
        _scene("S06", "verdict", "result_summary", {
            "result_title": "先可用，再优化",
            "key_results": ["流程闭环", "调用变快"],
            "final_verdict": "先跑通",
            "next_step": "继续扩展",
        }),
        _scene("S07", "method", "concept_layers", {
            "concept_title": "三层结构",
            "layers": ["收集", "组织", "调用"],
            "layer_descriptions": ["素材进库", "链接起来", "直接调用"],
            "conclusion": "每层各做一件事",
        }),
        _scene("S08", "cta", "final_cta", {
            "final_claim": "先跑通一个最小闭环，再谈扩展",
            "next_step": "先跑一遍",
            "cta_text": "现在开始",
            "avoid_phrases": ["空谈"],
        }),
    ]

    report = _report(tmp_path, scenes)

    assert report["semantic_quality_score"] <= 100
    assert report["score_band"] == "READY"
    assert report["publish_candidate_readiness"] == "READY"
    assert report["gate_status"] == "PASS"
    assert report["status"] == "PASS"


def test_score_band_review_for_structural_risk(tmp_path: Path):
    scenes = [
        _scene("S01", "hook", "hook", {
            "main_claim": "为什么很多人记了很多笔记，最后还是写不出来",
            "pain_point": "记了很多",
            "status_badge": "QUESTION",
            "visual_emphasis": "写不出来",
        }),
        _scene("S02", "cta", "final_cta", {
            "final_claim": "先收藏",
            "next_step": "先收藏",
            "cta_text": "现在开始",
            "avoid_phrases": ["空谈"],
        }),
        _scene("S03", "problem", "problem_conflict", {
            "problem_title": "问题不是不努力，而是入口太散",
            "conflict_items": ["素材散", "路径散"],
            "consequence": "写的时候要重新拼",
            "warning_label": "ALERT",
        }),
        _scene("S04", "proof", "proof", {
            "proof_title": "真实案例",
            "proof_items": ["真实案例", "已经跑通"],
            "metric_or_evidence": "真实案例",
            "credibility_note": "经验",
        }),
        _scene("S05", "method", "method_steps", {
            "method_title": "先把入口收拢",
            "steps": ["统一入口", "建立索引", "直接调用"],
            "step_labels": ["1", "2", "3"],
            "final_result": "调用更快",
        }),
        _scene("S06", "proof", "case_study_card", {
            "case_title": "从 3 个入口收敛到 1 个",
            "situation": "以前入口散",
            "action": "先收拢再调用",
            "result": "检索更快",
            "lesson": "路径少了",
        }),
        _scene("S07", "method", "concept_layers", {
            "concept_title": "三层结构",
            "layers": ["收集", "组织", "调用"],
            "layer_descriptions": ["素材进库", "链接起来", "直接调用"],
            "conclusion": "每层各做一件事",
        }),
        _scene("S08", "cta", "final_cta", {
            "final_claim": "先跑通一个最小闭环，再谈扩展",
            "next_step": "先跑一遍",
            "cta_text": "现在开始",
            "avoid_phrases": ["空谈"],
        }),
    ]

    report = _report(tmp_path, scenes)

    assert report["gate_status"] == "PASS"
    assert report["score_band"] == "REVIEW"
    assert report["publish_candidate_readiness"] in {"REVIEW", "NO_GO"}
    assert report["cta_distribution"]["early_cta_count"] > 0
    assert report["cta_distribution"]["cta_distribution_risk"] in {"medium", "high"}


def test_hard_fail_for_missing_proof_and_cta(tmp_path: Path):
    scenes = [
        _scene("S01", "hook", "hook", {
            "main_claim": "为什么很多人记了很多笔记，最后还是写不出来",
            "pain_point": "记了很多",
            "status_badge": "QUESTION",
            "visual_emphasis": "写不出来",
        }),
        _scene("S02", "problem", "problem_conflict", {
            "problem_title": "问题不是不努力，而是入口太散",
            "conflict_items": ["素材散", "路径散"],
            "consequence": "写的时候要重新拼",
            "warning_label": "ALERT",
        }),
        _scene("S03", "method", "method_steps", {
            "method_title": "先把入口收拢",
            "steps": ["统一入口", "建立索引", "直接调用"],
            "step_labels": ["1", "2", "3"],
            "final_result": "调用更快",
        }),
    ]

    report = _report(tmp_path, scenes)

    assert report["gate_status"] == "FAIL"
    assert report["score_band"] == "FAIL"
    assert report["publish_candidate_readiness"] == "NO_GO"
    assert any("proof_scene_count = 0" == reason for reason in report["hard_fail_reasons"])
    assert any("cta_scene_count = 0" == reason for reason in report["hard_fail_reasons"])


def test_early_cta_detection(tmp_path: Path):
    scenes = [
        _scene("S01", "hook", "hook", {
            "main_claim": "为什么很多人记了很多笔记，最后还是写不出来",
            "pain_point": "记了很多",
            "status_badge": "QUESTION",
            "visual_emphasis": "写不出来",
        }),
        _scene("S02", "cta", "final_cta", {
            "final_claim": "先收藏",
            "next_step": "先收藏",
            "cta_text": "现在开始",
            "avoid_phrases": ["空谈"],
        }),
        _scene("S03", "problem", "problem_conflict", {
            "problem_title": "问题不是不努力，而是入口太散",
            "conflict_items": ["素材散", "路径散"],
            "consequence": "写的时候要重新拼",
            "warning_label": "ALERT",
        }),
        _scene("S04", "proof", "proof", {
            "proof_title": "真实案例",
            "proof_items": ["真实案例", "已经跑通"],
            "metric_or_evidence": "真实案例",
            "credibility_note": "经验",
        }),
        _scene("S05", "method", "method_steps", {
            "method_title": "先把入口收拢",
            "steps": ["统一入口", "建立索引", "直接调用"],
            "step_labels": ["1", "2", "3"],
            "final_result": "调用更快",
        }),
        _scene("S06", "proof", "case_study_card", {
            "case_title": "从 3 个入口收敛到 1 个",
            "situation": "以前入口散",
            "action": "先收拢再调用",
            "result": "检索更快",
            "lesson": "路径少了",
        }),
        _scene("S07", "method", "concept_layers", {
            "concept_title": "三层结构",
            "layers": ["收集", "组织", "调用"],
            "layer_descriptions": ["素材进库", "链接起来", "直接调用"],
            "conclusion": "每层各做一件事",
        }),
        _scene("S08", "cta", "final_cta", {
            "final_claim": "先跑通一个最小闭环，再谈扩展",
            "next_step": "先跑一遍",
            "cta_text": "现在开始",
            "avoid_phrases": ["空谈"],
        }),
    ]

    report = _report(tmp_path, scenes)

    assert report["cta_distribution"]["early_cta_count"] > 0
    assert report["cta_distribution"]["cta_distribution_risk"] in {"medium", "high"}
    assert any("early_cta" in item["structural_risks"] for item in report["worst_3_scenes"])


def test_repeated_cta_detection_and_high_risk(tmp_path: Path):
    scenes = [
        _scene("S01", "hook", "hook", {
            "main_claim": "为什么很多人记了很多笔记，最后还是写不出来",
            "pain_point": "记了很多",
            "status_badge": "QUESTION",
            "visual_emphasis": "写不出来",
        }),
        _scene("S02", "cta", "final_cta", {"final_claim": "先收藏", "next_step": "先收藏", "cta_text": "现在开始", "avoid_phrases": ["空谈"]}),
        _scene("S03", "problem", "problem_conflict", {"problem_title": "问题不是不努力，而是入口太散", "conflict_items": ["素材散"], "consequence": "写的时候要重新拼", "warning_label": "ALERT"}),
        _scene("S04", "cta", "final_cta", {"final_claim": "先收藏", "next_step": "先收藏", "cta_text": "现在开始", "avoid_phrases": ["空谈"]}),
        _scene("S05", "proof", "proof", {"proof_title": "真实案例", "proof_items": ["真实案例", "已经跑通"], "metric_or_evidence": "真实案例", "credibility_note": "经验"}),
        _scene("S06", "cta", "final_cta", {"final_claim": "先收藏", "next_step": "先收藏", "cta_text": "现在开始", "avoid_phrases": ["空谈"]}),
        _scene("S07", "method", "method_steps", {"method_title": "先把入口收拢", "steps": ["统一入口", "建立索引", "直接调用"], "step_labels": ["1", "2", "3"], "final_result": "调用更快"}),
        _scene("S08", "cta", "final_cta", {"final_claim": "先跑通一个最小闭环，再谈扩展", "next_step": "先跑一遍", "cta_text": "现在开始", "avoid_phrases": ["空谈"]}),
    ]

    report = _report(tmp_path, scenes)

    assert report["cta_distribution"]["cta_scene_count"] == 4
    assert report["cta_distribution"]["repeated_cta_count"] >= 3
    assert report["cta_distribution"]["cta_distribution_risk"] == "high"
    assert report["publish_candidate_readiness"] == "NO_GO"


def test_abstract_proof_detection(tmp_path: Path):
    scenes = [
        _scene("S01", "hook", "hook", {
            "main_claim": "为什么很多人记了很多笔记，最后还是写不出来",
            "pain_point": "记了很多",
            "status_badge": "QUESTION",
            "visual_emphasis": "写不出来",
        }),
        _scene("S02", "problem", "problem_conflict", {
            "problem_title": "问题不是不努力，而是入口太散",
            "conflict_items": ["素材散", "路径散"],
            "consequence": "写的时候要重新拼",
            "warning_label": "ALERT",
        }),
        _scene("S03", "proof", "proof", {
            "proof_title": "真实案例",
            "proof_items": ["真实案例", "已经跑通", "可复用"],
            "metric_or_evidence": "经验",
            "credibility_note": "结果看得见",
        }),
        _scene("S04", "cta", "final_cta", {
            "final_claim": "先跑通一个最小闭环，再谈扩展",
            "next_step": "先跑一遍",
            "cta_text": "现在开始",
            "avoid_phrases": ["空谈"],
        }),
    ]

    report = _report(tmp_path, scenes)

    assert report["proof_strength"]["abstract_proof_count"] == 1
    assert report["proof_strength"]["proof_strength_risk"] in {"medium", "high"}
    assert any("abstract_proof" in item["structural_risks"] for item in report["worst_3_scenes"])


def test_repeated_role_and_template_detection(tmp_path: Path):
    scenes = [
        _scene("S01", "hook", "hook", {
            "main_claim": "为什么很多人记了很多笔记，最后还是写不出来",
            "pain_point": "记了很多",
            "status_badge": "QUESTION",
            "visual_emphasis": "写不出来",
        }),
        _scene("S02", "problem", "problem_conflict", {"problem_title": "问题不是不努力，而是入口太散", "conflict_items": ["素材散"], "consequence": "写的时候要重新拼", "warning_label": "ALERT"}),
        _scene("S03", "problem", "problem_conflict", {"problem_title": "问题不是不努力，而是入口太散", "conflict_items": ["素材散"], "consequence": "写的时候要重新拼", "warning_label": "ALERT"}),
        _scene("S04", "problem", "problem_conflict", {"problem_title": "问题不是不努力，而是入口太散", "conflict_items": ["素材散"], "consequence": "写的时候要重新拼", "warning_label": "ALERT"}),
        _scene("S05", "proof", "proof", {"proof_title": "真实案例", "proof_items": ["真实案例", "已经跑通"], "metric_or_evidence": "真实案例", "credibility_note": "经验"}),
        _scene("S06", "cta", "final_cta", {"final_claim": "先跑通一个最小闭环，再谈扩展", "next_step": "先跑一遍", "cta_text": "现在开始", "avoid_phrases": ["空谈"]}),
    ]

    report = _report(tmp_path, scenes)

    assert report["scene_repetition"]["repeated_role_runs"] >= 2
    assert report["scene_repetition"]["repeated_template_runs"] >= 2
    assert report["scene_repetition"]["repetition_risk"] == "high"
    assert any("repeated_role" in item["structural_risks"] or "repeated_template" in item["structural_risks"] for item in report["worst_3_scenes"])


def test_weak_hook_detection(tmp_path: Path):
    scenes = [
        _scene("S01", "hook", "hook", {
            "main_claim": "开始流程",
            "pain_point": "开始",
            "status_badge": "INFO",
            "visual_emphasis": "流程",
        }),
        _scene("S02", "problem", "problem_conflict", {"problem_title": "问题不是不努力，而是入口太散", "conflict_items": ["素材散"], "consequence": "写的时候要重新拼", "warning_label": "ALERT"}),
        _scene("S03", "proof", "proof", {"proof_title": "真实案例", "proof_items": ["真实案例", "已经跑通"], "metric_or_evidence": "真实案例", "credibility_note": "经验"}),
        _scene("S04", "cta", "final_cta", {"final_claim": "先跑通一个最小闭环，再谈扩展", "next_step": "先跑一遍", "cta_text": "现在开始", "avoid_phrases": ["空谈"]}),
    ]

    report = _report(tmp_path, scenes)

    assert report["hook_strength"]["hook_strength_risk"] == "high"
    assert report["hook_strength"]["hook_scene_id"] == "S01"
    assert any("weak_hook" in item["structural_risks"] for item in report["worst_3_scenes"])


def test_preview_load_report_passes_with_complete_artifacts(tmp_path: Path):
    from video_director_v3.qa.semantic_quality_gate import build_preview_load_report

    scenes = [
        _scene("S01", "hook", "hook", {
            "main_claim": "先跑通",
            "pain_point": "别再囤工具",
            "status_badge": "QUESTION",
            "visual_emphasis": "闭环",
        }),
        _scene("S02", "proof", "proof", {
            "proof_title": "结果更稳",
            "proof_items": ["资料可复用", "过程可验证"],
            "metric_or_evidence": "真实案例",
            "credibility_note": "已经跑通",
        }),
        _scene("S03", "cta", "final_cta", {
            "final_claim": "现在开始",
            "next_step": "先完成最小闭环",
            "cta_text": "先跑一遍",
            "avoid_phrases": ["空谈"],
        }),
    ]
    _write_preview_artifacts(tmp_path, scenes)
    report = build_preview_load_report(tmp_path)
    assert report["status"] == "PASS"
    assert report["preview_load_status"] == "PASS"
    assert report["index_duration"] > 0
    assert report["timeline_scene_count"] == 3


def test_preview_load_report_fails_on_zero_duration(tmp_path: Path):
    from video_director_v3.qa.semantic_quality_gate import build_preview_load_report

    timeline_root = tmp_path / "hyperframes_timeline"
    timeline_data_dir = timeline_root / "data"
    timeline_data_dir.mkdir(parents=True, exist_ok=True)
    (timeline_root / "assets").mkdir(parents=True, exist_ok=True)
    (timeline_root / "meta.json").write_text(
        json.dumps(
            {
                "project": tmp_path.name,
                "project_id": tmp_path.name,
                "entry_point": "hyperframes_timeline/index.html",
                "entry_point_path": str(timeline_root / "index.html"),
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )
    (timeline_root / "index.html").write_text(
        "<html><body><section data-duration=\"0\"></section></body></html>",
        encoding="utf-8",
    )
    (timeline_root / "assets" / "voiceover.mp3").write_bytes(b"fake")
    (timeline_data_dir / "director_timeline.json").write_text(
        json.dumps({"scenes": [{"id": "S01"}], "total_duration_sec": 4.0}, ensure_ascii=False),
        encoding="utf-8",
    )
    report = build_preview_load_report(tmp_path)
    assert report["status"] == "FAIL"
    assert "index duration is zero" in report["hard_fail_reasons"]


def test_layout_fit_gate_detects_off_canvas_and_caption_overlap(tmp_path: Path):
    scenes = [
        _scene("S01", "hook", "hook", {
            "main_claim": "先跑通",
            "pain_point": "别再囤工具",
            "status_badge": "QUESTION",
            "visual_emphasis": "闭环",
        }),
        _scene("S02", "proof", "proof", {
            "proof_title": "结果更稳",
            "proof_items": ["资料可复用", "过程可验证"],
            "metric_or_evidence": "真实案例",
            "credibility_note": "已经跑通",
        }),
        _scene("S03", "cta", "final_cta", {
            "final_claim": "现在开始",
            "next_step": "先完成最小闭环",
            "cta_text": "先跑一遍",
            "avoid_phrases": ["空谈"],
        }),
    ]
    for scene in scenes:
        scene["layout_box"] = {
            "main_top": 120,
            "main_bottom": 120,
            "support_top": 70,
            "support_bottom": 1600,
            "center_y": 1400,
            "caption_top": 1200,
            "header_bottom": 260,
            "support_cards": [{"x": -20, "y": 80, "w": 320, "h": 180}],
        }

    report = _report(tmp_path, scenes)
    assert report["layout_fit"]["layout_fit_status"] == "FAIL"
    assert any(
        "layout fit gate failed" == reason or "off-canvas support card detected" in reason
        for reason in report["hard_fail_reasons"]
    )


def test_missing_proof_is_hard_fail(tmp_path: Path):
    scenes = [
        _scene("S01", "hook", "hook", {
            "main_claim": "为什么很多人记了很多笔记，最后还是写不出来",
            "pain_point": "记了很多",
            "status_badge": "QUESTION",
            "visual_emphasis": "写不出来",
        }),
        _scene("S02", "problem", "problem_conflict", {"problem_title": "问题不是不努力，而是入口太散", "conflict_items": ["素材散"], "consequence": "写的时候要重新拼", "warning_label": "ALERT"}),
        _scene("S03", "cta", "final_cta", {"final_claim": "先跑通一个最小闭环，再谈扩展", "next_step": "先跑一遍", "cta_text": "现在开始", "avoid_phrases": ["空谈"]}),
    ]

    report = _report(tmp_path, scenes)

    assert report["gate_status"] == "FAIL"
    assert report["score_band"] == "FAIL"
    assert report["publish_candidate_readiness"] == "NO_GO"
    assert any("proof_scene_count = 0" == reason for reason in report["hard_fail_reasons"])


def test_missing_cta_is_hard_fail(tmp_path: Path):
    scenes = [
        _scene("S01", "hook", "hook", {
            "main_claim": "为什么很多人记了很多笔记，最后还是写不出来",
            "pain_point": "记了很多",
            "status_badge": "QUESTION",
            "visual_emphasis": "写不出来",
        }),
        _scene("S02", "problem", "problem_conflict", {"problem_title": "问题不是不努力，而是入口太散", "conflict_items": ["素材散"], "consequence": "写的时候要重新拼", "warning_label": "ALERT"}),
        _scene("S03", "proof", "proof", {"proof_title": "真实案例", "proof_items": ["真实案例", "已经跑通"], "metric_or_evidence": "真实案例", "credibility_note": "经验"}),
    ]

    report = _report(tmp_path, scenes)

    assert report["gate_status"] == "FAIL"
    assert report["score_band"] == "FAIL"
    assert report["publish_candidate_readiness"] == "NO_GO"
    assert any("cta_scene_count = 0" == reason for reason in report["hard_fail_reasons"])


def test_missing_contact_sheet_is_hard_fail(tmp_path: Path):
    scenes = [
        _scene("S01", "hook", "hook", {
            "main_claim": "为什么很多人记了很多笔记，最后还是写不出来",
            "pain_point": "记了很多",
            "status_badge": "QUESTION",
            "visual_emphasis": "写不出来",
        }),
        _scene("S02", "problem", "problem_conflict", {"problem_title": "问题不是不努力，而是入口太散", "conflict_items": ["素材散"], "consequence": "写的时候要重新拼", "warning_label": "ALERT"}),
        _scene("S03", "proof", "proof", {"proof_title": "真实案例", "proof_items": ["真实案例", "已经跑通"], "metric_or_evidence": "真实案例", "credibility_note": "经验"}),
        _scene("S04", "cta", "final_cta", {"final_claim": "先跑通一个最小闭环，再谈扩展", "next_step": "先跑一遍", "cta_text": "现在开始", "avoid_phrases": ["空谈"]}),
    ]

    _write_preview_artifacts(tmp_path, scenes, contact_sheet=False)
    report = build_semantic_quality_report(
        project_dir=tmp_path,
        scene_pack=_scene_pack(scenes),
        review_frames_data={"status": "FAIL", "ok_count": 0},
        stage_status={"studio_native_preview": "PASS"},
    )

    assert report["gate_status"] == "FAIL"
    assert any("contact sheet missing" == reason for reason in report["hard_fail_reasons"])


def test_layout_density_gate_detects_overflow_and_repeated_family(tmp_path: Path):
    scenes = [
        _scene("V01", "method", "tool_stack", {
            "stack_title": "工具栈",
            "tools": ["Obsidian", "Claude", "Hermes"],
            "tool_roles": ["存储", "整理", "复盘"],
            "workflow_result": "把工具接成线",
        }),
        _scene("V02", "method", "tool_stack", {
            "stack_title": "工具栈",
            "tools": ["Obsidian", "Claude", "Hermes"],
            "tool_roles": ["存储", "整理", "复盘"],
            "workflow_result": "把工具接成线",
        }),
        _scene("V03", "method", "tool_stack", {
            "stack_title": "工具栈",
            "tools": ["Obsidian", "Claude", "Hermes"],
            "tool_roles": ["存储", "整理", "复盘"],
            "workflow_result": "把工具接成线",
        }),
        _scene("V04", "cta", "final_cta", {
            "final_claim": "现在开始",
            "next_step": "先跑一遍",
            "cta_text": "现在开始",
            "avoid_phrases": ["空谈"],
        }),
    ]
    for scene in scenes:
        scene["layout_family"] = "tool_pipeline"
        scene["layout_variant"] = "stack"
        scene["content_item_count"] = 7
        scene["content_item_limit"] = 6

    report = _report(tmp_path, scenes)

    assert report["layout_density"]["density_overflow_count"] == 4
    assert report["layout_density"]["repeated_layout_family_run_count"] >= 1
    assert any("layout_density_overflow" in reason or "layout_family repeated" in reason for reason in report["hard_fail_reasons"])
