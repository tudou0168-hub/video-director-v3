"""Scene-framework protocol + 6 seed templates (V3-P3.3 MVP).

Each template defines id, kind, semantic_roles, content_shapes, density,
variables, motion_preset, compatible_transitions, preview_fixture.
Seeded from v3_p28_g1_clean_preview HUD visual_elements.
"""
from __future__ import annotations

from typing import Any

from video_director_v3.motion.component_registry import register_component


HOOK_HERO_CENTER: dict[str, Any] = {
    "id": "scene.hook.hero_center",
    "kind": "scene_framework",
    "render_template": "hook_big_claim",
    "semantic_roles": ["hook", "pain"],
    "content_shapes": ["question", "single_metric", "conflict"],
    "density": "high",
    "variables": ["headline", "subline", "keyword", "accent"],
    "motion_preset": "kinetic_title_burst",
    "compatible_transitions": ["transition.fade_slide_bridge", "transition.scan_reveal"],
    "preview_fixture": {
        "headline": "读得越多 忘得越快",
        "subline": "知识没有消失，只是没有进入可检索的系统",
        "keyword": "记不住",
        "accent": "#FF4757",
    },
}

DENSE_DATA_TABLE: dict[str, Any] = {
    "id": "scene.input.dense_data_table",
    "kind": "scene_framework",
    "render_template": "pain_card_stack",
    "semantic_roles": ["input", "evidence"],
    "content_shapes": ["list", "four_sources", "comparison_table"],
    "density": "high",
    "variables": ["header", "rows", "sync_status", "accent"],
    "motion_preset": "marker_sweep",
    "compatible_transitions": ["transition.scan_reveal", "transition.glow_shift"],
    "preview_fixture": {
        "header": "输入流汇聚状态",
        "rows": [
            {"label": "微信读书笔记", "status": "SYNC"},
            {"label": "网页剪藏", "status": "SYNC"},
            {"label": "语音转写", "status": "SYNC"},
            {"label": "视频笔记", "status": "SYNC"},
        ],
        "accent": "#FBBF24",
    },
}

PROOF_OVERLAY: dict[str, Any] = {
    "id": "scene.memory.proof_overlay",
    "kind": "scene_framework",
    "render_template": "broken_chain",
    "semantic_roles": ["memory", "method", "explain"],
    "content_shapes": ["two_role_split", "responsibility_matrix"],
    "density": "medium",
    "variables": ["headline", "left_label", "right_label", "body", "footer_badge"],
    "motion_preset": "card_stagger",
    "compatible_transitions": ["transition.glow_shift", "transition.slide_bridge"],
    "preview_fixture": {
        "headline": "把记住外包出去",
        "left_label": "大脑",
        "right_label": "Obsidian",
        "body": "思考 创造",
        "footer_badge": "OBSIDIAN = EXTERNAL MEMORY",
        "accent": "#A855F7",
    },
}

PIPELINE_NODES: dict[str, Any] = {
    "id": "scene.retrieval.pipeline_nodes",
    "kind": "scene_framework",
    "render_template": "tool_chain_three_cols",
    "semantic_roles": ["retrieval", "method", "explain"],
    "content_shapes": ["three_step", "flow_chart", "process_chain"],
    "density": "medium",
    "variables": ["headline", "steps", "accent"],
    "motion_preset": "flow_draw",
    "compatible_transitions": ["transition.slide_bridge", "transition.glow_shift"],
    "preview_fixture": {
        "headline": "AI 检索工作流",
        "steps": [
            {"num": "01", "title": "提问", "sub": "自然语言"},
            {"num": "02", "title": "检索", "sub": "Obsidian 笔记"},
            {"num": "03", "title": "整理", "sub": "观点和例子"},
        ],
        "accent": "#A855F7",
    },
}

OPTION_SPLIT_VERTICAL: dict[str, Any] = {
    "id": "scene.compare.option_split_vertical",
    "kind": "scene_framework",
    "render_template": "before_after_compare",
    "semantic_roles": ["compare", "evidence", "proof"],
    "content_shapes": ["before_after", "two_column", "vs_split"],
    "density": "medium",
    "variables": ["headline", "left_label", "left_metric", "right_label", "right_metric", "accent"],
    "motion_preset": "table_stream",
    "compatible_transitions": ["transition.fade_slide_bridge", "transition.scan_reveal"],
    "preview_fixture": {
        "headline": "找素材，不再翻遍所有 App",
        "left_label": "旧方式",
        "left_metric": "翻遍多个 App",
        "right_label": "新方式",
        "right_metric": "30 秒拿到素材包",
        "accent": "#34D399",
    },
}

CHECKLIST_BOARD: dict[str, Any] = {
    "id": "scene.cta.checklist_board",
    "kind": "scene_framework",
    "render_template": "checklist_cta",
    "semantic_roles": ["cta", "ready", "summary"],
    "content_shapes": ["checklist", "three_step_plan", "summary"],
    "density": "medium",
    "variables": ["headline", "items", "final_message", "accent"],
    "motion_preset": "check_pop",
    "compatible_transitions": ["transition.glow_shift", "transition.soft_wipe"],
    "preview_fixture": {
        "headline": "先跑通最小闭环",
        "items": [
            "输入：内容汇聚到 Obsidian",
            "检索：需要时直接问 AI",
            "输出：把素材变成作品",
        ],
        "final_message": "把记住交给第二大脑，把精力留给真正的创造",
        "accent": "#34D399",
    },
}


# ─── P3.3 — 6 new seed templates (method × 2, evidence × 2, proof × 2) ───

METHOD_FRAMEWORK_QUADRANT: dict[str, Any] = {
    "id": "scene.method.framework_quadrant",
    "kind": "scene_framework",
    "render_template": "framework_quadrant",
    "semantic_roles": ["method", "explain"],
    "content_shapes": ["four_quadrant", "matrix_2x2", "framework"],
    "density": "high",
    "variables": ["headline", "quadrants", "center_label", "accent"],
    "motion_preset": "card_stagger",
    "compatible_transitions": ["transition.glow_shift", "transition.slide_bridge"],
    "preview_fixture": {
        "headline": "知识管理的四象限",
        "center_label": "Obsidian",
        "quadrants": [
            {"label": "Q1 收集", "text": "微信 / 网页 / 语音", "color": "#4D9FFF"},
            {"label": "Q2 整理", "text": "双向链接 / 主题页", "color": "#2ED573"},
            {"label": "Q3 检索", "text": "直接问 AI", "color": "#FF6B35"},
            {"label": "Q4 输出", "text": "写作 / 复盘", "color": "#A855F7"},
        ],
        "accent": "#4D9FFF",
    },
}

METHOD_DECISION_TREE: dict[str, Any] = {
    "id": "scene.method.decision_tree",
    "kind": "scene_framework",
    "render_template": "decision_tree",
    "semantic_roles": ["method", "explain"],
    "content_shapes": ["binary_branch", "decision_flow", "criteria"],
    "density": "medium",
    "variables": ["headline", "root_question", "branches", "outcomes", "accent"],
    "motion_preset": "flow_draw",
    "compatible_transitions": ["transition.line_draw_bridge", "transition.slide_bridge"],
    "preview_fixture": {
        "headline": "要不要用 Obsidian",
        "root_question": "你素材 > 1000 条？",
        "branches": [
            {"label": "是", "leads_to": "用 Obsidian 双链管理"},
            {"label": "否", "leads_to": "先用笔记 App 足够"},
        ],
        "outcomes": [
            {"label": "是", "text": "先搭最小闭环", "color": "#2ED573"},
            {"label": "否", "text": "先别上系统", "color": "#FF6B35"},
        ],
        "accent": "#A855F7",
    },
}

EVIDENCE_METRIC_DASHBOARD: dict[str, Any] = {
    "id": "scene.evidence.metric_dashboard",
    "kind": "scene_framework",
    "render_template": "metric_dashboard",
    "semantic_roles": ["evidence", "proof"],
    "content_shapes": ["multi_metric", "kpi_grid", "trend_line"],
    "density": "high",
    "variables": ["headline", "metrics", "trend_caption", "accent"],
    "motion_preset": "count_up",
    "compatible_transitions": ["transition.scan_reveal", "transition.glow_shift"],
    "preview_fixture": {
        "headline": "三个月后的实际数据",
        "metrics": [
            {"label": "日均输出", "value": "3.2 篇", "delta": "+40%"},
            {"label": "素材利用率", "value": "78%", "delta": "+52%"},
            {"label": "检索响应", "value": "12s", "delta": "-65%"},
            {"label": "完播率", "value": "61%", "delta": "+18%"},
        ],
        "trend_caption": "3 个月持续跑通最小闭环",
        "accent": "#2ED573",
    },
}

EVIDENCE_CASE_STUDY_CARD: dict[str, Any] = {
    "id": "scene.evidence.case_study_card",
    "kind": "scene_framework",
    "render_template": "case_study_card",
    "semantic_roles": ["evidence", "example"],
    "content_shapes": ["single_case", "before_after_persona", "highlights"],
    "density": "medium",
    "variables": ["headline", "case_subject", "before", "after", "highlights", "accent"],
    "motion_preset": "card_stagger",
    "compatible_transitions": ["transition.soft_wipe", "transition.glow_shift"],
    "preview_fixture": {
        "headline": "真实案例",
        "case_subject": "李同学 · 知识管理 90 天",
        "before": "笔记散 5 个 App，写一篇要 6 小时",
        "after": "统一到 Obsidian + AI，1.5 小时成稿",
        "highlights": ["整理耗时下降 75%", "素材复用率 3.4×", "AI 草稿接受率 80%"],
        "accent": "#4D9FFF",
    },
}

PROOF_SECTION_BOARD: dict[str, Any] = {
    "id": "scene.proof.section_board",
    "kind": "scene_framework",
    "render_template": "section_board",
    "semantic_roles": ["proof", "summary"],
    "content_shapes": ["four_to_five_panels", "dimension_split", "summary"],
    "density": "medium",
    "variables": ["headline", "sections", "accent"],
    "motion_preset": "panel_slide",
    "compatible_transitions": ["transition.soft_wipe", "transition.slide_bridge"],
    "preview_fixture": {
        "headline": "这一轮的四个判断维度",
        "sections": [
            {"label": "获得感", "text": "学到至少 1 个能用的方法"},
            {"label": "收藏价值", "text": "可以复用的检查清单"},
            {"label": "评论触发", "text": "可执行的下一步动作"},
            {"label": "复看理由", "text": "信息密度足够高"},
        ],
        "accent": "#FF6B35",
    },
}

PROOF_COMMENT_QUESTION: dict[str, Any] = {
    "id": "scene.proof.comment_question",
    "kind": "scene_framework",
    "render_template": "comment_question",
    "semantic_roles": ["proof", "cta"],
    "content_shapes": ["comment_simulation", "guided_question"],
    "density": "medium",
    "variables": ["headline", "fake_comment", "guide_question", "accent"],
    "motion_preset": "quote_reveal",
    "compatible_transitions": ["transition.soft_wipe", "transition.final_hold_fade"],
    "preview_fixture": {
        "headline": "你想先跑通哪一步？",
        "fake_comment": "“我之前用过 3 个笔记 App，最后都放弃了”",
        "guide_question": "你愿意先只保留一个入口吗？评论区告诉我",
        "accent": "#FF4757",
    },
}


SEED_TEMPLATES: list[dict[str, Any]] = [
    HOOK_HERO_CENTER,
    DENSE_DATA_TABLE,
    PROOF_OVERLAY,
    PIPELINE_NODES,
    OPTION_SPLIT_VERTICAL,
    CHECKLIST_BOARD,
    METHOD_FRAMEWORK_QUADRANT,
    METHOD_DECISION_TREE,
    EVIDENCE_METRIC_DASHBOARD,
    EVIDENCE_CASE_STUDY_CARD,
    PROOF_SECTION_BOARD,
    PROOF_COMMENT_QUESTION,
]

TEMPLATE_BY_ID: dict[str, dict[str, Any]] = {
    template["id"]: template for template in SEED_TEMPLATES
}


ROLE_DEFAULT_TEMPLATE: dict[str, str] = {
    "hook": HOOK_HERO_CENTER["id"],
    "pain": DENSE_DATA_TABLE["id"],
    "input": DENSE_DATA_TABLE["id"],
    "memory": PROOF_OVERLAY["id"],
    "method": PIPELINE_NODES["id"],
    "retrieval": PIPELINE_NODES["id"],
    "explain": PROOF_OVERLAY["id"],
    "evidence": OPTION_SPLIT_VERTICAL["id"],
    "proof": OPTION_SPLIT_VERTICAL["id"],
    "compare": OPTION_SPLIT_VERTICAL["id"],
    "cta": CHECKLIST_BOARD["id"],
    "ready": CHECKLIST_BOARD["id"],
    "summary": CHECKLIST_BOARD["id"],
    # P3.3 — explicit seed overrides for method/evidence/proof families
    "framework": METHOD_FRAMEWORK_QUADRANT["id"],
    "decision": METHOD_DECISION_TREE["id"],
    "metric": EVIDENCE_METRIC_DASHBOARD["id"],
    "example": EVIDENCE_CASE_STUDY_CARD["id"],
    "board": PROOF_SECTION_BOARD["id"],
    "comment": PROOF_COMMENT_QUESTION["id"],
}


def register_seed_templates() -> int:
    """Register all 6 seed templates into the global component registry."""
    for template in SEED_TEMPLATES:
        register_component(template["id"], template)
    return len(SEED_TEMPLATES)


def get_template(template_id: str) -> dict[str, Any]:
    from video_director_v3.motion.component_registry import get_component
    return get_component(template_id) or TEMPLATE_BY_ID.get(template_id, {})


def pick_template_for_role(role: str) -> dict[str, Any]:
    template_id = ROLE_DEFAULT_TEMPLATE.get(role, PROOF_OVERLAY["id"])
    return get_template(template_id)
