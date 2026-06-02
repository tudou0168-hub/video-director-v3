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


# ─── P3.4 — 8 new seed templates ───────────────────────────────────────

HOOK_COUNTDOWN_STRIKE: dict[str, Any] = {
    "id": "scene.hook.countdown_strike",
    "kind": "scene_framework",
    "render_template": "countdown_strike",
    "semantic_roles": ["hook", "pain"],
    "content_shapes": ["countdown", "count_down", "urgency"],
    "density": "high",
    "variables": ["headline", "countdown_steps", "final_label", "accent"],
    "motion_preset": "count_up",
    "compatible_transitions": ["transition.scan_reveal", "transition.glow_shift"],
    "preview_fixture": {
        "headline": "你只剩 3 天",
        "countdown_steps": [{"num": "03", "label": "找到入口"}, {"num": "02", "label": "跑通最小"}, {"num": "01", "label": "开始输出"}],
        "final_label": "GO / NOW",
        "accent": "#FF4757",
    },
}

HOOK_KEYWORD_PUNCHLINE: dict[str, Any] = {
    "id": "scene.hook.keyword_punchline",
    "kind": "scene_framework",
    "render_template": "keyword_punchline",
    "semantic_roles": ["hook", "pain"],
    "content_shapes": ["keyword", "single_phrase", "punch"],
    "density": "medium",
    "variables": ["keyword", "punchline", "accent"],
    "motion_preset": "kinetic_title_burst",
    "compatible_transitions": ["transition.glow_shift", "transition.soft_wipe"],
    "preview_fixture": {
        "keyword": "记住",
        "punchline": "不是多一个工具，而是把链路接通",
        "accent": "#FF6B35",
    },
}

PAIN_DATA_DENSE_TABLE: dict[str, Any] = {
    "id": "scene.pain.data_dense_table",
    "kind": "scene_framework",
    "render_template": "data_dense_table",
    "semantic_roles": ["pain", "input"],
    "content_shapes": ["dense_rows", "table", "status_grid"],
    "density": "high",
    "variables": ["headline", "rows", "summary", "accent"],
    "motion_preset": "table_stream",
    "compatible_transitions": ["transition.scan_reveal", "transition.glow_shift"],
    "preview_fixture": {
        "headline": "输入流汇聚状态",
        "rows": [
            {"label": "微信读书笔记", "status": "SYNC", "value": "1,234"},
            {"label": "网页剪藏", "status": "SYNC", "value": "568"},
            {"label": "语音转写", "status": "PENDING", "value": "21"},
            {"label": "视频笔记", "status": "STALE", "value": "12"},
        ],
        "summary": "87% 已同步，13% 待处理",
        "accent": "#FBBF24",
    },
}

METHOD_STEP_LADDER: dict[str, Any] = {
    "id": "scene.method.step_ladder",
    "kind": "scene_framework",
    "render_template": "step_ladder",
    "semantic_roles": ["method", "explain"],
    "content_shapes": ["ladder", "step_progression", "vertical_rungs"],
    "density": "high",
    "variables": ["headline", "steps", "top_label", "accent"],
    "motion_preset": "node_pulse",
    "compatible_transitions": ["transition.line_draw_bridge", "transition.panel_slide_bridge"],
    "preview_fixture": {
        "headline": "从 0 到可用",
        "steps": [
            {"label": "1. 入口", "text": "Obsidian 库"},
            {"label": "2. 链接", "text": "双向链接"},
            {"label": "3. 检索", "text": "AI 提问"},
            {"label": "4. 输出", "text": "草稿 + 复盘"},
        ],
        "top_label": "MILESTONE",
        "accent": "#2ED573",
    },
}

METHOD_CONCEPT_LAYERS: dict[str, Any] = {
    "id": "scene.method.concept_layers",
    "kind": "scene_framework",
    "render_template": "concept_layers",
    "semantic_roles": ["method", "explain"],
    "content_shapes": ["layered_concepts", "pyramid", "abstraction_levels"],
    "density": "medium",
    "variables": ["headline", "layers", "accent"],
    "motion_preset": "graph_rise",
    "compatible_transitions": ["transition.panel_slide_bridge", "transition.glow_shift"],
    "preview_fixture": {
        "headline": "三个层次递进",
        "layers": [
            {"level": "L1", "text": "收集：素材进库"},
            {"level": "L2", "text": "结构：双向链接"},
            {"level": "L3", "text": "调用：AI 提问"},
        ],
        "accent": "#A855F7",
    },
}

EVIDENCE_PROGRESS_TRACKER: dict[str, Any] = {
    "id": "scene.evidence.progress_tracker",
    "kind": "scene_framework",
    "render_template": "progress_tracker",
    "semantic_roles": ["evidence", "proof"],
    "content_shapes": ["progress_bars", "multi_track", "weekly_trend"],
    "density": "high",
    "variables": ["headline", "tracks", "caption", "accent"],
    "motion_preset": "graph_rise",
    "compatible_transitions": ["transition.scan_reveal", "transition.glow_shift"],
    "preview_fixture": {
        "headline": "8 周能力曲线",
        "tracks": [
            {"label": "输入", "weeks": [20, 35, 50, 60, 70, 78, 85, 90]},
            {"label": "检索", "weeks": [10, 25, 45, 60, 72, 80, 88, 93]},
            {"label": "输出", "weeks": [5, 18, 35, 50, 62, 75, 85, 92]},
        ],
        "caption": "8 周跑通最小闭环后，三条曲线同步进入加速段",
        "accent": "#4D9FFF",
    },
}

PROOF_KNOWLEDGE_GRAPH: dict[str, Any] = {
    "id": "scene.proof.knowledge_graph",
    "kind": "scene_framework",
    "render_template": "knowledge_graph",
    "semantic_roles": ["proof", "summary"],
    "content_shapes": ["node_graph", "relation_map", "centrality"],
    "density": "high",
    "variables": ["headline", "nodes", "edges", "central_node", "accent"],
    "motion_preset": "graph_rise",
    "compatible_transitions": ["transition.soft_wipe", "transition.glow_shift"],
    "preview_fixture": {
        "headline": "三个月后你的知识网络",
        "nodes": [
            {"id": "N1", "label": "时间管理", "x": 540, "y": 800},
            {"id": "N2", "label": "GTD", "x": 250, "y": 500},
            {"id": "N3", "label": "番茄钟", "x": 830, "y": 500},
            {"id": "N4", "label": "Obsidian", "x": 540, "y": 400},
            {"id": "N5", "label": "AI 提问", "x": 250, "y": 1100},
            {"id": "N6", "label": "写作复盘", "x": 830, "y": 1100},
        ],
        "edges": [("N1","N2"), ("N1","N3"), ("N1","N4"), ("N2","N5"), ("N3","N6"), ("N4","N5"), ("N4","N6")],
        "central_node": "N1",
        "accent": "#A855F7",
    },
}

CTA_QUOTE_CLOSE: dict[str, Any] = {
    "id": "scene.cta.quote_close",
    "kind": "scene_framework",
    "render_template": "quote_close",
    "semantic_roles": ["cta", "ready", "summary"],
    "content_shapes": ["quote_card", "single_phrase", "closing"],
    "density": "low",
    "variables": ["quote", "attribution", "action", "accent"],
    "motion_preset": "quote_reveal",
    "compatible_transitions": ["transition.final_hold_fade", "transition.soft_wipe"],
    "preview_fixture": {
        "quote": "记住，是把素材变成自己的过程。",
        "attribution": "— 第二大脑实践 90 天",
        "action": "先跑通最小闭环，评论区告诉我你的第一步",
        "accent": "#34D399",
    },
}


# ─── P3.5 — 10 new seed templates (final 30-asset target) ─────────────

HOOK_MYTH_BUST: dict[str, Any] = {
    "id": "scene.hook.myth_bust",
    "kind": "scene_framework",
    "render_template": "myth_bust",
    "semantic_roles": ["hook", "pain"],
    "content_shapes": ["myth_vs_truth", "strikethrough", "correction"],
    "density": "high",
    "variables": ["headline", "myth", "truth", "accent"],
    "motion_preset": "kinetic_title_burst",
    "compatible_transitions": ["transition.glow_shift", "transition.scan_reveal"],
    "preview_fixture": {
        "headline": "大部分人都搞错了",
        "myth": "多装插件就能提高效率",
        "truth": "先跑通最小闭环再说",
        "accent": "#FF4757",
    },
}

HOOK_BEFORE_AFTER_FLASH: dict[str, Any] = {
    "id": "scene.hook.before_after_flash",
    "kind": "scene_framework",
    "render_template": "before_after_flash",
    "semantic_roles": ["hook", "evidence"],
    "content_shapes": ["flash_compare", "split_frame", "impact_moment"],
    "density": "high",
    "variables": ["before_metric", "after_metric", "metric_label", "accent"],
    "motion_preset": "count_up",
    "compatible_transitions": ["transition.scan_reveal", "transition.glow_shift"],
    "preview_fixture": {
        "before_metric": "5h",
        "after_metric": "40m",
        "metric_label": "找素材时间",
        "accent": "#2ED573",
    },
}

PAIN_TIMELINE_PAIN: dict[str, Any] = {
    "id": "scene.pain.timeline_pain",
    "kind": "scene_framework",
    "render_template": "timeline_pain",
    "semantic_roles": ["pain", "summary"],
    "content_shapes": ["timeline_horizon", "pain_points_over_time", "accumulation"],
    "density": "high",
    "variables": ["headline", "events", "conclusion", "accent"],
    "motion_preset": "marker_sweep",
    "compatible_transitions": ["transition.scan_reveal", "transition.glow_shift"],
    "preview_fixture": {
        "headline": "三个月没整理的代价",
        "events": [
            {"week": "W1", "text": "笔记散 5 个 App", "severity": "LOW"},
            {"week": "W4", "text": "素材找不到，想用时空白", "severity": "MID"},
            {"week": "W8", "text": "开始怀疑记笔记的意义", "severity": "HIGH"},
            {"week": "W12", "text": "放弃，开始纯靠脑子", "severity": "CRIT"},
        ],
        "conclusion": "信息过载不是记不住，是没结构",
        "accent": "#FF6B35",
    },
}

METHOD_TIMELINE_PATH: dict[str, Any] = {
    "id": "scene.method.timeline_path",
    "kind": "scene_framework",
    "render_template": "timeline_path",
    "semantic_roles": ["method", "explain"],
    "content_shapes": ["timeline_horizon", "step_milestones", "progress"],
    "density": "high",
    "variables": ["headline", "milestones", "top_label", "accent"],
    "motion_preset": "node_pulse",
    "compatible_transitions": ["transition.line_draw_bridge", "transition.panel_slide_bridge"],
    "preview_fixture": {
        "headline": "90 天建立第二大脑",
        "milestones": [
            {"week": "W1-W2", "text": "统一入口"},
            {"week": "W3-W4", "text": "建结构"},
            {"week": "W5-W8", "text": "跑通检索"},
            {"week": "W9-W12", "text": "持续输出"},
        ],
        "top_label": "ROADMAP",
        "accent": "#4D9FFF",
    },
}

METHOD_TOOL_STACK: dict[str, Any] = {
    "id": "scene.method.tool_stack",
    "kind": "scene_framework",
    "render_template": "tool_stack",
    "semantic_roles": ["method", "explain"],
    "content_shapes": ["stacked_layers", "tool_pyramid", "stack_visualization"],
    "density": "medium",
    "variables": ["headline", "stack_layers", "accent"],
    "motion_preset": "graph_rise",
    "compatible_transitions": ["transition.panel_slide_bridge", "transition.glow_shift"],
    "preview_fixture": {
        "headline": "三件套搭起来",
        "stack_layers": [
            {"name": "Obsidian", "role": "存储", "color": "#7C3AED"},
            {"name": "Codex", "role": "整理", "color": "#4D9FFF"},
            {"name": "Hermes", "role": "复盘", "color": "#2ED573"},
        ],
        "accent": "#A855F7",
    },
}

EVIDENCE_CASE_STUDY: dict[str, Any] = {
    "id": "scene.evidence.case_study",
    "kind": "scene_framework",
    "render_template": "case_study",
    "semantic_roles": ["evidence", "example"],
    "content_shapes": ["single_case", "metrics_3", "outcome"],
    "density": "medium",
    "variables": ["headline", "case_label", "metrics", "outcome", "accent"],
    "motion_preset": "card_stagger",
    "compatible_transitions": ["transition.soft_wipe", "transition.glow_shift"],
    "preview_fixture": {
        "headline": "真实案例 · 知识管理 90 天",
        "case_label": "李同学 / 设计师 / 自由职业",
        "metrics": [
            {"label": "整理耗时", "value": "-75%"},
            {"label": "素材复用", "value": "3.4×"},
            {"label": "完稿速度", "value": "+200%"},
        ],
        "outcome": "从 1 篇/周到 3 篇/周，质量反而更稳",
        "accent": "#4D9FFF",
    },
}

EVIDENCE_CARDS: dict[str, Any] = {
    "id": "scene.evidence.evidence_cards",
    "kind": "scene_framework",
    "render_template": "evidence_cards",
    "semantic_roles": ["evidence", "proof"],
    "content_shapes": ["card_grid_2x2", "evidence_pills", "multi_proof"],
    "density": "high",
    "variables": ["headline", "cards", "caption", "accent"],
    "motion_preset": "card_stagger",
    "compatible_transitions": ["transition.glow_shift", "transition.soft_wipe"],
    "preview_fixture": {
        "headline": "四项独立证据",
        "cards": [
            {"label": "测试 1", "text": "素材利用率 ↑ 78%"},
            {"label": "测试 2", "text": "完播率 ↑ 61%"},
            {"label": "测试 3", "text": "复盘耗时 ↓ 65%"},
            {"label": "测试 4", "text": "草稿接受率 80%"},
        ],
        "caption": "三个独立测试都指向同一结论",
        "accent": "#2ED573",
    },
}

PROOF_SCORE_PANEL: dict[str, Any] = {
    "id": "scene.proof.score_panel",
    "kind": "scene_framework",
    "render_template": "score_panel",
    "semantic_roles": ["proof", "summary"],
    "content_shapes": ["score_breakdown", "criteria_panel", "verdict"],
    "density": "medium",
    "variables": ["headline", "criteria", "verdict", "accent"],
    "motion_preset": "count_up",
    "compatible_transitions": ["transition.soft_wipe", "transition.final_hold_fade"],
    "preview_fixture": {
        "headline": "这一轮的得分",
        "criteria": [
            {"name": "内容", "score": 9, "max": 10},
            {"name": "节奏", "score": 8, "max": 10},
            {"name": "结构", "score": 9, "max": 10},
            {"name": "互动", "score": 7, "max": 10},
        ],
        "verdict": "PASS / 已可发布",
        "accent": "#34D399",
    },
}

PROOF_NEXT_STEP_BOARD: dict[str, Any] = {
    "id": "scene.proof.next_step_board",
    "kind": "scene_framework",
    "render_template": "next_step_board",
    "semantic_roles": ["proof", "summary", "cta"],
    "content_shapes": ["next_steps_list", "action_plan", "do_this_next"],
    "density": "medium",
    "variables": ["headline", "next_steps", "accent"],
    "motion_preset": "check_pop",
    "compatible_transitions": ["transition.soft_wipe", "transition.final_hold_fade"],
    "preview_fixture": {
        "headline": "下一步你做哪一步？",
        "next_steps": [
            {"label": "1", "text": "选一个入口 App"},
            {"label": "2", "text": "把 10 条素材搬进去"},
            {"label": "3", "text": "建立 3 个主题页"},
            {"label": "4", "text": "问 AI 一个真实问题"},
        ],
        "accent": "#FF6B35",
    },
}

CTA_COMMENT_INVITE: dict[str, Any] = {
    "id": "scene.cta.comment_invite",
    "kind": "scene_framework",
    "render_template": "comment_invite",
    "semantic_roles": ["cta", "comment"],
    "content_shapes": ["comment_invitation", "engagement_card", "simple_cta"],
    "density": "low",
    "variables": ["headline", "question", "action", "accent"],
    "motion_preset": "quote_reveal",
    "compatible_transitions": ["transition.soft_wipe", "transition.final_hold_fade"],
    "preview_fixture": {
        "headline": "评论区告诉我",
        "question": "你愿意先只保留一个入口吗？",
        "action": "评论 / 点赞 / 收藏 / 转发",
        "accent": "#FF4757",
    },
}


# ─── P3.4 — 6 new motion presets + 4 new transitions ───────────────────

# Motion presets (used by scene variables) — protocol only; actual GSAP
# strings live in publish_templates._GSAP_FUNCTIONS.
MOTION_PRESETS: dict[str, dict[str, str]] = {
    "kinetic_title_burst": {"kind": "burst", "intensity": "high", "trigger": "scene_enter"},
    "marker_sweep": {"kind": "sweep", "intensity": "medium", "trigger": "key_word"},
    "card_stagger": {"kind": "stagger", "intensity": "medium", "trigger": "scene_enter"},
    "count_up": {"kind": "counter", "intensity": "high", "trigger": "metric_reveal"},
    "flow_draw": {"kind": "draw", "intensity": "medium", "trigger": "node_connect"},
    "table_stream": {"kind": "stream", "intensity": "medium", "trigger": "row_reveal"},
    "node_pulse": {"kind": "pulse", "intensity": "high", "trigger": "step_reveal"},
    "graph_rise": {"kind": "rise", "intensity": "medium", "trigger": "bar_reveal"},
    "quote_reveal": {"kind": "reveal", "intensity": "low", "trigger": "phrase_reveal"},
    # P3.5 — 5 new motion presets (final 14-asset target)
    "parallax_drift": {"kind": "drift", "intensity": "low", "trigger": "scroll_like"},
    "scan_focus": {"kind": "focus", "intensity": "high", "trigger": "key_metric"},
    "depth_push": {"kind": "depth", "intensity": "medium", "trigger": "stack_reveal"},
    "glow_breathe": {"kind": "breathe", "intensity": "low", "trigger": "ambient"},
    "check_pop": {"kind": "pop", "intensity": "medium", "trigger": "checklist_reveal"},
}

# Transition catalog (referenced by scene.compatible_transitions).
TRANSITIONS: dict[str, dict[str, str]] = {
    "transition.glow_shift": {"kind": "crossfade", "duration": "0.4s"},
    "transition.fade_slide_bridge": {"kind": "bridge", "duration": "0.5s"},
    "transition.scan_reveal": {"kind": "wipe", "duration": "0.3s"},
    "transition.slide_bridge": {"kind": "bridge", "duration": "0.4s"},
    "transition.soft_wipe": {"kind": "wipe", "duration": "0.5s"},
    "transition.line_draw_bridge": {"kind": "draw", "duration": "0.4s"},
    "transition.panel_slide_bridge": {"kind": "bridge", "duration": "0.45s"},
    "transition.final_hold_fade": {"kind": "hold_fade", "duration": "0.6s"},
    "transition.cards_to_flow": {"kind": "morph", "duration": "0.4s"},
    "transition.flow_to_table": {"kind": "morph", "duration": "0.4s"},
    "transition.metric_to_compare": {"kind": "morph", "duration": "0.4s"},
    "transition.radial_focus_shift": {"kind": "focus", "duration": "0.5s"},
    "transition.zoom_through": {"kind": "zoom", "duration": "0.4s"},
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
    HOOK_COUNTDOWN_STRIKE,
    HOOK_KEYWORD_PUNCHLINE,
    PAIN_DATA_DENSE_TABLE,
    METHOD_STEP_LADDER,
    METHOD_CONCEPT_LAYERS,
    EVIDENCE_PROGRESS_TRACKER,
    PROOF_KNOWLEDGE_GRAPH,
    CTA_QUOTE_CLOSE,
    HOOK_MYTH_BUST,
    HOOK_BEFORE_AFTER_FLASH,
    PAIN_TIMELINE_PAIN,
    METHOD_TIMELINE_PATH,
    METHOD_TOOL_STACK,
    EVIDENCE_CASE_STUDY,
    EVIDENCE_CARDS,
    PROOF_SCORE_PANEL,
    PROOF_NEXT_STEP_BOARD,
    CTA_COMMENT_INVITE,
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
    # P3.4 — new seed overrides
    "countdown": HOOK_COUNTDOWN_STRIKE["id"],
    "punchline": HOOK_KEYWORD_PUNCHLINE["id"],
    "table": PAIN_DATA_DENSE_TABLE["id"],
    "ladder": METHOD_STEP_LADDER["id"],
    "layers": METHOD_CONCEPT_LAYERS["id"],
    "progress": EVIDENCE_PROGRESS_TRACKER["id"],
    "graph": PROOF_KNOWLEDGE_GRAPH["id"],
    "close": CTA_QUOTE_CLOSE["id"],
    # P3.5 — final 10 new seed overrides (30 total)
    "myth": HOOK_MYTH_BUST["id"],
    "flash": HOOK_BEFORE_AFTER_FLASH["id"],
    "timeline_pain": PAIN_TIMELINE_PAIN["id"],
    "roadmap": METHOD_TIMELINE_PATH["id"],
    "stack": METHOD_TOOL_STACK["id"],
    "case": EVIDENCE_CASE_STUDY["id"],
    "evidence_cards": EVIDENCE_CARDS["id"],
    "score": PROOF_SCORE_PANEL["id"],
    "next_step": PROOF_NEXT_STEP_BOARD["id"],
    "comment_invite": CTA_COMMENT_INVITE["id"],
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


# ─── V3-P3.8 — Per-role render_template rotation pools ──────────
# When `_assign_visual_templates` cannot find a keyword override for a
# scene's role + narration, it falls back to the per-role pool below
# instead of the single ROLE_DEFAULT_TEMPLATE entry. The pool is rotated
# by scene index so consecutive scenes with the same role get distinct
# visual templates (the dominant "same-skeleton × N" issue in the
# 2026-05-26 acceptance run).

RENDER_TEMPLATE_POOLS: dict[str, list[str]] = {
    "explain": [
        "broken_chain",
        "concept_layers",
        "knowledge_graph",
        "myth_bust",
        "framework_quadrant",
    ],
    "evidence": [
        "before_after_compare",
        "metric_dashboard",
        "progress_tracker",
        "case_study_card",
        "section_board",
        "data_dense_table",
    ],
    "method": [
        "tool_chain_three_cols",
        "step_ladder",
        "framework_quadrant",
        "concept_layers",
    ],
}

# Reverse lookup from render_template → seed_id, so callers can convert
# a rotated render_template string back into the full template dict
# (needed for accent / density / preview_fixture).
RENDER_TEMPLATE_TO_SEED_ID: dict[str, str] = {
    "broken_chain": PROOF_OVERLAY["id"],
    "concept_layers": METHOD_CONCEPT_LAYERS["id"],
    "knowledge_graph": PROOF_KNOWLEDGE_GRAPH["id"],
    "myth_bust": HOOK_MYTH_BUST["id"],
    "framework_quadrant": METHOD_FRAMEWORK_QUADRANT["id"],
    "before_after_compare": OPTION_SPLIT_VERTICAL["id"],
    "metric_dashboard": EVIDENCE_METRIC_DASHBOARD["id"],
    "progress_tracker": EVIDENCE_PROGRESS_TRACKER["id"],
    "case_study_card": EVIDENCE_CASE_STUDY_CARD["id"],
    "section_board": PROOF_SECTION_BOARD["id"],
    "data_dense_table": PAIN_DATA_DENSE_TABLE["id"],
    "tool_chain_three_cols": PIPELINE_NODES["id"],
    "step_ladder": METHOD_STEP_LADDER["id"],
}


def pick_render_template_for_role(role: str, index: int = 0) -> str | None:
    """Return a render_template string for `role` rotated by `index` mod pool size.

    Returns None when `role` has no rotation pool — caller should fall back
    to `pick_template_for_role(role)`. Layer 1 of the V3-P3.8 anti-repetition
    scheme (see plan §4.1).
    """
    pool = RENDER_TEMPLATE_POOLS.get(role)
    if not pool:
        return None
    return pool[index % len(pool)]


# V3-P3.8R1 — single source of truth for the V3-P3.8 feature gate.
# `design_variance < 5` → legacy deterministic (no Layer 1 rotation,
# no Layer 2 fallback, no last-scene CTA default).
# `design_variance >= 5` → all V3-P3.8 visual-quality features on.
# This function is the ONLY place in the codebase that decides whether
# V3-P3.8 features fire. Layer 1, Layer 2, and the last-scene CTA
# default all consult this same function.
V3_P38_FEATURE_THRESHOLD = 5


def should_enable_v3_p38_features(design_variance: int) -> bool:
    """Single source of truth for the V3-P3.8 feature gate.

    `design_variance < 5` → legacy deterministic behavior.
    `design_variance >= 5` → all V3-P3.8 features (Layer 1 rotation,
    Layer 2 fallback, last-scene CTA = end_score_goodbye) are enabled.
    """
    return design_variance >= V3_P38_FEATURE_THRESHOLD
