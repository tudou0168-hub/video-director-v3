from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from video_director_v3.director.cta_policy import (
    load_default_cta_policy,
    validate_cta_policy,
)
from video_director_v3.director.offer_profile import (
    load_default_offer_profile,
    validate_offer_profile,
)
from video_director_v3.director.proof_asset import (
    load_default_proof_asset,
    validate_proof_asset,
)
from video_director_v3.director.semantic_planner import build_scene_pack
from video_director_v3.director.scene_pack_schema import validate_scene_pack
from video_director_v3.qa.semantic_quality_gate import build_semantic_quality_report


def _write_review_artifacts(tmp_path: Path, *, ok_count: int = 7) -> None:
    review_dir = tmp_path / "review_frames"
    review_dir.mkdir(parents=True, exist_ok=True)
    (review_dir / "contact-sheet.jpg").write_bytes(b"fake")

    timeline_dir = tmp_path / "hyperframes_timeline" / "data"
    timeline_dir.mkdir(parents=True, exist_ok=True)
    (timeline_dir / "director_timeline.json").write_text(
        json.dumps({"scenes": []}, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def _base_scene(scene_id: str, role: str, template_type: str, voiceover: str, slots: dict[str, object]) -> dict[str, object]:
    return {
        "id": scene_id,
        "role": role,
        "intent": "test_intent",
        "duration": 4.0,
        "voiceover": voiceover,
        "display_headline": voiceover[:12] or scene_id,
        "display_subtitle": voiceover[:24] or scene_id,
        "template_type": template_type,
        "slots": slots,
        "qa_rules": {
            "headline_max_chars": 32,
            "requires_voiceover": True,
            "requires_slots": True,
            "no_placeholder_slots": True,
            "chinese_first": True,
        },
        "semantic_score": {
            "role_match": 1.0,
            "slot_completeness": 1.0,
            "visual_readability_risk": 0.1,
            "cta_presence": 1.0 if role == "cta" or template_type == "final_cta" else 0.0,
            "proof_presence": 1.0 if role == "proof" or template_type in {"proof", "case_study_card"} else 0.0,
        },
    }


def test_offer_proof_cta_contract_assets_load_and_validate():
    offer = load_default_offer_profile()
    proof = load_default_proof_asset()
    cta = load_default_cta_policy()

    assert offer.profile_id == "default_ai_content_system"
    assert proof.asset_id == "default_ai_content_system_proof"
    assert cta.policy_id == "default_value_first"
    assert "评论区打关键词领取资料" in cta.forbidden_phrases

    assert validate_offer_profile(offer.as_dict()) == []
    assert validate_proof_asset(proof.as_dict()) == []
    assert validate_cta_policy(cta.as_dict()) == []


def test_scene_pack_optional_contract_extensions_are_emitted_for_sales_like_storyboard():
    storyboard = {
        "scenes": [
            {
                "scene_id": "S01",
                "role": "hook",
                "duration": 4.0,
                "narration": "为什么很多人记了很多笔记，最后还是写不出来？",
                "visual_template": "hook_big_claim",
            },
            {
                "scene_id": "S02",
                "role": "proof",
                "duration": 5.0,
                "narration": "以前素材分散，现在可以直接调用已有素材包。",
                "visual_template": "case_study_card",
            },
            {
                "scene_id": "S03",
                "role": "cta",
                "duration": 4.0,
                "narration": "现在开始",
                "visual_template": "checklist_cta",
            },
        ]
    }

    scene_pack = build_scene_pack(
        project_id="sales_contract_refs",
        narration_plan={"sentence_list": []},
        storyboard=storyboard,
        audio_timeline={"sentence_timings": []},
    )

    assert scene_pack["lint"]["status"] == "PASS"
    assert validate_scene_pack(scene_pack) == []

    proof_scene = next(scene for scene in scene_pack["scenes"] if scene["role"] == "proof")
    cta_scene = scene_pack["scenes"][-1]

    assert proof_scene["proof_asset_ref"] == "default_ai_content_system_proof"
    assert proof_scene["slots"]["metric_or_evidence"] != "真实案例"
    assert cta_scene["offer_profile_ref"] == "default_ai_content_system"
    assert cta_scene["cta_policy_ref"] == "default_value_first"
    assert cta_scene["cta_stage"] == "final"
    assert cta_scene["cta_strength"] == "strong"
    assert cta_scene["slots"]["cta_text"] == "先跑一版最小成交流程"


def test_quality_gate_rejects_forbidden_cta_phrase(tmp_path: Path):
    _write_review_artifacts(tmp_path)
    scenes = [
        _base_scene(
            "S01",
            "hook",
            "hook",
            "为什么很多人记了很多笔记，最后还是写不出来？",
            {
                "main_claim": "为什么很多人记了很多笔记，最后还是写不出来？",
                "pain_point": "记了很多却写不出来",
                "status_badge": "QUESTION",
                "visual_emphasis": "写不出来",
            },
        ),
        _base_scene(
            "S02",
            "proof",
            "proof",
            "以前入口分散，现在可以直接调用已有素材包。",
            {
                "proof_title": "前后对比",
                "proof_items": ["前后对比", "执行记录"],
                "metric_or_evidence": "前后对比",
                "credibility_note": "有执行记录",
            },
        ),
        _base_scene(
            "S03",
            "cta",
            "final_cta",
            "评论区打关键词领取资料",
            {
                "final_claim": "先跑通一个最小闭环，再继续优化",
                "next_step": "先跑一版最小成交流程",
                "cta_text": "评论区打关键词领取资料",
                "avoid_phrases": ["空谈"],
            },
        ),
    ]
    scenes[0]["offer_profile_ref"] = "default_ai_content_system"
    scenes[1]["proof_asset_ref"] = "default_ai_content_system_proof"
    scenes[2]["offer_profile_ref"] = "default_ai_content_system"
    scenes[2]["cta_policy_ref"] = "default_value_first"
    scenes[2]["cta_stage"] = "final"
    scenes[2]["cta_strength"] = "strong"

    scene_pack = {
        "version": "v0.1-dry-run",
        "project_id": "forbidden_cta",
        "contract": "V3 semantic director -> HyperFrames native preview",
        "status": "dry_run",
        "scenes": scenes,
        "lint": {"scene_pack_status": "PASS", "template_contracts_status": "PASS", "contract_errors": []},
    }

    report = build_semantic_quality_report(
        project_dir=tmp_path,
        scene_pack=scene_pack,
        review_frames_data={"status": "PASS", "ok_count": 7},
        stage_status={"studio_native_preview": "PASS"},
    )

    assert report["gate_status"] == "FAIL"
    assert any("forbidden CTA phrase detected" in reason for reason in report["hard_fail_reasons"])
    assert report["cta_policy"]["forbidden_cta_count"] == 1


def test_quality_gate_rejects_fake_proof_metric(tmp_path: Path):
    _write_review_artifacts(tmp_path)
    scenes = [
        _base_scene(
            "S01",
            "hook",
            "hook",
            "为什么很多人记了很多笔记，最后还是写不出来？",
            {
                "main_claim": "为什么很多人记了很多笔记，最后还是写不出来？",
                "pain_point": "记了很多却写不出来",
                "status_badge": "QUESTION",
                "visual_emphasis": "写不出来",
            },
        ),
        _base_scene(
            "S02",
            "proof",
            "proof",
            "以前入口分散，现在可以直接调用已有素材包。",
            {
                "proof_title": "前后对比",
                "proof_items": ["前后对比", "执行记录"],
                "metric_or_evidence": "1000%",
                "credibility_note": "有执行记录",
            },
        ),
        _base_scene(
            "S03",
            "cta",
            "final_cta",
            "先开始",
            {
                "final_claim": "先跑通一个最小闭环，再继续优化",
                "next_step": "先跑一版最小成交流程",
                "cta_text": "先开始",
                "avoid_phrases": ["空谈"],
            },
        ),
    ]
    scenes[0]["offer_profile_ref"] = "default_ai_content_system"
    scenes[1]["proof_asset_ref"] = "default_ai_content_system_proof"
    scenes[2]["offer_profile_ref"] = "default_ai_content_system"
    scenes[2]["cta_policy_ref"] = "default_value_first"
    scenes[2]["cta_stage"] = "final"
    scenes[2]["cta_strength"] = "strong"

    scene_pack = {
        "version": "v0.1-dry-run",
        "project_id": "fake_metric",
        "contract": "V3 semantic director -> HyperFrames native preview",
        "status": "dry_run",
        "scenes": scenes,
        "lint": {"scene_pack_status": "PASS", "template_contracts_status": "PASS", "contract_errors": []},
    }

    report = build_semantic_quality_report(
        project_dir=tmp_path,
        scene_pack=scene_pack,
        review_frames_data={"status": "PASS", "ok_count": 7},
        stage_status={"studio_native_preview": "PASS"},
    )

    assert report["gate_status"] == "FAIL"
    assert any("fake proof metric detected" in reason for reason in report["hard_fail_reasons"])
    assert report["proof_asset"]["fake_metric_count"] == 1

