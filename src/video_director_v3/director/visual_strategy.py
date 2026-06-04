"""Visual strategy pack for contract-driven video differentiation."""
from __future__ import annotations

from dataclasses import dataclass, asdict
import re
from typing import Any


VIDEO_TYPES = {"knowledge_method", "ai_toolflow", "sales_offer"}
OPENING_VARIANTS = {"pain_hook", "result_hook", "mistake_hook", "contrast_hook", "process_hook"}
ENDING_VARIANTS = {"insight_close", "homework_close", "action_close", "checklist_close", "offer_close"}
CAPTION_MODES = {"standard_caption", "emphasis_caption", "minimal_caption", "quote_caption", "action_caption"}
LAYOUT_FAMILIES = {
    "hero_statement",
    "hero_metric",
    "process_ladder",
    "tool_pipeline",
    "config_panel",
    "file_tree",
    "comparison_board",
    "proof_matrix",
    "framework_map",
    "decision_fork",
    "opportunity_map",
    "action_close",
    "insight_close",
    "checklist_close",
    "offer_close",
}


@dataclass(frozen=True)
class VisualStrategy:
    strategy_id: str
    video_type: str
    opening_variants: tuple[str, ...]
    preferred_templates: tuple[str, ...]
    avoided_templates: tuple[str, ...]
    layout_families: tuple[str, ...]
    visual_objects: tuple[str, ...]
    memory_anchor_policy: str
    visual_object_policy: str
    save_reason_policy: str
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
        layout_families=("hero_statement", "framework_map", "process_ladder", "insight_close", "checklist_close"),
        visual_objects=("framework_map", "knowledge_graph", "file_tree", "opportunity_map"),
        memory_anchor_policy="prefer concrete method anchors and reusable checkpoints",
        visual_object_policy="prefer framework maps, graphs, and concrete artifacts",
        save_reason_policy="describe why the scene is reusable as a method",
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
        layout_families=("tool_pipeline", "config_panel", "file_tree", "checklist_close", "action_close"),
        visual_objects=("tool_pipeline", "config_panel", "file_tree", "action_card"),
        memory_anchor_policy="prefer concrete toolchains, settings, and workflow nouns",
        visual_object_policy="prefer pipeline, config, and file-tree artifacts",
        save_reason_policy="describe why the workflow is reusable next time",
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
        layout_families=("hero_metric", "proof_matrix", "comparison_board", "offer_close", "action_close"),
        visual_objects=("proof_matrix", "metric_dashboard", "opportunity_map", "decision_fork"),
        memory_anchor_policy="prefer numeric offers, proof anchors, and buying cues",
        visual_object_policy="prefer proof, offer, and metric objects",
        save_reason_policy="describe why the structure helps a future conversion",
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
    opening_variant = choose_opening_variant(video_type, title, text)
    ending_variant = choose_ending_variant(video_type, title=title, text=text, role="cta")
    memory_anchor = build_memory_anchor(text, video_type=video_type, role="hook", template_type="hook")
    visual_object = choose_visual_object(video_type, "hook", "hook", title=title, text=text)
    return {
        **strategy.as_dict(),
        "opening_variant": opening_variant,
        "ending_variant": ending_variant,
        "layout_families": list(strategy.layout_families),
        "visual_objects": list(strategy.visual_objects),
        "memory_anchor": memory_anchor,
        "save_reason": build_save_reason(
            video_type=video_type,
            role="hook",
            template_type="hook",
            memory_anchor=memory_anchor,
            visual_object=visual_object,
        ),
        "visual_object": visual_object,
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


def choose_ending_variant(video_type: str, title: str = "", text: str = "", role: str = "") -> str:
    """Pick an ending grammar that actually changes the closing feel.

    The phase uses a small stable set:
    - knowledge_method -> insight_close / homework_close
    - ai_toolflow -> checklist_close / action_close
    - sales_offer -> offer_close
    """
    strategy = get_visual_strategy(video_type)
    blob = f"{title} {text} {role}"
    if video_type == "knowledge_method":
        if any(token in blob for token in ("练习", "作业", "执行", "跟着做", "动手", "下一步")):
            return "homework_close"
        return "insight_close"
    if video_type == "ai_toolflow":
        if role == "cta":
            return "checklist_close"
        if any(token in blob for token in ("行动", "开始", "马上", "立刻", "执行")):
            return "action_close"
        return "checklist_close"
    if video_type == "sales_offer":
        return "offer_close"
    return strategy.ending_variant


def choose_layout_family(
    video_type: str,
    role: str,
    template_type: str,
    index: int,
    total: int,
    *,
    opening_variant: str = "",
    ending_variant: str = "",
    title: str = "",
    text: str = "",
) -> str:
    """Choose a render-visible layout family for the scene.

    Layout families are intentionally more concrete than template names so
    the same contract template can be displayed with a different frame.
    """
    strategy = get_visual_strategy(video_type)
    is_opening = index == 0
    is_ending = index >= max(0, total - 1)
    blob = f"{title} {text} {role} {template_type}"

    if is_opening:
        if video_type == "knowledge_method":
            return "hero_statement" if "为什么" in blob or "不是" in blob else "framework_map"
        if video_type == "ai_toolflow":
            return "tool_pipeline" if any(token in blob for token in ("工具", "流程", "工作流", "接进")) else "config_panel"
        if video_type == "sales_offer":
            return "hero_metric" if any(token in blob for token in ("数字", "增长", "%", "收入", "成本")) else "opportunity_map"

    if is_ending:
        ending = ending_variant or choose_ending_variant(video_type, title=title, text=text, role=role)
        return {
            "knowledge_method": "insight_close" if ending in {"insight_close", "homework_close"} else "checklist_close",
            "ai_toolflow": "checklist_close" if ending == "checklist_close" else "action_close",
            "sales_offer": "offer_close",
        }.get(video_type, strategy.layout_families[-1])

    if template_type in {"method_steps", "progress_tracker", "tool_stack"}:
        if video_type == "ai_toolflow":
            return {0: "tool_pipeline", 1: "config_panel", 2: "file_tree", 3: "decision_fork"}.get(index % 4, "tool_pipeline")
        return {0: "process_ladder", 1: "framework_map", 2: "comparison_board", 3: "insight_close"}.get(index % 4, "process_ladder")
    if template_type in {"framework_quadrant", "concept_layers", "knowledge_graph"}:
        if video_type == "knowledge_method":
            return {0: "framework_map", 1: "process_ladder", 2: "comparison_board", 3: "insight_close"}.get(index % 4, "framework_map")
        return "framework_map"
    if template_type in {"problem_conflict", "before_after"}:
        if video_type == "sales_offer":
            return {0: "comparison_board", 1: "proof_matrix", 2: "opportunity_map", 3: "decision_fork"}.get(index % 4, "comparison_board")
        return "comparison_board"
    if template_type in {"proof", "case_study_card"}:
        if video_type == "sales_offer":
            return {0: "proof_matrix", 1: "comparison_board", 2: "opportunity_map", 3: "decision_fork"}.get(index % 4, "proof_matrix")
        return {0: "opportunity_map", 1: "framework_map", 2: "comparison_board", 3: "insight_close"}.get(index % 4, "opportunity_map")
    if template_type in {"final_cta", "result_summary"}:
        ending = ending_variant or choose_ending_variant(video_type, title=title, text=text, role=role)
        return {
            "knowledge_method": "insight_close" if ending in {"insight_close", "homework_close"} else "checklist_close",
            "ai_toolflow": "checklist_close" if ending == "checklist_close" else "action_close",
            "sales_offer": "offer_close",
        }.get(video_type, strategy.layout_families[-1])
    if role == "hook":
        return "hero_statement"
    if role in {"offer", "cta", "verdict"}:
        return "action_close" if video_type == "ai_toolflow" else "offer_close"
    return strategy.layout_families[index % len(strategy.layout_families)]


def choose_visual_object(
    video_type: str,
    role: str,
    template_type: str,
    *,
    title: str = "",
    text: str = "",
    index: int = 0,
    total: int = 1,
) -> str:
    blob = f"{title} {text} {role} {template_type}"
    if video_type == "knowledge_method":
        cycle = ("framework_map", "knowledge_graph", "process_ladder", "comparison_board")
        if index == 0 or role == "hook":
            return "framework_map"
        if any(token in blob for token in ("目录", "文件", "树", "路径")):
            return "file_tree"
        if any(token in blob for token in ("结构", "框架", "模型", "层", "体系")):
            return cycle[index % len(cycle)]
        return cycle[index % len(cycle)]
    if video_type == "ai_toolflow":
        cycle = ("tool_pipeline", "config_panel", "file_tree", "workflow_node")
        if index == 0 or role == "hook":
            return "tool_pipeline" if any(token in blob for token in ("工具", "流程", "工作流")) else "config_panel"
        if any(token in blob for token in ("设置", "配置", "参数", "settings.json", "json")):
            return "config_panel"
        if any(token in blob for token in ("目录", "文件", "树", "路径")):
            return "file_tree"
        if any(token in blob for token in ("工具", "工作流", "管线", "流程")):
            return cycle[index % len(cycle)]
        return cycle[index % len(cycle)]
    if video_type == "sales_offer":
        cycle = ("opportunity_map", "proof_matrix", "metric_dashboard", "decision_fork")
        if index == 0 or role == "hook":
            return "opportunity_map" if any(token in blob for token in ("痛点", "问题", "卡", "难", "转化", "成交")) else "metric_dashboard"
        if any(token in blob for token in ("数字", "增长", "%", "收入", "成本", "转化")):
            return cycle[index % len(cycle)]
        if any(token in blob for token in ("证据", "证明", "截图", "记录", "对比")):
            return "proof_matrix"
        return cycle[index % len(cycle)]
    return "artifact_showcase"


def build_memory_anchor(text: str, *, video_type: str, role: str, template_type: str) -> str:
    """Build a sticky, repeatable memory anchor for the scene.

    Prefer concrete objects, counts, file names, or workflow nouns.
    """
    normalized = _normalize_text(text)
    if not normalized:
        return {
            "knowledge_method": "先看再做",
            "ai_toolflow": "输入-整理-调用-输出",
            "sales_offer": "先跑一版最小成交",
        }.get(video_type, "先跑通")

    anchors = [
        r"\d+\s*(?:分钟|秒|小时|天|周|本|条|个|种|倍|%)\s*[\u4e00-\u9fffA-Za-z0-9]{0,8}",
        r"settings\.json",
        r"bypassPermissions",
        r"Obsidian\s*\+\s*Codex\s*\+\s*Hermes",
        r"输入\s*[-→>]\s*整理\s*[-→>]\s*调用\s*[-→>]\s*输出",
        r"看\s*[-→>]\s*筛\s*[-→>]\s*建",
        r"[\u4e00-\u9fff]{2,8}\s*(?:条|个|种|步|层|页|卡|页|板)",
    ]
    for pattern in anchors:
        match = re.search(pattern, normalized)
        if match:
            anchor = match.group(0).strip()
            anchor = re.sub(r"\s+", "", anchor)
            anchor = anchor.replace("→", "-").replace(">", "-")
            if len(anchor) > 16:
                anchor = anchor[:16]
            return anchor

    if video_type == "knowledge_method":
        return _clip("先看再做", 16)
    if video_type == "ai_toolflow":
        return _clip("输入-整理-调用-输出", 16)
    return _clip("先跑一版最小成交", 16)


def build_save_reason(*, video_type: str, role: str, template_type: str, memory_anchor: str, visual_object: str) -> str:
    if video_type == "knowledge_method":
        return _clip(f"可直接复用这个方法锚点：{memory_anchor}", 28)
    if video_type == "ai_toolflow":
        return _clip(f"下次可直接套这条工具链：{memory_anchor}", 28)
    if video_type == "sales_offer":
        return _clip(f"这是一条可直接复用的成交结构：{memory_anchor}", 28)
    return _clip(f"保存这个结构：{visual_object}", 28)


def build_visual_headline(
    text: str,
    *,
    video_type: str,
    role: str,
    template_type: str,
    memory_anchor: str = "",
) -> str:
    """Make a visible headline, not a raw caption prefix."""
    cleaned = _normalize_text(text)
    if not cleaned:
        fallback = {
            "hook": "先抓住这一秒",
            "problem": "问题不是你不努力",
            "conflict": "真正卡住的是入口",
            "method": "把动作接起来",
            "proof": "结果要能看见",
            "offer": "给出可执行下一步",
            "cta": "现在就开始",
            "verdict": "把结论落下来",
        }.get(role, "这一段的重点")
        return _clip(fallback, 18)

    cleaned = _remove_leading_fragments(cleaned)
    if should_compact_headline(cleaned) or len(cleaned) > 20:
        cleaned = headline_compact(cleaned, video_type=video_type, role=role, template_type=template_type)
    cleaned = _trim_fillers(cleaned)
    if _is_fragment_headline(cleaned):
        if memory_anchor:
            anchor_headline = {
                "hook": f"先记住这个点：{memory_anchor}",
                "method": f"把{memory_anchor}接成流程",
                "proof": f"把{memory_anchor}变成证据",
                "cta": f"围绕{memory_anchor}开始执行",
            }.get(role, f"围绕{memory_anchor}开始")
            return _clip(anchor_headline, 18)
        return _clip({
            "hook": "先看这个锚点",
            "method": "把动作接起来",
            "proof": "让结果看得见",
            "cta": "现在开始",
        }.get(role, "先抓住观点"), 18)
    if memory_anchor and len(cleaned) <= 6 and memory_anchor not in cleaned:
        cleaned = f"先记住这个点：{memory_anchor}" if role == "hook" else f"{memory_anchor}，{cleaned}"
    if role == "hook" and memory_anchor and memory_anchor not in cleaned and len(cleaned) < 12:
        cleaned = f"先记住这个点：{memory_anchor}"
    if role == "hook" and memory_anchor and (cleaned.startswith(memory_anchor) or re.match(r"^\d", cleaned)):
        cleaned = f"先记住这个点：{memory_anchor}"
    return _clip(cleaned, 18 if role != "hook" else 16)


def caption_mode_for_scene(
    video_type: str,
    role: str,
    template_type: str,
    index: int,
    total: int,
    *,
    layout_family: str = "",
    ending_variant: str = "",
) -> str:
    strategy = get_visual_strategy(video_type)
    if index == 0:
        return strategy.caption_mode_policy.get("hook", "emphasis_caption")
    if index == max(0, total - 1):
        return strategy.caption_mode_policy.get(role, "action_caption")
    if layout_family in {"hero_statement", "hero_metric"}:
        return "emphasis_caption"
    if layout_family in {"tool_pipeline", "config_panel", "file_tree"}:
        return "minimal_caption"
    if layout_family in {"proof_matrix", "comparison_board", "framework_map"}:
        return "standard_caption"
    if ending_variant in {"offer_close", "action_close"}:
        return "action_caption"
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
    compressed = _remove_leading_fragments(_trim_fillers(best))
    if _is_fragment_headline(compressed):
        compressed = {
            "hook": "先抓住这一秒",
            "problem": "问题不是努力不够",
            "method": "把动作接起来",
            "proof": "结果要能看见",
            "cta": "现在就开始",
        }.get(role, compressed)
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


def _clip(text: str, limit: int) -> str:
    normalized = _normalize_text(text)
    if len(normalized) <= limit:
        return normalized
    return normalized[:limit].rstrip("，,。；;:： ")


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


def _remove_leading_fragments(text: str) -> str:
    result = _normalize_text(text)
    for prefix in ("我把", "以前的流程是", "以前", "之前", "然后", "再"):
        if result.startswith(prefix) and len(result) > len(prefix) + 1:
            result = result[len(prefix):].lstrip(" ，。；;:：")
    result = re.sub(r"^(我把|以前的流程是|以前|之前|然后|再|先)\s*", "", result)
    return result.strip()


def _is_fragment_headline(text: str) -> bool:
    compact = _normalize_text(text)
    if not compact:
        return True
    if compact in {"10", "我把", "以前的流程是", "以前", "之前", "然后", "再", "先"}:
        return True
    if len(compact) <= 2:
        return True
    if compact.startswith(("我把", "以前的流程是", "以前", "之前", "然后", "再")):
        return True
    if compact.isdigit():
        return True
    return False


def _tokenize(text: str) -> set[str]:
    normalized = _normalize_text(text).lower()
    tokens = set(re.findall(r"[\u4e00-\u9fffA-Za-z0-9]+", normalized))
    if not tokens and normalized:
        tokens = set(normalized)
    return tokens
