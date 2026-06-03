"""Template contract registry and lint for scene_pack-driven rendering."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any


PLACEHOLDER_VALUES = {"", "TODO", "TBD", "placeholder", "占位", "待补充", "N/A", "NA"}


@dataclass(frozen=True)
class TemplateContract:
    template_id: str
    role_compatibility: tuple[str, ...]
    required_slots: tuple[str, ...]
    optional_slots: tuple[str, ...]
    max_chars: dict[str, int]
    min_items: dict[str, int]
    max_items: dict[str, int]
    fallback_template: str
    forbidden_fields: tuple[str, ...]
    lint_rules: tuple[str, ...]
    semantic_intent: str


def _contract(
    *,
    template_id: str,
    role_compatibility: tuple[str, ...],
    required_slots: tuple[str, ...],
    optional_slots: tuple[str, ...] = (),
    max_chars: dict[str, int] | None = None,
    min_items: dict[str, int] | None = None,
    max_items: dict[str, int] | None = None,
    fallback_template: str = "simple_card",
    semantic_intent: str,
) -> TemplateContract:
    return TemplateContract(
        template_id=template_id,
        role_compatibility=role_compatibility,
        required_slots=required_slots,
        optional_slots=optional_slots,
        max_chars=max_chars or {},
        min_items=min_items or {},
        max_items=max_items or {},
        fallback_template=fallback_template,
        forbidden_fields=("narration", "raw_text", "script", "script_text", "voiceover_script"),
        lint_rules=(
            "required_slots",
            "placeholder_copy",
            "item_bounds",
            "max_chars",
            "role_compatibility",
            "forbidden_fields",
        ),
        semantic_intent=semantic_intent,
    )


TEMPLATE_CONTRACTS: dict[str, TemplateContract] = {
    "hook": _contract(
        template_id="hook",
        role_compatibility=("hook",),
        required_slots=("main_claim", "pain_point", "status_badge", "visual_emphasis"),
        optional_slots=("display_subtitle",),
        max_chars={"main_claim": 30, "pain_point": 40, "status_badge": 16, "visual_emphasis": 12},
        fallback_template="simple_verdict",
        semantic_intent="capture_attention",
    ),
    "problem_conflict": _contract(
        template_id="problem_conflict",
        role_compatibility=("problem", "conflict", "method"),
        required_slots=("problem_title", "conflict_items", "consequence", "warning_label"),
        optional_slots=("display_subtitle",),
        max_chars={"problem_title": 30, "consequence": 40, "warning_label": 16},
        min_items={"conflict_items": 2},
        max_items={"conflict_items": 4},
        fallback_template="simple_card",
        semantic_intent="show_tension_or_blocker",
    ),
    "before_after": _contract(
        template_id="before_after",
        role_compatibility=("method", "offer", "proof", "verdict"),
        required_slots=("before_label", "after_label", "before_items", "after_items", "verdict"),
        optional_slots=("display_headline",),
        max_chars={"before_label": 12, "after_label": 12, "verdict": 36},
        min_items={"before_items": 2, "after_items": 2},
        max_items={"before_items": 4, "after_items": 4},
        fallback_template="simple_card",
        semantic_intent="show_transformation",
    ),
    "proof": _contract(
        template_id="proof",
        role_compatibility=("proof", "verdict", "method"),
        required_slots=("proof_title", "proof_items", "metric_or_evidence", "credibility_note"),
        optional_slots=("display_subtitle",),
        max_chars={"proof_title": 30, "metric_or_evidence": 20, "credibility_note": 36},
        min_items={"proof_items": 2},
        max_items={"proof_items": 4},
        fallback_template="simple_verdict",
        semantic_intent="support_claim_with_evidence",
    ),
    "final_cta": _contract(
        template_id="final_cta",
        role_compatibility=("cta", "offer", "verdict"),
        required_slots=("final_claim", "next_step", "cta_text", "avoid_phrases"),
        optional_slots=("display_subtitle",),
        max_chars={"final_claim": 30, "next_step": 34, "cta_text": 18},
        min_items={"avoid_phrases": 1},
        max_items={"avoid_phrases": 8},
        fallback_template="simple_verdict",
        semantic_intent="close_with_action",
    ),
    "method_steps": _contract(
        template_id="method_steps",
        role_compatibility=("method", "offer"),
        required_slots=("method_title", "steps", "step_labels", "final_result"),
        max_chars={"method_title": 30, "final_result": 34},
        min_items={"steps": 3, "step_labels": 3},
        max_items={"steps": 4, "step_labels": 4},
        fallback_template="simple_card",
        semantic_intent="explain_sequence",
    ),
    "framework_quadrant": _contract(
        template_id="framework_quadrant",
        role_compatibility=("method", "proof"),
        required_slots=("framework_title", "quadrants", "center_claim", "usage_note"),
        max_chars={"framework_title": 30, "center_claim": 16, "usage_note": 36},
        min_items={"quadrants": 4},
        max_items={"quadrants": 4},
        fallback_template="simple_card",
        semantic_intent="structure_framework",
    ),
    "progress_tracker": _contract(
        template_id="progress_tracker",
        role_compatibility=("proof", "method"),
        required_slots=("progress_title", "stages", "current_stage", "completion_signal"),
        max_chars={"progress_title": 30, "current_stage": 18, "completion_signal": 24},
        min_items={"stages": 3},
        max_items={"stages": 5},
        fallback_template="simple_card",
        semantic_intent="show_progress",
    ),
    "tool_stack": _contract(
        template_id="tool_stack",
        role_compatibility=("method", "offer"),
        required_slots=("stack_title", "tools", "tool_roles", "workflow_result"),
        max_chars={"stack_title": 28, "workflow_result": 34},
        min_items={"tools": 3, "tool_roles": 3},
        max_items={"tools": 4, "tool_roles": 4},
        fallback_template="simple_card",
        semantic_intent="show_system_stack",
    ),
    "keyword_punchline": _contract(
        template_id="keyword_punchline",
        role_compatibility=("hook", "problem"),
        required_slots=("keyword", "punchline", "contrast", "memory_anchor"),
        max_chars={"keyword": 10, "punchline": 28, "contrast": 26, "memory_anchor": 16},
        fallback_template="simple_verdict",
        semantic_intent="memorize_core_phrase",
    ),
    "myth_bust": _contract(
        template_id="myth_bust",
        role_compatibility=("hook", "problem", "method"),
        required_slots=("myth", "truth", "reason", "correction"),
        max_chars={"myth": 26, "truth": 26, "reason": 34, "correction": 24},
        fallback_template="simple_card",
        semantic_intent="correct_misconception",
    ),
    "case_study_card": _contract(
        template_id="case_study_card",
        role_compatibility=("proof", "offer", "verdict"),
        required_slots=("case_title", "situation", "action", "result", "lesson"),
        max_chars={"case_title": 28, "situation": 24, "action": 24, "result": 24, "lesson": 28},
        fallback_template="simple_card",
        semantic_intent="show_case_outcome",
    ),
    "concept_layers": _contract(
        template_id="concept_layers",
        role_compatibility=("method", "proof"),
        required_slots=("concept_title", "layers", "layer_descriptions", "conclusion"),
        max_chars={"concept_title": 28, "conclusion": 34},
        min_items={"layers": 3, "layer_descriptions": 3},
        max_items={"layers": 4, "layer_descriptions": 4},
        fallback_template="simple_card",
        semantic_intent="explain_abstraction_levels",
    ),
    "knowledge_graph": _contract(
        template_id="knowledge_graph",
        role_compatibility=("proof", "method"),
        required_slots=("graph_title", "nodes", "edges", "insight"),
        max_chars={"graph_title": 28, "insight": 34},
        min_items={"nodes": 3, "edges": 2},
        max_items={"nodes": 6, "edges": 8},
        fallback_template="simple_card",
        semantic_intent="show_connected_knowledge",
    ),
    "result_summary": _contract(
        template_id="result_summary",
        role_compatibility=("verdict", "cta", "proof", "offer"),
        required_slots=("result_title", "key_results", "final_verdict", "next_step"),
        max_chars={"result_title": 28, "final_verdict": 34, "next_step": 30},
        min_items={"key_results": 3},
        max_items={"key_results": 4},
        fallback_template="simple_verdict",
        semantic_intent="summarize_outcome",
    ),
}


CONTRACT_FALLBACK_TEMPLATES = {"simple_card", "simple_verdict"}


def get_template_contract(template_id: str) -> TemplateContract | None:
    return TEMPLATE_CONTRACTS.get(template_id)


def lint_scene_against_contract(scene: dict[str, Any]) -> list[str]:
    """Validate a scene_pack scene against its template contract."""
    template_id = str(scene.get("template_type"))
    contract = get_template_contract(template_id)
    prefix = f"{scene.get('id', '<unknown>')}:{template_id}"
    if contract is None:
        return [f"{prefix} has no template contract"]

    errors: list[str] = []
    role = scene.get("role")
    if role not in contract.role_compatibility:
        errors.append(f"{prefix} role {role!r} is not compatible with {contract.role_compatibility}")

    for forbidden in contract.forbidden_fields:
        if forbidden in scene:
            errors.append(f"{prefix} forbidden field {forbidden!r} present on contract scene")

    slots = scene.get("slots")
    if not isinstance(slots, dict):
        return errors + [f"{prefix} slots must be an object"]

    for slot_name in contract.required_slots:
        if slot_name not in slots:
            errors.append(f"{prefix} missing required slot {slot_name!r}")
            continue
        errors.extend(_lint_slot_value(prefix, slot_name, slots[slot_name], contract))

    for slot_name in contract.optional_slots:
        if slot_name in slots:
            errors.extend(_lint_slot_value(prefix, slot_name, slots[slot_name], contract))

    return errors


def lint_scene_pack_contracts(scene_pack: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    for scene in scene_pack.get("scenes", []):
        errors.extend(lint_scene_against_contract(scene))
    return errors


def require_contract_scene(scene: dict[str, Any]) -> tuple[TemplateContract | None, list[str]]:
    template_id = str(scene.get("contract_template_id") or scene.get("template_type") or "")
    contract = get_template_contract(template_id)
    if contract is None:
        return None, [f"{scene.get('id', '<unknown>')}:{template_id} has no template contract"]
    lint_scene = {
        "id": scene.get("id") or scene.get("scene_id"),
        "role": scene.get("scene_pack_role", scene.get("role")),
        "template_type": template_id,
        "slots": scene.get("slots", {}),
    }
    return contract, lint_scene_against_contract(lint_scene)


def _lint_slot_value(prefix: str, slot_name: str, value: Any, contract: TemplateContract) -> list[str]:
    errors: list[str] = []
    slot_root = slot_name.split("[", 1)[0].split(".", 1)[0]
    if isinstance(value, list):
        min_items = contract.min_items.get(slot_root)
        max_items = contract.max_items.get(slot_root)
        if min_items is not None and len(value) < min_items:
            errors.append(f"{prefix} slot {slot_root!r} needs at least {min_items} items")
        if max_items is not None and len(value) > max_items:
            errors.append(f"{prefix} slot {slot_root!r} exceeds {max_items} items")
        if not value:
            return [f"{prefix} slot {slot_root!r} must not be an empty array"]
        for idx, item in enumerate(value):
            errors.extend(_lint_slot_value(prefix, f"{slot_root}[{idx}]", item, contract))
        return errors
    if isinstance(value, dict):
        if not value:
            return [f"{prefix} slot {slot_root!r} must not be an empty object"]
        for key, item in value.items():
            errors.extend(_lint_slot_value(prefix, f"{slot_root}.{key}", item, contract))
        return errors
    if not isinstance(value, str):
        value = str(value)
    normalized = value.strip()
    if normalized in PLACEHOLDER_VALUES:
        errors.append(f"{prefix} slot {slot_name!r} is placeholder/empty")
    max_chars = contract.max_chars.get(slot_root)
    if max_chars is not None and _count_visible_chars(normalized) > max_chars:
        errors.append(f"{prefix} slot {slot_name!r} exceeds {max_chars} chars")
    return errors


def _count_visible_chars(value: str) -> int:
    return sum(1 for ch in value if not ch.isspace())
