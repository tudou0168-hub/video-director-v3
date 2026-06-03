"""Visual strategy pack for contract-driven video differentiation."""
from __future__ import annotations

from dataclasses import dataclass, asdict
import re
from typing import Any


VIDEO_TYPES = {"knowledge_method", "ai_toolflow", "sales_offer"}
OPENING_VARIANTS = {"pain_hook", "result_hook", "mistake_hook", "contrast_hook", "process_hook"}
ENDING_VARIANTS = {"insight_close", "action_close", "checklist_close", "offer_close"}
CAPTION_MODES = {"standard_caption", "emphasis_caption", "minimal_caption", "quote_caption", "action_caption"}


@dataclass(frozen=True)
class VisualStrategy:
    strategy_id: str
    video_type: str
    opening_variants: tuple[str, ...]
    preferred_templates: tuple[str, ...]
    avoided_templates: tuple[str, ...]
    max_template_repeats: int
    max_role_repeats: int
    ending_variant: str
    caption_mode_policy: dict[str, str]
    template_sequence_shape: str
    layout_density_policy: str

    def as_dict(self) -> dict[str, Any]:
        return asdict(self)


KNOWLEDGE_KEYWORDS = {
    "方法", "框架", "认知", "步骤", "为什么", "怎么", "原理", "结构", "逻辑", "体系",
    "系统", "流程", "闭环", "第二大脑", "知识", "复盘", "模型",
}
TOOLFLOW_KEYWORDS = {
    "工具", "Claude", "Codex", "Obsidian", "Hermes", "插件", "流程", "自动化",
    "工作流", "技能", "安装", "配置", "Git", "代码", "内容系统", "AI",
}
SALES_KEYWORDS = {
    "成交", "客户", "服务", "咨询", "课程", "offer", "购买", "转化", "下单", "复购",
    "卖", "付费", "产品", "报价", "方案", "买", "引导", "预约",
}

ROLE_TEMPLATE_CYCLES: dict[str, dict[str, tuple[str, ...]]] = {
    "knowledge_method": {
        "opening": ("hook_big_claim", "keyword_punchline", "myth_bust"),
        "middle": ("method_steps", "framework_quadrant", "concept_layers", "knowledge_graph", "before_after", "result_summary"),
        "ending": ("result_summary", "concept_layers"),
    },
    "ai_toolflow": {
        "opening": ("hook_big_claim", "keyword_punchline", "myth_bust"),
        "middle": ("tool_stack", "progress_tracker", "method_steps", "knowledge_graph", "case_study_card", "before_after", "result_summary"),
        "ending": ("result_summary", "case_study_card"),
    },
    "sales_offer": {
        "opening": ("hook_big_claim", "myth_bust", "before_after_compare"),
        "middle": ("problem_conflict", "before_after", "proof", "case_study_card", "result_summary"),
        "ending": ("final_cta", "result_summary"),
    },
}

STRATEGY_DEFS: dict[str, VisualStrategy] = {
    "knowledge_method": VisualStrategy(
        strategy_id="vs_knowledge_method_v1",
        video_type="knowledge_method",
        opening_variants=("contrast_hook", "process_hook", "mistake_hook"),
        preferred_templates=ROLE_TEMPLATE_CYCLES["knowledge_method"]["middle"],
        avoided_templates=("problem_conflict", "final_cta", "checklist_cta"),
        max_template_repeats=2,
        max_role_repeats=2,
        ending_variant="insight_close",
        caption_mode_policy={
            "hook": "emphasis_caption",
            "method": "standard_caption",
            "proof": "minimal_caption",
            "cta": "action_caption",
            "verdict": "standard_caption",
        },
        template_sequence_shape="hook -> framework/method -> proof -> insight_close",
        layout_density_policy="balanced_mid",
    ),
    "ai_toolflow": VisualStrategy(
        strategy_id="vs_ai_toolflow_v1",
        video_type="ai_toolflow",
        opening_variants=("process_hook", "contrast_hook", "result_hook"),
        preferred_templates=ROLE_TEMPLATE_CYCLES["ai_toolflow"]["middle"],
        avoided_templates=("problem_conflict", "myth_bust", "final_cta"),
        max_template_repeats=2,
        max_role_repeats=2,
        ending_variant="checklist_close",
        caption_mode_policy={
            "hook": "emphasis_caption",
            "method": "minimal_caption",
            "proof": "minimal_caption",
            "cta": "action_caption",
            "verdict": "standard_caption",
        },
        template_sequence_shape="hook -> stack/process -> proof -> checklist_close",
        layout_density_policy="process_mid",
    ),
    "sales_offer": VisualStrategy(
        strategy_id="vs_sales_offer_v1",
        video_type="sales_offer",
        opening_variants=("pain_hook", "contrast_hook", "mistake_hook"),
        preferred_templates=ROLE_TEMPLATE_CYCLES["sales_offer"]["middle"],
        avoided_templates=("concept_layers", "knowledge_graph"),
        max_template_repeats=2,
        max_role_repeats=2,
        ending_variant="offer_close",
        caption_mode_policy={
            "hook": "emphasis_caption",
            "problem": "minimal_caption",
            "proof": "quote_caption",
            "offer": "action_caption",
            "cta": "action_caption",
            "verdict": "standard_caption",
        },
        template_sequence_shape="hook -> pain -> proof -> offer_close",
        layout_density_policy="conversion_mid",
    ),
}


def detect_video_type(text: str, *, title: str = "", script_path: str | None = None) -> str:
    blob_raw = f"{title} {text} {script_path or ''}"
    frontmatter_role = _extract_frontmatter_field(text, "content_role")
    if frontmatter_role:
        if any(token in frontmatter_role for token in ("销售", "转化", "成交", "offer")):
            return "sales_offer"
        if any(token in frontmatter_role for token in ("工具", "流程", "工作流")):
            return "ai_toolflow"
        if any(token in frontmatter_role for token in ("知识", "方法", "认知")):
            return "knowledge_method"

    blob = blob_raw.lower()
    scores = {
        "knowledge_method": _keyword_score(blob, KNOWLEDGE_KEYWORDS),
        "ai_toolflow": _keyword_score(blob, TOOLFLOW_KEYWORDS),
        "sales_offer": _keyword_score(blob, SALES_KEYWORDS),
    }
    # Sales wins on strong commercial signals, toolflow wins on explicit tool/workflow language,
    # otherwise knowledge-method is the safe default.
    if scores["sales_offer"] >= max(scores["ai_toolflow"], scores["knowledge_method"]) and scores["sales_offer"] > 0:
        return "sales_offer"
    if scores["ai_toolflow"] >= max(scores["knowledge_method"], scores["sales_offer"]) and scores["ai_toolflow"] > 0:
        return "ai_toolflow"
    if scores["knowledge_method"] > 0:
        return "knowledge_method"
    if any(token in blob for token in ("工具", "流程", "方法", "框架")):
        return "ai_toolflow" if scores["ai_toolflow"] >= scores["knowledge_method"] else "knowledge_method"
    return "knowledge_method"


def _extract_frontmatter_field(text: str, field_name: str) -> str:
    match = re.match(r"^---\n(.*?)\n---", text, re.S)
    if not match:
        return ""
    block = match.group(1)
    pattern = re.compile(rf"^{re.escape(field_name)}:\s*(.+)$", re.M)
    field_match = pattern.search(block)
    if not field_match:
        return ""
    return field_match.group(1).strip().strip("[]\"'")


def build_visual_strategy_pack(
    *,
    text: str,
    title: str = "",
    script_path: str | None = None,
) -> dict[str, Any]:
    video_type = detect_video_type(text, title=title, script_path=script_path)
    strategy = STRATEGY_DEFS[video_type]
    return {
        **strategy.as_dict(),
        "detected_from": {
            "title": title,
            "script_path": script_path or "",
            "video_type": video_type,
        },
    }


def get_visual_strategy(video_type: str) -> VisualStrategy:
    return STRATEGY_DEFS.get(video_type, STRATEGY_DEFS["knowledge_method"])


def choose_opening_variant(video_type: str, title: str, text: str) -> str:
    strategy = get_visual_strategy(video_type)
    blob = f"{title} {text}"
    if video_type == "sales_offer":
        if any(token in blob for token in ("痛点", "问题", "累", "卡", "难", "不够", "收费", "成本")):
            return "pain_hook"
    if video_type == "ai_toolflow":
        if any(token in blob for token in ("流程", "步骤", "工具", "接进", "自动化", "工作流")):
            return "process_hook"
    if video_type == "knowledge_method":
        if any(token in blob for token in ("为什么", "怎么", "方法", "框架", "步骤", "认知")):
            return "contrast_hook"
    return strategy.opening_variants[0]


def choose_ending_variant(video_type: str) -> str:
    return get_visual_strategy(video_type).ending_variant


def caption_mode_for_scene(video_type: str, role: str, template_type: str, index: int, total: int) -> str:
    strategy = get_visual_strategy(video_type)
    if index == 0:
        return strategy.caption_mode_policy.get("hook", "emphasis_caption")
    if index == max(0, total - 1):
        return strategy.caption_mode_policy.get(role, "action_caption")
    if template_type in {"method_steps", "framework_quadrant", "concept_layers", "knowledge_graph", "progress_tracker"}:
        return strategy.caption_mode_policy.get("method", "minimal_caption")
    if template_type in {"proof", "case_study_card"}:
        return strategy.caption_mode_policy.get("proof", "minimal_caption")
    if role in {"cta", "offer"}:
        return strategy.caption_mode_policy.get("cta", "action_caption")
    if role == "hook":
        return strategy.caption_mode_policy.get("hook", "emphasis_caption")
    return "standard_caption"


def sequence_slot_for_scene(index: int, total: int) -> str:
    if index == 0:
        return "opening"
    if index >= max(0, total - 2):
        return "ending"
    return "middle"


def layout_band_for_scene(video_type: str, role: str, template_type: str, index: int, total: int) -> str:
    if index == 0:
        return "upper"
    if index >= max(0, total - 1):
        return "lower"
    if video_type == "sales_offer" and template_type in {"problem_conflict", "proof", "final_cta"}:
        return "lower"
    if video_type == "ai_toolflow" and template_type in {"tool_stack", "progress_tracker", "method_steps"}:
        return "middle"
    if video_type == "knowledge_method" and template_type in {"framework_quadrant", "concept_layers", "knowledge_graph"}:
        return "middle"
    if role in {"proof", "offer", "verdict"}:
        return "lower"
    return "middle"


def template_sequence_signature(
    *,
    video_type: str,
    opening_variant: str,
    ending_variant: str,
    template_types: list[str],
) -> str:
    return "|".join([video_type, opening_variant, ending_variant, ",".join(template_types)])


def headline_compact(text: str, *, video_type: str, role: str, template_type: str) -> str:
    cleaned = _normalize_text(text)
    if not cleaned:
        return ""

    limit = 18
    if role == "hook":
        limit = 16
    elif video_type == "sales_offer" and role in {"proof", "offer", "cta"}:
        limit = 18
    elif video_type == "ai_toolflow":
        limit = 17
    elif video_type == "knowledge_method":
        limit = 18

    candidates = _headline_candidates(cleaned)
    best = min(candidates, key=lambda item: (_headline_penalty(item, video_type, role, template_type), len(item))) if candidates else cleaned
    compressed = _trim_fillers(best)
    if len(compressed) > limit:
        compressed = compressed[:limit].rstrip("，,。；;:： ")
    return compressed.strip(" ，。；;:：")


def title_caption_similarity(headline: str, caption: str) -> float:
    tokens_a = _tokenize(headline)
    tokens_b = _tokenize(caption)
    if not tokens_a or not tokens_b:
        return 0.0
    overlap = len(tokens_a & tokens_b)
    union = len(tokens_a | tokens_b)
    return round(overlap / union if union else 0.0, 3)


def should_compact_headline(headline: str) -> bool:
    chinese_chars = len(re.findall(r"[\u4e00-\u9fff]", headline))
    mixed_chars = len(headline.strip())
    return chinese_chars > 26 or mixed_chars > 32 or chinese_chars > 18


def _keyword_score(blob: str, keywords: set[str]) -> int:
    return sum(1 for token in keywords if token.lower() in blob)


def _normalize_text(text: str) -> str:
    return re.sub(r"[\n\r]+", " ", str(text or "")).strip()


def _headline_candidates(text: str) -> list[str]:
    parts = [part.strip() for part in re.split(r"[，,。；;：:\s]+", text) if part.strip()]
    if not parts:
        return [text]
    candidates = []
    for idx, part in enumerate(parts):
        candidates.append(part)
        if idx + 1 < len(parts) and len(part) < 10 and len(parts[idx + 1]) < 10:
            candidates.append(f"{part} {parts[idx + 1]}".strip())
    candidates.append("".join(parts[:2]))
    return [item for item in candidates if item]


def _headline_penalty(text: str, video_type: str, role: str, template_type: str) -> tuple[int, int]:
    score = 0
    if video_type == "sales_offer" and role in {"proof", "cta"} and any(token in text for token in ("体验", "领取", "评论区", "私信")):
        score -= 2
    if video_type == "ai_toolflow" and any(token in text for token in ("成交", "购买", "offer")):
        score -= 1
    if video_type == "knowledge_method" and any(token in text for token in ("评论区", "购买", "成交")):
        score -= 1
    if template_type in {"method_steps", "framework_quadrant", "concept_layers", "knowledge_graph"}:
        score += 1
    if role == "hook":
        score += 1
    return score, len(text)


def _trim_fillers(text: str) -> str:
    fillers = ("我把", "终于", "其实", "很多人", "你会", "你就", "一个", "一种", "一下", "真正", "还是", "然后", "再")
    result = _normalize_text(text)
    changed = True
    while changed:
        changed = False
        for filler in fillers:
            if filler in result and len(result) > 8:
                result = result.replace(filler, "", 1)
                changed = True
    result = re.sub(r"\s+", "", result)
    return result


def _tokenize(text: str) -> set[str]:
    normalized = _normalize_text(text).lower()
    tokens = set(re.findall(r"[\u4e00-\u9fffA-Za-z0-9]+", normalized))
    if not tokens and normalized:
        tokens = set(normalized)
    return tokens
