"""Semantic scene_pack planner for contract-driven template rendering."""
from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

from video_director_v3.director.cta_policy import load_default_cta_policy
from video_director_v3.director.offer_profile import load_default_offer_profile
from video_director_v3.director.visual_strategy import (
    build_visual_strategy_pack,
    build_memory_anchor,
    build_save_reason,
    build_visual_headline,
    caption_mode_for_scene,
    choose_ending_variant,
    choose_opening_variant,
    choose_layout_family,
    choose_visual_object,
    headline_compact,
    layout_band_for_scene,
    sequence_slot_for_scene,
    template_sequence_signature,
    title_caption_similarity,
)
from video_director_v3.director.scene_pack_schema import (
    SCENE_PACK_VERSION,
    normalize_scene_role,
    validate_scene_pack,
)
from video_director_v3.director.proof_asset import load_default_proof_asset
from video_director_v3.director.template_contracts import lint_scene_pack_contracts


VISUAL_TEMPLATE_TO_CONTRACT = {
    "hook_big_claim": "hook",
    "broken_chain": "problem_conflict",
    "before_after_compare": "before_after",
    "checklist_cta": "final_cta",
    "step_ladder": "method_steps",
    "framework_quadrant": "framework_quadrant",
    "progress_tracker": "progress_tracker",
    "tool_stack": "tool_stack",
    "keyword_punchline": "keyword_punchline",
    "myth_bust": "myth_bust",
    "case_study_card": "case_study_card",
    "concept_layers": "concept_layers",
    "knowledge_graph": "knowledge_graph",
    "section_board": "result_summary",
}


def build_scene_pack(
    *,
    project_id: str,
    narration_plan: dict[str, Any],
    storyboard: dict[str, Any],
    audio_timeline: dict[str, Any] | None = None,
    source_text: str | None = None,
) -> dict[str, Any]:
    offer_profile = load_default_offer_profile()
    proof_asset = load_default_proof_asset()
    cta_policy = load_default_cta_policy()
    visual_strategy = build_visual_strategy_pack(
        text=_visual_strategy_text(source_text=source_text, narration_plan=narration_plan, storyboard=storyboard),
        title=str(narration_plan.get("title") or project_id),
        script_path=str(narration_plan.get("script_path") or ""),
    )
    video_type = str(visual_strategy.get("video_type") or "knowledge_method")
    opening_variant = str(visual_strategy.get("opening_variant") or choose_opening_variant(video_type, str(narration_plan.get("title") or project_id), source_text or ""))
    ending_variant = str(visual_strategy.get("ending_variant") or choose_ending_variant(video_type, title=str(narration_plan.get("title") or project_id), text=source_text or "", role="cta"))
    scenes = []
    all_scenes = storyboard.get("scenes", [])
    for index, scene in enumerate(all_scenes):
        voiceover = _scene_voiceover(scene, narration_plan, audio_timeline or {})
        role = _rebalance_scene_role(
            normalize_scene_role(scene.get("role", "method")),
            voiceover,
            index,
            len(all_scenes),
            scenes[-1]["role"] if scenes else "",
            video_type=video_type,
            total_scenes=len(all_scenes),
        )
        template_type = _template_type_for_scene(
            scene,
            role,
            index,
            len(all_scenes),
            video_type=video_type,
            opening_variant=opening_variant,
            ending_variant=ending_variant,
        )
        layout_family = choose_layout_family(
            video_type,
            role,
            template_type,
            index,
            len(all_scenes),
            opening_variant=opening_variant,
            ending_variant=ending_variant,
            title=str(narration_plan.get("title") or project_id),
            text=voiceover,
        )
        visual_object = choose_visual_object(
            video_type,
            role,
            template_type,
            title=str(narration_plan.get("title") or project_id),
            text=voiceover,
            index=index,
            total=len(all_scenes),
        )
        memory_anchor = build_memory_anchor(voiceover, video_type=video_type, role=role, template_type=template_type)
        headline = build_visual_headline(
            voiceover,
            video_type=video_type,
            role=role,
            template_type=template_type,
            memory_anchor=memory_anchor,
        )
        subtitle = _subtitle_from_voiceover(voiceover, headline, video_type=video_type)
        display_conclusion = _display_conclusion(voiceover, subtitle)
        contract_context = _contract_context_for_scene(
            role=role,
            template_type=template_type,
            index=index,
            total=len(all_scenes),
            offer_profile=offer_profile.as_dict(),
            proof_asset=proof_asset.as_dict(),
            cta_policy=cta_policy.as_dict(),
            video_type=video_type,
        )
        save_reason = build_save_reason(
            video_type=video_type,
            role=role,
            template_type=template_type,
            memory_anchor=memory_anchor,
            visual_object=visual_object,
        )
        primary_message = _scene_pack_primary_message(
            headline=headline,
            video_type=video_type,
            role=role,
            template_type=template_type,
            memory_anchor=memory_anchor,
            save_reason=save_reason,
            visual_object=visual_object,
        )
        support_elements = _scene_pack_support_elements(
            layout_family=layout_family,
            role=role,
            template_type=template_type,
            primary_message=primary_message,
            memory_anchor=memory_anchor,
            save_reason=save_reason,
            visual_object=visual_object,
        )
        slot_context = {
            **contract_context,
            "offer_profile": offer_profile.as_dict(),
            "proof_asset": proof_asset.as_dict(),
            "cta_policy": cta_policy.as_dict(),
        }
        slots = _slots_for_template(
            template_type,
            headline,
            subtitle,
            display_conclusion,
            voiceover,
            role,
            contract_context=slot_context,
        )
        title_caption_overlap = title_caption_similarity(headline, subtitle or voiceover)
        caption_mode = caption_mode_for_scene(
            video_type,
            role,
            template_type,
            index,
            len(all_scenes),
            layout_family=layout_family,
            ending_variant=ending_variant,
        )
        scenes.append({
            "id": scene.get("scene_id") or f"S{index + 1:02d}",
            "role": role,
            "intent": _intent_for_role(role, voiceover, template_type),
            "duration": round(float(scene.get("duration", 0) or 0), 3),
            "voiceover": voiceover,
            "display_headline": primary_message,
            "display_subtitle": support_elements[0] if support_elements else subtitle,
            "visual_headline": primary_message,
            "memory_anchor": memory_anchor,
            "save_reason": save_reason,
            "layout_family": layout_family,
            "visual_object": visual_object,
            "primary_message": primary_message,
            "support_elements": support_elements,
            "headline_compact": primary_message,
            "title_caption_similarity": round(title_caption_overlap, 3),
            "caption_mode": caption_mode,
            "visual_role": _visual_role_for_scene(role, template_type, video_type),
            "sequence_slot": sequence_slot_for_scene(index, len(all_scenes)),
            "visual_strategy_reason": _visual_strategy_reason(video_type, role, template_type, index, len(all_scenes), layout_family=layout_family, visual_object=visual_object),
            "layout_band": layout_band_for_scene(video_type, role, template_type, index, len(all_scenes)),
            "readability_risk": round(_scene_readability_risk(headline, subtitle, slots, title_caption_overlap), 3),
            "display_conclusion": display_conclusion,
            "template_type": template_type,
            "slots": slots,
            "is_final_scene": index == len(all_scenes) - 1,
            "ending_variant": ending_variant if index == len(all_scenes) - 1 else "",
            **contract_context,
            "qa_rules": {
                "headline_max_chars": 32,
                "requires_voiceover": True,
                "requires_slots": True,
                "no_placeholder_slots": True,
                "chinese_first": True,
            },
            "semantic_score": _semantic_score(role, template_type, slots),
            "source": {
                "storyboard_role": scene.get("role", ""),
                "visual_template": scene.get("visual_template", ""),
                "sentence_ids": scene.get("sentence_ids", []),
            },
        })

    scene_pack = {
        "version": SCENE_PACK_VERSION,
        "project_id": project_id,
        "contract": "V3 semantic director -> HyperFrames native preview",
        "status": "dry_run",
        "video_type": video_type,
        "visual_strategy_id": visual_strategy.get("strategy_id", "vs_knowledge_method_v1"),
        "opening_variant": opening_variant,
        "ending_variant": ending_variant,
        "template_sequence_signature": template_sequence_signature(
            video_type=video_type,
            opening_variant=opening_variant,
            ending_variant=ending_variant,
            template_types=[scene["template_type"] for scene in scenes],
        ),
        "visual_strategy": visual_strategy,
        "scenes": scenes,
    }
    schema_errors = validate_scene_pack(scene_pack)
    contract_errors = lint_scene_pack_contracts(scene_pack)
    scene_pack["lint"] = {
        "status": "PASS" if not schema_errors and not contract_errors else "FAIL",
        "scene_pack_status": "PASS" if not schema_errors else "FAIL",
        "template_contracts_status": "PASS" if not contract_errors else "FAIL",
        "schema_errors": schema_errors,
        "contract_errors": contract_errors,
    }
    return scene_pack


def write_scene_pack(scene_pack: dict[str, Any], project_dir: Path) -> None:
    payload = json.dumps(scene_pack, ensure_ascii=False, indent=2) + "\n"
    (project_dir / "scene_pack.json").write_text(payload, encoding="utf-8")
    data_dir = project_dir / "hyperframes_timeline" / "data"
    if data_dir.exists():
        (data_dir / "scene_pack.json").write_text(payload, encoding="utf-8")


def _scene_voiceover(scene: dict[str, Any], narration_plan: dict[str, Any], audio_timeline: dict[str, Any]) -> str:
    narration = str(scene.get("narration") or "").strip()
    if narration:
        return narration
    sentence_ids = set(scene.get("sentence_ids", []))
    if sentence_ids:
        by_id = {item.get("sentence_id"): item.get("text", "") for item in audio_timeline.get("sentence_timings", [])}
        joined = " ".join(by_id.get(sid, "") for sid in sentence_ids).strip()
        if joined:
            return joined
    sentences = narration_plan.get("sentence_list", [])
    if sentences:
        return str(sentences[0].get("text", "")).strip()
    return "这一段的重点是把动作先跑通。"


def _template_type_for_scene(
    scene: dict[str, Any],
    role: str,
    index: int,
    total: int,
    *,
    video_type: str,
    opening_variant: str,
    ending_variant: str,
) -> str:
    visual_template = str(scene.get("visual_template") or "")
    strategy_cycle = _strategy_template_cycle(video_type)
    if index == 0:
        return _opening_template_for_strategy(video_type, opening_variant, visual_template, role)
    if index == total - 1:
        return _ending_template_for_strategy(video_type, ending_variant, role, visual_template)

    if visual_template in VISUAL_TEMPLATE_TO_CONTRACT:
        template_type = VISUAL_TEMPLATE_TO_CONTRACT[visual_template]
        if template_type == "final_cta":
            if role == "cta" and index == total - 1:
                return _ending_template_for_strategy(video_type, ending_variant, role, visual_template)
            if role in {"offer", "verdict"} and index < total - 1:
                return _summary_variant_for_scene(index, total)
            return _ending_template_for_strategy(video_type, ending_variant, role, visual_template)
        if template_type in strategy_cycle and _template_allowed_for_role(template_type, role):
            return template_type

    if role == "hook":
        return _opening_template_for_strategy(video_type, opening_variant, visual_template, role)

    if role == "proof":
        if video_type == "sales_offer":
            return "proof"
        if video_type == "ai_toolflow":
            return "case_study_card" if index % 2 else "knowledge_graph"
        return "case_study_card" if index % 2 else "knowledge_graph"

    if role == "problem":
        return "problem_conflict" if video_type == "sales_offer" else "myth_bust"

    if role == "conflict":
        return "problem_conflict" if video_type == "sales_offer" else "before_after"

    if role == "method":
        if video_type == "ai_toolflow":
            method_cycle = ("tool_stack", "progress_tracker", "method_steps", "knowledge_graph")
            return method_cycle[index % len(method_cycle)]
        if video_type == "sales_offer":
            method_cycle = ("problem_conflict", "before_after", "method_steps")
            return method_cycle[index % len(method_cycle)]
        method_cycle = ("method_steps", "framework_quadrant", "concept_layers", "knowledge_graph", "before_after")
        return method_cycle[index % len(method_cycle)]

    if role == "offer":
        if video_type == "sales_offer":
            return _summary_variant_for_scene(index, total) if index < total - 1 else "final_cta"
        return _summary_variant_for_scene(index, total)

    if role == "verdict":
        return _summary_variant_for_scene(index, total)

    if role == "cta":
        return _ending_template_for_strategy(video_type, ending_variant, role, visual_template)

    return strategy_cycle[index % len(strategy_cycle)] if strategy_cycle else "before_after"


def _summary_variant_for_scene(index: int, total: int) -> str:
    """Rotate summary-like scenes across a small reusable template set.

    This keeps offer / verdict scenes readable while avoiding repeated
    result_summary blocks in contract-driven previews.
    """
    cycle = ("result_summary", "case_study_card", "before_after")
    return cycle[index % len(cycle)] if total else "result_summary"


def _rebalance_scene_role(
    role: str,
    voiceover: str,
    index: int,
    total: int,
    previous_role: str,
    *,
    video_type: str,
    total_scenes: int,
) -> str:
    """Slightly rebalance role assignments so CTA/proof distribution matches human review."""
    normalized = normalize_scene_role(role)
    text = (voiceover or "").strip()
    if not text:
        return normalized

    last_index = max(0, total - 1)
    early_cutoff = max(2, int(total * 0.7))
    summary_like = _looks_like_summary_line(text)
    action_like = _looks_like_action_line(text)
    proof_like = _looks_like_concrete_evidence(text)
    problem_like = _looks_like_problem_line(text)

    if index == last_index:
        if normalized in {"cta", "offer", "verdict"}:
            return "cta"
        if summary_like:
            return "cta"
        return normalized

    if normalized == "cta":
        if index < early_cutoff:
            if summary_like:
                return "verdict" if video_type != "sales_offer" else "offer"
            return "offer" if action_like and video_type == "sales_offer" else "verdict"
        return "offer"

    if normalized == "offer":
        if video_type != "sales_offer":
            if index < max(2, int(total * 0.55)):
                return "method"
            if summary_like:
                return "verdict"
            return "method" if action_like else "method"
        if index < max(2, int(total * 0.55)):
            return "method" if action_like or summary_like else "method"
        if summary_like and previous_role in {"offer", "verdict"}:
            return "method"
        if summary_like:
            return "offer"
        return "method" if action_like and not proof_like else "offer"

    if normalized in {"problem", "conflict"}:
        if summary_like or (previous_role in {"problem", "conflict"} and (action_like or proof_like)):
            return "verdict"
        if previous_role in {"problem", "conflict"} and not problem_like:
            return "method"

    if normalized == "method":
        if index >= total - 2 and summary_like:
            return "verdict"
        if index > 0 and previous_role in {"problem", "conflict"} and action_like and not problem_like:
            return "method"

    if normalized == "proof":
        if index >= total - 2 and summary_like and not proof_like:
            return "verdict"
        if summary_like and not proof_like:
            return "verdict"

    if normalized == "verdict":
        if index < last_index:
            if video_type != "sales_offer":
                return "method" if not proof_like else "proof"
            if summary_like and previous_role in {"offer", "verdict"}:
                return "method"
            if summary_like:
                return "offer"
            if action_like:
                return "offer"
            return "method"

    return normalized


def _intent_for_role(role: str, voiceover: str, template_type: str) -> str:
    template_intents = {
        "hook": "capture_attention",
        "problem_conflict": "show_pain_or_gap",
        "before_after": "show_transformation",
        "proof": "support_claim",
        "final_cta": "close_with_action",
        "method_steps": "explain_sequence",
        "framework_quadrant": "structure_framework",
        "progress_tracker": "show_progress",
        "tool_stack": "show_system_stack",
        "keyword_punchline": "memorize_core_phrase",
        "myth_bust": "correct_misconception",
        "case_study_card": "show_case_outcome",
        "concept_layers": "explain_abstraction_levels",
        "knowledge_graph": "show_connected_knowledge",
        "result_summary": "summarize_outcome",
    }
    if "不是" in voiceover and "而是" in voiceover:
        return "frame_contrast"
    return template_intents.get(template_type, {
        "hook": "capture_attention",
        "problem": "show_pain_or_gap",
        "conflict": "frame_tension",
        "method": "explain_actionable_method",
        "proof": "support_claim",
        "offer": "make_next_step_concrete",
        "cta": "close_with_action",
        "verdict": "summarize_judgement",
    }.get(role, "explain_actionable_method"))


def _template_allowed_for_role(template_type: str, role: str) -> bool:
    contract_roles = {
        "hook": {"hook"},
        "problem_conflict": {"problem", "conflict", "method"},
        "before_after": {"method", "offer", "proof", "verdict"},
        "proof": {"proof", "verdict", "method"},
        "final_cta": {"cta", "offer", "verdict"},
        "method_steps": {"method", "offer"},
        "framework_quadrant": {"method", "proof"},
        "progress_tracker": {"proof", "method"},
        "tool_stack": {"method", "offer"},
        "keyword_punchline": {"hook", "problem"},
        "myth_bust": {"hook", "problem", "method"},
        "case_study_card": {"proof", "offer", "verdict"},
        "concept_layers": {"method", "proof"},
        "knowledge_graph": {"proof", "method"},
        "result_summary": {"verdict", "cta", "proof", "offer"},
    }
    return role in contract_roles.get(template_type, {role})


def _strategy_template_cycle(video_type: str) -> tuple[str, ...]:
    return {
        "knowledge_method": ("method_steps", "framework_quadrant", "concept_layers", "knowledge_graph", "before_after", "result_summary"),
        "ai_toolflow": ("tool_stack", "progress_tracker", "method_steps", "knowledge_graph", "case_study_card", "before_after", "result_summary"),
        "sales_offer": ("problem_conflict", "before_after", "proof", "case_study_card", "result_summary", "final_cta"),
    }.get(video_type, ("before_after", "result_summary"))


def _opening_template_for_strategy(video_type: str, opening_variant: str, visual_template: str, role: str) -> str:
    if video_type == "sales_offer":
        if opening_variant == "pain_hook":
            return "hook" if role == "hook" else "problem_conflict"
        if opening_variant == "contrast_hook":
            return "before_after" if role != "hook" else "hook"
        if opening_variant == "mistake_hook":
            return "myth_bust" if role != "hook" else "hook"
        return "hook"
    if video_type == "ai_toolflow":
        if opening_variant == "process_hook":
            return "hook" if role == "hook" else "tool_stack"
        if opening_variant == "result_hook":
            return "hook" if role == "hook" else "progress_tracker"
        if opening_variant == "contrast_hook":
            return "hook" if role == "hook" else "before_after"
        return "hook"
    if opening_variant == "mistake_hook":
        return "myth_bust" if role != "hook" else "hook"
    if opening_variant == "contrast_hook":
        return "before_after" if role != "hook" else "hook"
    return "hook"


def _ending_template_for_strategy(video_type: str, ending_variant: str, role: str, visual_template: str) -> str:
    if role == "cta":
        return "final_cta"
    if video_type == "sales_offer":
        if ending_variant == "offer_close":
            return "final_cta"
        return "result_summary"
    if video_type == "ai_toolflow":
        if ending_variant == "checklist_close":
            return "result_summary"
        if ending_variant == "action_close":
            return "result_summary"
        return "result_summary"
    return "result_summary"


def _slots_for_template(
    template_type: str,
    headline: str,
    subtitle: str,
    conclusion: str,
    voiceover: str,
    role: str,
    *,
    contract_context: dict[str, Any] | None = None,
) -> dict[str, Any]:
    contract_context = contract_context or {}
    offer_profile = contract_context.get("offer_profile", {})
    proof_asset = contract_context.get("proof_asset", {})
    cta_policy = contract_context.get("cta_policy", {})
    if template_type == "hook":
        return {
            "main_claim": headline,
            "pain_point": _clip(subtitle or "问题不是记不住，而是没有可调用的结构。", 40),
            "status_badge": _status_badge_for_text(voiceover),
            "visual_emphasis": _visual_emphasis_for_text(voiceover),
        }
    if template_type == "problem_conflict":
        return {
            "problem_title": headline,
            "conflict_items": _split_short_phrases(voiceover, 3, defaults=["动作分散", "入口太多", "输出卡住"]),
            "consequence": _clip(conclusion or "结果是想输出时总要从头来。", 40),
            "warning_label": _warning_label_for_text(voiceover),
        }
    if template_type == "before_after":
        before, after = _before_after_from_text(voiceover)
        return {
            "before_label": "以前",
            "after_label": "现在",
            "before_items": _split_short_phrases(before, 3, defaults=["入口分散", "检索缓慢", "写作卡住"]),
            "after_items": _split_short_phrases(after, 3, defaults=["统一入口", "直接调用", "输出更稳"]),
            "verdict": _clip(conclusion or "把链路接起来，动作才会稳定。", 36),
        }
    if template_type == "proof":
        metric_or_evidence = _metric_or_evidence_for_text(voiceover)
        if _looks_generic_proof(metric_or_evidence) and isinstance(proof_asset, dict):
            metric_or_evidence = str(proof_asset.get("metric_source") or metric_or_evidence).strip()
        return {
            "proof_title": headline,
            "proof_items": _proof_items_from_text(voiceover, proof_asset=proof_asset),
            "metric_or_evidence": metric_or_evidence,
            "credibility_note": _clip(
                conclusion
                or str(proof_asset.get("credibility_note") or "这是有执行记录的路径，不是空话。"),
                36,
            ),
        }
    if template_type == "final_cta":
        cta_text = _cta_text_for_text(voiceover)
        if _looks_generic_cta(cta_text) and isinstance(cta_policy, dict):
            cta_text = str(cta_policy.get("preferred_cta_text") or cta_text).strip()
        avoid_phrases = _avoid_phrases_for_cta(voiceover)
        policy_forbidden = [str(item).strip() for item in cta_policy.get("forbidden_phrases", []) if str(item).strip()]
        for item in policy_forbidden:
            if item not in avoid_phrases:
                avoid_phrases.append(item)
        return {
            "final_claim": _clip(str(offer_profile.get("core_promise") or headline), 30),
            "next_step": _clip(
                conclusion
                or str(offer_profile.get("next_step") or "先完成一次真实执行，再继续升级。"),
                34,
            ),
            "cta_text": cta_text,
            "avoid_phrases": avoid_phrases,
        }
    if template_type == "method_steps":
        steps = _sentence_steps(voiceover)
        return {
            "method_title": headline,
            "steps": [item["text"] for item in steps],
            "step_labels": [item["label"] for item in steps],
            "final_result": _clip(conclusion or "三步跑完，就能拿到可复用路径。", 34),
        }
    if template_type == "framework_quadrant":
        quadrants = _framework_quadrants(voiceover)
        return {
            "framework_title": headline,
            "quadrants": quadrants,
            "center_claim": _clip(_keyword_from_text(voiceover), 16),
            "usage_note": _clip(conclusion or "用这个框架判断当前卡在哪一层。", 36),
        }
    if template_type == "progress_tracker":
        stages = _progress_stages(voiceover)
        current_stage = stages[min(1, len(stages) - 1)]["label"]
        return {
            "progress_title": headline,
            "stages": stages,
            "current_stage": _clip(current_stage, 18),
            "completion_signal": _completion_signal(voiceover),
        }
    if template_type == "tool_stack":
        stack = _tool_stack(voiceover)
        return {
            "stack_title": _clip(f"{_keyword_from_text(voiceover)}工具栈", 18),
            "tools": [item["tool"] for item in stack],
            "tool_roles": [item["role"] for item in stack],
            "workflow_result": _clip(conclusion or "工具各司其职，结果才能稳定产出。", 34),
        }
    if template_type == "keyword_punchline":
        keyword = _keyword_from_text(voiceover)
        return {
            "keyword": _clip(keyword, 10),
            "punchline": _clip(headline, 28),
            "contrast": _clip(_contrast_line(voiceover), 26),
            "memory_anchor": _clip(_memory_anchor(voiceover), 16),
        }
    if template_type == "myth_bust":
        myth, truth = _myth_truth(voiceover)
        return {
            "myth": _clip(myth, 26),
            "truth": _clip(truth, 26),
            "reason": _clip(conclusion or "真正的问题不是工具数量，而是动作没闭环。", 34),
            "correction": _clip(_correction_line(voiceover), 24),
        }
    if template_type == "case_study_card":
        situation, action, result = _case_story_triplet(voiceover)
        metric_or_evidence = _metric_or_evidence_for_text(voiceover)
        return {
            "case_title": _clip(headline, 28),
            "situation": _clip(situation, 24),
            "action": _clip(action, 24),
            "result": _clip(result, 24),
            "lesson": _clip(conclusion or str(offer_profile.get("core_promise") or "先跑通最小路径，再扩大系统规模。"), 28),
            "metric_or_evidence": metric_or_evidence,
            "credibility_note": _clip(str(proof_asset.get("credibility_note") or "有执行记录，不是空谈。"), 22),
        }
    if template_type == "concept_layers":
        layers = _concept_layers(voiceover)
        return {
            "concept_title": _clip(headline, 28),
            "layers": [item["label"] for item in layers],
            "layer_descriptions": [item["text"] for item in layers],
            "conclusion": _clip(conclusion or "理解层次以后，就知道下一步该补哪一层。", 34),
        }
    if template_type == "knowledge_graph":
        nodes, edges = _knowledge_graph(voiceover)
        return {
            "graph_title": headline,
            "nodes": nodes,
            "edges": edges,
            "insight": _clip(conclusion or "一旦节点连起来，调用成本就会快速下降。", 34),
        }
    if template_type == "result_summary":
        return {
            "result_title": _clip(headline, 28),
            "key_results": _summary_key_results(voiceover),
            "final_verdict": _clip(
                conclusion or str(offer_profile.get("core_promise") or "这一轮你已经拿到一个可执行、可复用的结论。"),
                34,
            ),
            "next_step": _clip(
                _next_step_from_text(voiceover) or str(offer_profile.get("next_step") or ""),
                30,
            ),
        }
    return {
        "final_claim": headline,
        "next_step": _clip(conclusion or "先完成一次真实执行，再继续升级。", 34),
        "cta_text": _cta_text_for_text(voiceover),
        "avoid_phrases": _avoid_phrases_for_cta(voiceover),
    }


def _semantic_score(role: str, template_type: str, slots: dict[str, Any]) -> dict[str, float]:
    required_like = len([value for value in slots.values() if value not in ("", [], {}, None)])
    readability_risk = 0.2
    for value in slots.values():
        if isinstance(value, str) and len(value) > 28:
            readability_risk = max(readability_risk, 0.45)
        if isinstance(value, list) and len(value) > 4:
            readability_risk = max(readability_risk, 0.5)
    return {
        "role_match": 0.92 if role and template_type else 0.5,
        "slot_completeness": round(min(1.0, required_like / max(len(slots), 1)), 2),
        "visual_readability_risk": round(readability_risk, 2),
        "cta_presence": 1.0 if role == "cta" or template_type == "final_cta" else 0.0,
        "proof_presence": 1.0 if role == "proof" or template_type in {"proof", "knowledge_graph", "progress_tracker", "case_study_card"} else 0.0,
    }


def _headline_from_voiceover(voiceover: str, role: str, template_type: str, video_type: str) -> str:
    cleaned = re.sub(r"[\n\r]+", " ", voiceover).strip()
    if not cleaned:
        return {
            "hook": "先抓住这一秒",
            "problem": "问题不是工具不够",
            "method": "把步骤拆成动作",
            "proof": "结果要能被看见",
            "cta": "现在跑一遍",
        }.get(role, "这一段的重点")
    return build_visual_headline(
        cleaned,
        video_type=video_type,
        role=role,
        template_type=template_type,
        memory_anchor=_memory_anchor(cleaned),
    )


def should_compact_headline(text: str) -> bool:
    compact = re.sub(r"\s+", "", str(text)).strip()
    if len(compact) >= 18:
        return True
    if any(marker in compact for marker in ("，", "。", "；", "：", "？", "！")):
        return len(compact) >= 12
    if any(token in compact for token in ("不是", "而是", "以前", "现在", "但是", "所以")):
        return True
    return False


def _trim_fillers(text: str) -> str:
    compact = re.sub(r"\s+", "", str(text)).strip()
    for filler in ("这个", "那个", "然后", "其实", "就是", "有点", "一下", "我们", "可以"):
        compact = compact.replace(filler, "")
    compact = compact.strip(" ，。；;:：")
    return compact or str(text).strip()


def _remove_leading_fragments(text: str) -> str:
    compact = re.sub(r"\s+", "", str(text)).strip()
    for prefix in ("我把", "以前的流程是", "以前", "之前", "然后", "再", "先", "一个", "一种", "10", "十"):
        if compact.startswith(prefix) and len(compact) > len(prefix) + 1:
            compact = compact[len(prefix):].lstrip(" ，。；;:：")
    compact = re.sub(r"^(我把|以前的流程是|以前|之前|然后|再|先)\s*", "", compact)
    return compact.strip()


def _is_fragment_headline(text: str) -> bool:
    compact = re.sub(r"\s+", "", str(text)).strip()
    if not compact:
        return True
    if compact in {"10", "我把", "以前的流程是", "以前", "之前", "然后", "再", "先"}:
        return True
    if compact.isdigit() or len(compact) <= 2:
        return True
    if compact.startswith(("我把", "以前的流程是", "以前", "之前", "然后", "再")):
        return True
    return False


def _subtitle_from_voiceover(voiceover: str, headline: str, *, video_type: str) -> str:
    remainder = voiceover.replace(headline.replace("…", ""), "", 1).strip(" ，。；;:：")
    candidate = remainder or voiceover
    if title_caption_similarity(headline, candidate) > 0.65:
        candidate = _trim_fillers(candidate)
    if video_type == "sales_offer":
        return _clip(candidate, 34)
    if video_type == "ai_toolflow":
        return _clip(candidate, 38)
    return _clip(candidate, 40)


def _display_conclusion(voiceover: str, subtitle: str) -> str:
    if "所以" in voiceover:
        return _clip(voiceover.split("所以", 1)[1].strip(" ，。"), 38)
    if "这样" in voiceover:
        tail = voiceover.split("这样", 1)[-1].strip(" ，。")
        if tail:
            return _clip(tail, 38)
    return _clip(subtitle or voiceover, 38)


def _visual_strategy_text(
    *,
    source_text: str | None,
    narration_plan: dict[str, Any],
    storyboard: dict[str, Any],
) -> str:
    parts: list[str] = []
    if source_text:
        parts.append(source_text)
    title = str(narration_plan.get("title") or "").strip()
    if title:
        parts.append(title)
    for sentence in narration_plan.get("sentence_list", []):
        text = str(sentence.get("text") or "").strip()
        if text:
            parts.append(text)
    for scene in storyboard.get("scenes", []) or []:
        text = str(scene.get("narration") or "").strip()
        if text:
            parts.append(text)
    return "\n".join(parts)


def _contract_context_for_scene(
    *,
    role: str,
    template_type: str,
    index: int,
    total: int,
    offer_profile: dict[str, Any],
    proof_asset: dict[str, Any],
    cta_policy: dict[str, Any],
    video_type: str,
) -> dict[str, Any]:
    context: dict[str, Any] = {}
    if template_type in {"result_summary", "final_cta"} or role in {"offer", "cta", "verdict"}:
        context["offer_profile_ref"] = str(offer_profile.get("profile_id") or "default_ai_content_system")
        context["cta_policy_ref"] = str(cta_policy.get("policy_id") or "default_value_first")
        stage = _cta_stage_for_scene(index=index, total=total, role=role, template_type=template_type)
        context["cta_stage"] = stage
        context["cta_strength"] = _cta_strength_for_stage(stage, role=role, template_type=template_type)
    if template_type in {"proof", "case_study_card", "knowledge_graph", "progress_tracker"} or role == "proof":
        context["proof_asset_ref"] = str(proof_asset.get("asset_id") or "default_ai_content_system_proof")
    return context


def _visual_role_for_scene(role: str, template_type: str, video_type: str) -> str:
    if template_type in {"method_steps", "framework_quadrant", "concept_layers", "knowledge_graph", "tool_stack", "progress_tracker"}:
        return f"{video_type}:structure"
    if template_type in {"proof", "case_study_card"}:
        return f"{video_type}:evidence"
    if template_type in {"final_cta", "result_summary"}:
        return f"{video_type}:closing"
    if role == "hook":
        return f"{video_type}:opening"
    if role in {"problem", "conflict"}:
        return f"{video_type}:pain"
    return f"{video_type}:{role}"


def _visual_strategy_reason(
    video_type: str,
    role: str,
    template_type: str,
    index: int,
    total: int,
    *,
    layout_family: str = "",
    visual_object: str = "",
) -> str:
    slot = sequence_slot_for_scene(index, total)
    extras = [part for part in (layout_family, visual_object) if part]
    suffix = f"[{':'.join(extras)}]" if extras else ""
    return f"{video_type}:{slot}:{role}->{template_type}{suffix}"


def _scene_readability_risk(headline: str, subtitle: str, slots: dict[str, Any], title_caption_similarity_value: float) -> float:
    risk = 0.12
    headline_chars = len(re.findall(r"[\u4e00-\u9fff]", headline))
    headline_total = len(headline.strip())
    if headline_chars > 26 or headline_total > 32:
        risk += 0.24
    if headline_chars > 18:
        risk += 0.12
    if title_caption_similarity_value > 0.65:
        risk += 0.22
    if subtitle and len(subtitle.strip()) > 48:
        risk += 0.10
    list_heaviness = sum(len(value) for value in slots.values() if isinstance(value, list))
    if list_heaviness >= 8:
        risk += 0.12
    if len(slots) >= 5:
        risk += 0.08
    return min(risk, 1.0)


def _cta_stage_for_scene(*, index: int, total: int, role: str, template_type: str) -> str:
    if index >= max(0, total - 1) and (role == "cta" or template_type == "final_cta"):
        return "final"
    ratio = index / max(total - 1, 1)
    if ratio >= 0.78:
        return "late"
    if ratio >= 0.45:
        return "mid"
    return "opening"


def _cta_strength_for_stage(stage: str, *, role: str, template_type: str) -> str:
    if stage == "final" or template_type == "final_cta":
        return "strong"
    if stage == "late" or role in {"offer", "verdict"}:
        return "normal"
    return "soft"


def _before_after_from_text(text: str) -> tuple[str, str]:
    if "以前" in text and "现在" in text:
        before = text.split("现在", 1)[0].replace("以前", "").strip(" ，。")
        after = text.split("现在", 1)[1].strip(" ，。")
        return before or "入口分散", after or "流程可复用"
    if "不是" in text and "而是" in text:
        before = text.split("而是", 1)[0].replace("不是", "").strip(" ，。")
        after = text.split("而是", 1)[1].strip(" ，。")
        return before or "旧判断", after or "新判断"
    return "动作分散，输出成本高", text


def _split_short_phrases(text: str, limit: int, defaults: list[str] | None = None) -> list[str]:
    parts = [p.strip() for p in re.split(r"[，,。；;：:、\s]+", text) if p.strip()]
    result = [_clip(p, 18) for p in parts[:limit]]
    fallback = defaults or ["输入", "结构", "输出", "复盘"]
    while len(result) < limit:
        result.append(fallback[len(result)])
    return result[:limit]


def _sentence_steps(text: str) -> list[dict[str, str]]:
    chunks = [chunk.strip() for chunk in re.split(r"[。；;]", text) if chunk.strip()]
    labels = ["STEP 1", "STEP 2", "STEP 3", "STEP 4"]
    steps = []
    for idx, chunk in enumerate(chunks[:4]):
        steps.append({"label": labels[idx], "text": _clip(chunk, 22)})
    while len(steps) < 3:
        defaults = ["统一入口", "建立结构", "开始调用"]
        steps.append({"label": labels[len(steps)], "text": defaults[len(steps)]})
    return steps


def _framework_quadrants(text: str) -> list[dict[str, str]]:
    seeds = _split_short_phrases(text, 4, defaults=["输入", "整理", "检索", "输出"])
    labels = ["Q1", "Q2", "Q3", "Q4"]
    return [{"label": labels[idx], "text": seed} for idx, seed in enumerate(seeds[:4])]


def _progress_stages(text: str) -> list[dict[str, str]]:
    stages = _split_short_phrases(text, 3, defaults=["入口统一", "知识连起来", "输出跑起来"])
    return [{"label": f"阶段 {idx + 1}", "text": item} for idx, item in enumerate(stages)]


def _tool_stack(text: str) -> list[dict[str, str]]:
    tools = []
    known = [("Obsidian", "存储与链接"), ("Claude", "检索与整理"), ("Hermes", "复盘与跟进"), ("AI", "调用与输出")]
    for tool, role in known:
        if tool in text and all(existing["tool"] != tool for existing in tools):
            tools.append({"tool": tool, "role": role})
    if not tools:
        tools = [{"tool": tool, "role": role} for tool, role in known[:3]]
    while len(tools) < 3:
        tool, role = known[len(tools)]
        tools.append({"tool": tool, "role": role})
    return tools[:4]


def _keyword_from_text(text: str) -> str:
    for token in ("执行力", "记忆力", "Claude", "Obsidian", "AI", "闭环", "系统", "第二大脑"):
        if token in text:
            return token
    compact = re.sub(r"[^\u4e00-\u9fffA-Za-z0-9]", "", text)
    return _clip(compact or "重点", 8)


def _contrast_line(text: str) -> str:
    if "不是" in text and "而是" in text:
        before = text.split("而是", 1)[0].replace("不是", "").strip(" ，。")
        after = text.split("而是", 1)[1].strip(" ，。")
        return _clip(f"{before} / {after}", 26)
    return _clip("不是多收藏，而是先接通链路", 26)


def _memory_anchor(text: str) -> str:
    compact = re.sub(r"\s+", "", str(text or ""))
    for pattern in (
        r"\d+\s*(?:分钟|秒|小时|天|周|本|条|个|种|倍|%)\s*[\u4e00-\u9fffA-Za-z0-9]{0,8}",
        r"settings\.json",
        r"bypassPermissions",
        r"Obsidian\+Codex\+Hermes",
        r"输入[-→>]?整理[-→>]?调用[-→>]?输出",
        r"看[-→>]?筛[-→>]?建",
        r"[\u4e00-\u9fff]{2,8}(?:条|个|种|步|层|页|卡|板)",
    ):
        match = re.search(pattern, compact)
        if match:
            anchor = match.group(0).replace("→", "-").replace(">", "-")
            return anchor[:16]
    if "先" in compact:
        return "先跑一遍"
    if "直接" in compact:
        return "直接调用"
    return "看筛建"


def _support_anchor_for_scene(
    *,
    layout_family: str,
    role: str,
    template_type: str,
    primary_message: str,
    memory_anchor: str,
    save_reason: str,
    visual_object: str,
) -> str:
    layout_family = (layout_family or "").strip()
    role = (role or "").strip().lower()
    template_type = (template_type or "").strip()
    candidates = [
        {
            "hero_metric": "数字支撑",
            "hero_statement": "主视觉",
            "myth_bust": "问题拆解",
            "tool_pipeline": "流程支撑",
            "config_panel": "流程支撑",
            "file_tree": "流程支撑",
            "framework_map": "结构支撑",
            "proof_matrix": "证据支撑",
            "comparison_board": "对照支撑",
            "knowledge_graph": "结构支撑",
            "concept_layers": "概念分层",
            "progress_tracker": "进度追踪",
            "section_board": "结果收束",
            "action_close": "收束动作",
            "checklist_close": "行动清单",
            "insight_close": "观点收束",
            "offer_close": "成交收束",
        }.get(layout_family, ""),
        {
            "hook": "开场钩子",
            "problem": "问题定位",
            "conflict": "冲突点",
            "method": "方法支撑",
            "proof": "证据支撑",
            "offer": "价值说明",
            "cta": "行动收束",
            "verdict": "最终结论",
        }.get(role, ""),
        {
            "hook": "开场钩子",
            "problem_conflict": "问题定位",
            "before_after": "前后对比",
            "proof": "证据支撑",
            "final_cta": "行动收束",
            "method_steps": "方法步骤",
            "framework_quadrant": "框架图",
            "progress_tracker": "进度追踪",
            "tool_stack": "工具栈",
            "keyword_punchline": "关键词",
            "myth_bust": "问题拆解",
            "case_study_card": "真实案例",
            "concept_layers": "概念分层",
            "knowledge_graph": "知识图谱",
            "result_summary": "结果总结",
        }.get(template_type, ""),
        _clip(memory_anchor or "", 12),
        _clip(save_reason or "", 12),
        _clip(visual_object or "", 12),
        "结构支撑",
    ]
    normalized_primary = re.sub(r"\s+", "", primary_message or "")
    for candidate in candidates:
        text = _clip(candidate or "", 16)
        if text and re.sub(r"\s+", "", text) != normalized_primary:
            return text
    return "结构支撑"


def _scene_pack_primary_message(
    *,
    headline: str,
    video_type: str,
    role: str,
    template_type: str,
    memory_anchor: str,
    save_reason: str,
    visual_object: str,
) -> str:
    primary = headline_compact(headline or "", video_type=video_type, role=role, template_type=template_type)
    if not primary:
        for candidate in (memory_anchor, save_reason, visual_object, headline):
            compact = headline_compact(candidate or "", video_type=video_type, role=role, template_type=template_type)
            if compact:
                primary = compact
                break
    if not primary:
        primary = "结构支撑"
    return _clip(primary, 16)


def _scene_pack_support_elements(
    *,
    layout_family: str,
    role: str,
    template_type: str,
    primary_message: str,
    memory_anchor: str,
    save_reason: str,
    visual_object: str,
) -> list[str]:
    support = _support_anchor_for_scene(
        layout_family=layout_family,
        role=role,
        template_type=template_type,
        primary_message=primary_message,
        memory_anchor=memory_anchor,
        save_reason=save_reason,
        visual_object=visual_object,
    )
    support = _clip(support, 12)
    if support and re.sub(r"\s+", "", support) != re.sub(r"\s+", "", primary_message or ""):
        return [support]
    for candidate in (memory_anchor, save_reason, visual_object):
        support = _clip(candidate or "", 12)
        if support and re.sub(r"\s+", "", support) != re.sub(r"\s+", "", primary_message or ""):
            return [support]
    return [support or "结构支撑"]


def _myth_truth(text: str) -> tuple[str, str]:
    if "不是" in text and "而是" in text:
        myth = text.split("而是", 1)[0].replace("不是", "").strip(" ，。")
        truth = text.split("而是", 1)[1].strip(" ，。")
        return myth or "多装插件就能提高效率", truth or "先跑通最小闭环"
    if "别" in text or "不要" in text:
        return "一上来就做复杂系统", "先跑通最小闭环"
    return "以为记不住是努力不够", "其实是没有可调用结构"


def _correction_line(text: str) -> str:
    if "先" in text:
        return _clip("先跑通，再升级", 24)
    return _clip("先让系统可用", 24)


def _case_story_triplet(text: str) -> tuple[str, str, str]:
    sentences = [part.strip() for part in re.split(r"[。；;]", text) if part.strip()]
    if len(sentences) >= 3:
        return sentences[0], sentences[1], sentences[2]
    if len(sentences) == 2:
        return sentences[0], sentences[1], "结果是输出成本明显下降"
    return "原来流程很散", "后来先把入口统一", "结果是可以直接调用已有素材"


def _concept_layers(text: str) -> list[dict[str, str]]:
    seeds = _split_short_phrases(text, 3, defaults=["收集", "组织", "调用"])
    labels = ["底层", "中层", "顶层", "结果层"]
    return [{"label": labels[idx], "text": seed} for idx, seed in enumerate(seeds)]


def _knowledge_graph(text: str) -> tuple[list[dict[str, str]], list[dict[str, str]]]:
    nodes = [{"id": f"N{idx+1}", "label": label} for idx, label in enumerate(_split_short_phrases(text, 4, defaults=["输入", "链接", "检索", "输出"]))]
    edges = []
    for idx in range(len(nodes) - 1):
        edges.append({"from": nodes[idx]["id"], "to": nodes[idx + 1]["id"]})
    if len(nodes) >= 3:
        edges.append({"from": nodes[0]["id"], "to": nodes[-1]["id"]})
    return nodes, edges


def _metric_or_evidence_for_text(text: str) -> str:
    number_match = re.search(r"\d+\s*(秒|分钟|小时|天|周|本|条|个|%)", text)
    if number_match:
        return number_match.group(0)
    if "以前" in text and "现在" in text:
        return "前后对比"
    for marker in ("截图", "日志", "记录", "执行", "流程", "闭环", "对比", "素材包"):
        if marker in text:
            return f"{marker}记录"
    if "案例" in text:
        return "执行记录"
    return "前后对比"


def _looks_generic_proof(text: str) -> bool:
    compact = text.strip()
    if not compact:
        return True
    if compact in {"真实案例", "经验", "可复用", "已验证", "已经跑通", "结果看得见"}:
        return True
    return any(term in compact for term in ("真实案例", "经验", "案例", "实例", "已经跑通", "可复用"))


def _proof_items_from_text(text: str, proof_asset: dict[str, Any] | None = None) -> list[str]:
    cues = []
    for phrase in ("前后对比", "执行记录", "流程闭环", "素材包", "步骤可追溯", "结果可见"):
        if phrase in text:
            cues.append(phrase)
    if proof_asset:
        for item in proof_asset.get("evidence_items", []):
            value = str(item).strip()
            if value and value not in cues:
                cues.append(value)
                if len(cues) >= 4:
                    break
    if cues:
        return _split_short_phrases("，".join(cues), 3, defaults=["前后对比", "执行记录", "流程闭环"])
    if "以前" in text and "现在" in text:
        return ["前后对比", "执行记录", "流程闭环"]
    return _split_short_phrases(text, 3, defaults=["前后对比", "执行记录", "流程闭环"])


def _summary_key_results(text: str) -> list[str]:
    cues = []
    for phrase in ("可执行", "可复用", "可追溯", "流程闭环", "问题已明确", "下一步清楚"):
        if phrase in text:
            cues.append(phrase)
    if not cues:
        cues = ["流程闭环", "阻塞点已明确", "下一步可执行"]
    return _split_short_phrases("，".join(cues), 3, defaults=["流程闭环", "阻塞点已明确", "下一步可执行"])


def _looks_like_summary_line(text: str) -> bool:
    markers = ("所以", "结果", "最后", "总结", "收束", "下一步", "先跑通", "先完成", "接下来", "建议", "价值", "真正", "其实", "实际上", "靠的是", "不在", "而在")
    return any(marker in text for marker in markers)


def _looks_like_action_line(text: str) -> bool:
    markers = ("先", "再", "然后", "接着", "开始", "跑通", "执行", "调用", "整理", "统一", "建立")
    return any(marker in text for marker in markers)


def _looks_like_concrete_evidence(text: str) -> bool:
    markers = ("截图", "日志", "记录", "前后", "对比", "流程", "闭环", "素材包", "步骤", "场景", "结果")
    return any(marker in text for marker in markers)


def _looks_like_problem_line(text: str) -> bool:
    markers = ("问题", "卡住", "散", "焦虑", "不够", "太多", "更慢", "更难", "没有")
    return any(marker in text for marker in markers)


def _next_step_from_text(text: str) -> str:
    if "先" in text:
        return _clip(text[text.index("先"):], 30)
    if "现在" in text:
        return _clip(text[text.index("现在"):], 30)
    return "下一步：先跑通一次真实闭环"


def _status_badge_for_text(text: str) -> str:
    if "为什么" in text or "有没有" in text:
        return "QUESTION"
    if "结果" in text or "之后" in text:
        return "RESULT"
    return "HOOK"


def _visual_emphasis_for_text(text: str) -> str:
    for token in ("执行力", "记忆力", "Claude", "Obsidian", "闭环", "系统", "第二大脑"):
        if token in text:
            return token
    return "重点"


def _warning_label_for_text(text: str) -> str:
    if "别" in text or "不要" in text:
        return "WARNING"
    if "问题" in text:
        return "PROBLEM"
    return "RISK"


def _completion_signal(text: str) -> str:
    if "完成" in text or "跑通" in text:
        return "流程已闭环"
    if "现在" in text:
        return "可复用路径"
    return "关键阻塞点"


def _cta_text_for_text(text: str) -> str:
    if "收藏" in text:
        return "先收藏"
    if "评论" in text:
        return "评论告诉我"
    if "跑" in text:
        return "先跑一遍"
    return "现在开始"


def _looks_generic_cta(text: str) -> bool:
    compact = text.strip()
    if not compact:
        return True
    return compact in {"现在开始", "先开始", "先收藏", "继续看下去", "下一步"}


def _avoid_phrases_for_cta(text: str) -> list[str]:
    phrases = ["空谈", "完美准备", "继续囤工具"]
    if "拖" in text:
        phrases.append("继续拖延")
    return phrases[:4]


def _clip(text: str, max_chars: int) -> str:
    compact = re.sub(r"\s+", " ", str(text)).strip()
    compact = compact.replace("TODO", "").replace("placeholder", "").replace("待补充", "").replace("N/A", "")
    compact = compact.strip(" ，。；;:：")
    if len(compact) <= max_chars:
        return compact
    return compact[: max_chars - 1].rstrip(" ，。；;:：") + "…"
