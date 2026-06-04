from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from video_director_v3.director.semantic_planner import build_scene_pack
from video_director_v3.director.scene_pack_schema import validate_scene_pack
from video_director_v3.director.visual_strategy import (
    build_visual_strategy_pack,
    build_visual_headline,
    detect_video_type,
    headline_compact,
    choose_layout_family,
    choose_visual_object,
    title_caption_similarity,
)
from video_director_v3.qa.semantic_quality_gate import build_semantic_quality_report
from video_director_v3.renderers.hyperframes.publish_templates import get_scene_body


def _storyboard(scene_specs: list[tuple[str, str, str]]) -> dict:
    scenes = []
    for idx, (scene_id, role, narration) in enumerate(scene_specs):
        scenes.append(
            {
                "scene_id": scene_id,
                "role": role,
                "duration": 4.0,
                "narration": narration,
                "visual_template": "hook_big_claim" if idx == 0 else "checklist_cta",
            }
        )
    return {"scenes": scenes}


def test_visual_strategy_detects_three_content_types():
    knowledge_text = "Obsidian 第二大脑 方法 框架 认知 流程 闭环 知识 结构"
    toolflow_text = "Claude Codex Hermes 工具 流程 自动化 工作流 安装 配置 技能"
    sales_text = "成交 客户 服务 咨询 课程 付费 购买 转化 复购 方案"

    assert detect_video_type(knowledge_text, title="知识工作者效率指南") == "knowledge_method"
    assert detect_video_type(toolflow_text, title="工具系统搭建") == "ai_toolflow"
    assert detect_video_type(sales_text, title="成交系统") == "sales_offer"

    knowledge_pack = build_visual_strategy_pack(text=knowledge_text, title="知识工作者效率指南")
    toolflow_pack = build_visual_strategy_pack(text=toolflow_text, title="工具系统搭建")
    sales_pack = build_visual_strategy_pack(text=sales_text, title="成交系统")

    assert knowledge_pack["strategy_id"] != toolflow_pack["strategy_id"] != sales_pack["strategy_id"]
    assert knowledge_pack["ending_variant"] == "insight_close"
    assert toolflow_pack["ending_variant"] == "checklist_close"
    assert sales_pack["ending_variant"] == "offer_close"
    assert knowledge_pack["layout_families"]
    assert toolflow_pack["visual_objects"]
    assert sales_pack["memory_anchor"]
    assert "save_reason" in knowledge_pack
    assert knowledge_pack["memory_anchor_policy"]
    assert toolflow_pack["visual_object_policy"]
    assert sales_pack["save_reason_policy"]


def test_sales_strategy_uses_concrete_memory_anchor_fallback():
    pack = build_visual_strategy_pack(text="", title="成交系统")
    assert pack["video_type"] == "sales_offer"
    assert pack["memory_anchor"] == "先跑一版最小成交"


def test_scene_pack_exposes_visual_strategy_and_refs(tmp_path: Path):
    script = "\n".join(
        [
            "# 工具换来换去，累的还是你",
            "不是工具越多越高效，而是入口越乱越慢。",
            "先把 Obsidian、Claude 和 Hermes 接成一个入口，再跑一遍最小闭环。",
            "以前从零开始找素材，现在可以直接调用已有结构。",
            "最后，先开始一次真实执行。",
        ]
    )
    storyboard = _storyboard(
        [
            ("S01", "hook", "不是工具越多越高效，而是入口越乱越慢。"),
            ("S02", "method", "先把 Obsidian、Claude 和 Hermes 接成一个入口，再跑一遍最小闭环。"),
            ("S03", "proof", "以前从零开始找素材，现在可以直接调用已有结构。"),
            ("S04", "cta", "最后，先开始一次真实执行。"),
        ]
    )
    scene_pack = build_scene_pack(
        project_id="p41b_visual_strategy",
        narration_plan={"title": "工具系统搭建", "sentence_list": []},
        storyboard=storyboard,
        audio_timeline={"sentence_timings": []},
        source_text=script,
    )

    assert scene_pack["video_type"] == "ai_toolflow"
    assert scene_pack["visual_strategy_id"]
    assert scene_pack["template_sequence_signature"]
    assert scene_pack["opening_variant"] in {"process_hook", "contrast_hook", "result_hook"}
    assert scene_pack["ending_variant"] == "checklist_close"
    assert validate_scene_pack(scene_pack) == []

    first_scene = scene_pack["scenes"][0]
    last_scene = scene_pack["scenes"][-1]
    assert first_scene["caption_mode"]
    assert first_scene["visual_role"].startswith("ai_toolflow:")
    assert first_scene["sequence_slot"] == "opening"
    assert first_scene["headline_compact"]
    assert first_scene["visual_headline"]
    assert first_scene["layout_family"]
    assert first_scene["visual_object"]
    assert first_scene["memory_anchor"]
    assert first_scene["save_reason"]
    assert 0.0 <= first_scene["title_caption_similarity"] <= 1.0
    assert 0.0 <= first_scene["readability_risk"] <= 1.0
    assert last_scene["cta_stage"] == "final"
    assert last_scene["cta_policy_ref"]
    assert last_scene["offer_profile_ref"]
    assert last_scene["cta_strength"] == "strong"
    assert last_scene["ending_variant"] in {"checklist_close", "action_close", "offer_close", "insight_close", "homework_close"}
    assert last_scene["layout_family"]


def test_visual_strategy_quality_metrics_exist_and_track_readability(tmp_path: Path):
    script = "成交 客户 服务 咨询 课程 付费 购买 转化 复购 方案"
    storyboard = _storyboard(
        [
            ("S01", "hook", "你是不是也遇到过，工具越换越累？"),
            ("S02", "problem", "问题不是工具少，而是动作没接上。"),
            ("S03", "proof", "以前每次都从零开始，现在可以直接拿到一版结构。"),
            ("S04", "cta", "最后，先跑通这一遍。"),
        ]
    )
    scene_pack = build_scene_pack(
        project_id="p41b_sales_visual",
        narration_plan={"title": "成交系统", "sentence_list": []},
        storyboard=storyboard,
        audio_timeline={"sentence_timings": []},
        source_text=script,
    )

    review_dir = tmp_path / "review_frames"
    review_dir.mkdir(parents=True, exist_ok=True)
    (review_dir / "contact-sheet.jpg").write_bytes(b"fake")
    timeline_dir = tmp_path / "hyperframes_timeline" / "data"
    timeline_dir.mkdir(parents=True, exist_ok=True)
    (timeline_dir / "director_timeline.json").write_text(
        json.dumps(
            {
                "scenes": [
                    {
                        "id": scene["id"],
                        "contract_template_id": scene["template_type"],
                        "contract_source": "slots_only",
                        "template_contract_status": "PASS",
                        "template_contract_fallback_used": False,
                        "caption_mode": scene.get("caption_mode"),
                        "layout_band": scene.get("layout_band"),
                        "headline_compact": scene.get("headline_compact"),
                        "title_caption_similarity": scene.get("title_caption_similarity"),
                        "readability_risk": scene.get("readability_risk"),
                    }
                    for scene in scene_pack["scenes"]
                ]
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    report = build_semantic_quality_report(
        project_dir=tmp_path,
        scene_pack=scene_pack,
        review_frames_data={"status": "PASS", "ok_count": 7},
        stage_status={"studio_native_preview": "PASS"},
    )

    assert report["visual_strategy"]["video_type"] == "sales_offer"
    assert report["visual_strategy"]["template_sequence"]
    assert report["visual_strategy"]["differentiation_score"] >= 0
    assert report["visual_strategy"]["layout_readability_score"] >= 0
    assert "caption_conflict_count" in report["visual_strategy"]
    assert "title_caption_overlap_risk" in report["visual_strategy"]
    assert "repeated_opening_risk" in report["visual_strategy"]
    assert "repeated_ending_risk" in report["visual_strategy"]
    assert "template_repetition_risk" in report["visual_strategy"]
    assert "same_video_risk" in report["visual_strategy"]
    assert "memory_anchor_missing_count" in report["visual_strategy"]
    assert "visual_object_missing_count" in report["visual_strategy"]
    assert "save_reason_missing_count" in report["visual_strategy"]
    assert report["contact_sheet_exists"] is True


def test_headline_compaction_and_overlap_de_duplication():
    headline = headline_compact(
        "工具越换越累，入口越散越乱，最后还是得回到一个统一的动作闭环",
        video_type="ai_toolflow",
        role="hook",
        template_type="hook",
    )
    caption = "工具越换越累，入口越散越乱，最后还是得回到一个统一的动作闭环"
    similarity = title_caption_similarity(headline, caption)

    assert len(headline) <= 16
    assert 0.0 <= similarity <= 1.0
    assert similarity < 1.0


def test_visual_headline_avoids_fragment_prefixes():
    headline = build_visual_headline(
        "我把 10 分钟定选题，先把工具链接起来再输出",
        video_type="ai_toolflow",
        role="hook",
        template_type="hook",
        memory_anchor="10分钟定选题",
    )
    assert not headline.startswith(("我把", "10", "以前的流程是"))
    assert len(headline) <= 16


def test_layout_family_and_visual_object_differ_by_content_type():
    knowledge_layout = choose_layout_family("knowledge_method", "hook", "hook", 0, 6, title="知识工作流", text="先看再做")
    toolflow_layout = choose_layout_family("ai_toolflow", "hook", "hook", 0, 6, title="工具工作流", text="输入整理调用输出")
    sales_layout = choose_layout_family("sales_offer", "hook", "hook", 0, 6, title="成交系统", text="数字增长")

    assert knowledge_layout != toolflow_layout != sales_layout
    assert choose_visual_object("knowledge_method", "proof", "case_study_card", text="知识图谱 文件树") in {"framework_map", "knowledge_graph", "file_tree"}
    assert choose_visual_object("ai_toolflow", "method", "tool_stack", text="settings.json Obsidian") in {"tool_pipeline", "config_panel", "file_tree"}
    assert choose_visual_object("sales_offer", "proof", "proof", text="300% 转化率") in {"proof_matrix", "metric_dashboard", "opportunity_map"}


def test_contract_renderer_wraps_strategy_classes():
    scene = {
        "id": "S01",
        "role": "hook",
        "template_type": "hook",
        "contract_template_id": "hook",
        "display_headline": "10 分钟定选题",
        "display_subtitle": "先把入口统一，再开始输出",
        "visual_headline": "10分钟定选题",
        "caption_mode": "emphasis_caption",
        "layout_family": "hero_metric",
        "visual_object": "metric_dashboard",
        "memory_anchor": "10分钟定选题",
        "save_reason": "收藏后下次直接复用",
        "ending_variant": "insight_close",
        "is_final_scene": True,
        "slots": {
            "main_claim": "10分钟定选题",
            "pain_point": "别让入口太散",
            "status_badge": "QUESTION",
            "visual_emphasis": "选题",
        },
    }

    body = get_scene_body("S01", "hook", scene)

    assert "vf-strategy-shell" in body
    assert "vf-layout-hero_metric" in body
    assert "vf-content-region" in body
    assert "vf-hook-region" in body
    assert 'data-debug-visual-strategy="false"' in body
    assert "vf-strategy-meta" not in body
    assert "vf-ending-board" in body
    assert "hf-status-stamp" in body


def test_contract_renderer_shows_strategy_meta_only_when_debug_enabled():
    scene = {
        "id": "S01",
        "role": "hook",
        "template_type": "hook",
        "contract_template_id": "hook",
        "display_headline": "10 分钟定选题",
        "display_subtitle": "先把入口统一，再开始输出",
        "visual_headline": "10分钟定选题",
        "caption_mode": "emphasis_caption",
        "layout_family": "hero_metric",
        "visual_object": "metric_dashboard",
        "memory_anchor": "10分钟定选题",
        "save_reason": "收藏后下次直接复用",
        "ending_variant": "insight_close",
        "is_final_scene": True,
        "debug_visual_strategy": True,
        "slots": {
            "main_claim": "10分钟定选题",
            "pain_point": "别让入口太散",
            "status_badge": "QUESTION",
            "visual_emphasis": "选题",
        },
    }

    body = get_scene_body("S01", "hook", scene)

    assert 'data-debug-visual-strategy="true"' in body
    assert "vf-strategy-meta" in body
    assert "LAYOUT FAMILY" in body


def test_contract_renderer_reuses_mature_hud_components():
    proof_scene = {
        "id": "S05",
        "role": "proof",
        "template_type": "proof",
        "contract_template_id": "proof",
        "display_headline": "真实可复用的结果",
        "display_subtitle": "把证据做成可被保存的判断",
        "caption_mode": "action_caption",
        "layout_family": "proof_matrix",
        "visual_object": "proof_matrix",
        "memory_anchor": "真实可复用的结果",
        "save_reason": "下次直接复用证据结构",
        "ending_variant": "",
        "slots": {
            "proof_title": "真实可复用的结果",
            "proof_items": ["案例 1", "案例 2"],
            "metric_or_evidence": "100% 可解释",
            "credibility_note": "这组证据来自可复用流程",
        },
    }

    cta_scene = {
        "id": "S06",
        "role": "cta",
        "template_type": "final_cta",
        "contract_template_id": "final_cta",
        "display_headline": "现在开始执行",
        "display_subtitle": "把入口收束起来",
        "caption_mode": "action_caption",
        "layout_family": "action_close",
        "visual_object": "checklist_board",
        "memory_anchor": "现在开始执行",
        "save_reason": "收束到下一步",
        "ending_variant": "action_close",
        "slots": {
            "final_claim": "现在开始执行",
            "next_step": "先跑一遍预览",
            "cta_text": "继续下一步",
            "avoid_phrases": ["评论区打关键词领取资料"],
        },
    }

    proof_body = get_scene_body("S05", "proof", proof_scene)
    cta_body = get_scene_body("S06", "cta", cta_scene)

    assert "hf-metric-card" in proof_body
    assert "hf-glass-panel" in proof_body
    assert "hf-status-stamp" in cta_body
    assert "hf-glass-panel" in cta_body
