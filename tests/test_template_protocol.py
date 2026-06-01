"""Test P3.2.1: scene_framework protocol + 20 seed templates (P3.4)."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from video_director_v3.motion.component_registry import (
    COMPONENT_REGISTRY,
    clear_registry,
    list_components,
)
from video_director_v3.templates.scene_protocol import (
    ROLE_DEFAULT_TEMPLATE,
    SEED_TEMPLATES,
    MOTION_PRESETS,
    TRANSITIONS,
    get_template,
    pick_template_for_role,
    register_seed_templates,
)


REQUIRED_TEMPLATE_IDS = {
    # P3.2 batch 1
    "scene.hook.hero_center",
    "scene.input.dense_data_table",
    "scene.memory.proof_overlay",
    "scene.retrieval.pipeline_nodes",
    "scene.compare.option_split_vertical",
    "scene.cta.checklist_board",
    # P3.3
    "scene.method.framework_quadrant",
    "scene.method.decision_tree",
    "scene.evidence.metric_dashboard",
    "scene.evidence.case_study_card",
    "scene.proof.section_board",
    "scene.proof.comment_question",
    # P3.4
    "scene.hook.countdown_strike",
    "scene.hook.keyword_punchline",
    "scene.pain.data_dense_table",
    "scene.method.step_ladder",
    "scene.method.concept_layers",
    "scene.evidence.progress_tracker",
    "scene.proof.knowledge_graph",
    "scene.cta.quote_close",
}


def test_seed_template_count_is_twenty():
    assert len(SEED_TEMPLATES) == 20, f"expected 20 seeds, got {len(SEED_TEMPLATES)}"


def test_register_seed_templates_populates_registry():
    clear_registry()
    n = register_seed_templates()
    assert n == 20
    assert set(list_components()) == REQUIRED_TEMPLATE_IDS


def test_each_seed_has_protocol_fields():
    clear_registry()
    register_seed_templates()
    required = {"id", "kind", "semantic_roles", "content_shapes", "density",
                "variables", "motion_preset", "compatible_transitions", "preview_fixture", "render_template"}
    for tid in REQUIRED_TEMPLATE_IDS:
        spec = COMPONENT_REGISTRY[tid]
        missing = required - set(spec.keys())
        assert not missing, f"{tid} missing fields: {missing}"
        assert spec["kind"] == "scene_framework"
        assert spec["density"] in {"low", "medium", "high"}
        assert spec["render_template"], f"{tid} missing render_template"


def test_role_routing_covers_main_pipeline_roles():
    clear_registry()
    register_seed_templates()
    roles = [
        "hook", "pain", "input", "memory", "method", "retrieval",
        "explain", "evidence", "proof", "compare", "cta", "ready", "summary",
        "framework", "decision", "metric", "example", "board", "comment",
        "countdown", "punchline", "table", "ladder", "layers", "progress", "graph", "close",
    ]
    for role in roles:
        tpl = pick_template_for_role(role)
        assert tpl, f"role {role!r} got empty template"
        assert tpl["id"] in REQUIRED_TEMPLATE_IDS, f"role {role} routed to {tpl['id']!r} not in seed set"


def test_hook_routes_to_hero_center():
    clear_registry()
    register_seed_templates()
    assert pick_template_for_role("hook")["id"] == "scene.hook.hero_center"
    assert pick_template_for_role("cta")["id"] == "scene.cta.checklist_board"
    assert pick_template_for_role("retrieval")["id"] == "scene.retrieval.pipeline_nodes"
    # P3.3 explicit overrides
    assert pick_template_for_role("framework")["id"] == "scene.method.framework_quadrant"
    assert pick_template_for_role("decision")["id"] == "scene.method.decision_tree"
    assert pick_template_for_role("metric")["id"] == "scene.evidence.metric_dashboard"
    assert pick_template_for_role("example")["id"] == "scene.evidence.case_study_card"
    assert pick_template_for_role("board")["id"] == "scene.proof.section_board"
    assert pick_template_for_role("comment")["id"] == "scene.proof.comment_question"
    # P3.4 explicit overrides
    assert pick_template_for_role("countdown")["id"] == "scene.hook.countdown_strike"
    assert pick_template_for_role("punchline")["id"] == "scene.hook.keyword_punchline"
    assert pick_template_for_role("table")["id"] == "scene.pain.data_dense_table"
    assert pick_template_for_role("ladder")["id"] == "scene.method.step_ladder"
    assert pick_template_for_role("layers")["id"] == "scene.method.concept_layers"
    assert pick_template_for_role("progress")["id"] == "scene.evidence.progress_tracker"
    assert pick_template_for_role("graph")["id"] == "scene.proof.knowledge_graph"
    assert pick_template_for_role("close")["id"] == "scene.cta.quote_close"


def test_compatible_transitions_mention_known_set():
    clear_registry()
    register_seed_templates()
    for spec in SEED_TEMPLATES:
        for t in spec["compatible_transitions"]:
            assert t.startswith("transition."), f"{spec['id']} bad transition: {t}"


def test_unknown_role_falls_back_to_proof_overlay():
    clear_registry()
    register_seed_templates()
    assert pick_template_for_role("totally_unknown_role")["id"] == "scene.memory.proof_overlay"


def test_role_default_template_map_consistent():
    for role, tid in ROLE_DEFAULT_TEMPLATE.items():
        assert tid in REQUIRED_TEMPLATE_IDS, f"role {role!r} maps to unknown template {tid!r}"


# ─── P3.4 — protocol & motion/transitions coverage ───

def test_motion_presets_catalog_has_nine_entries():
    assert len(MOTION_PRESETS) == 9, f"expected 9 motion presets, got {len(MOTION_PRESETS)}"


def test_motion_presets_all_have_required_fields():
    for name, spec in MOTION_PRESETS.items():
        assert "kind" in spec
        assert "intensity" in spec
        assert "trigger" in spec
        assert spec["intensity"] in {"low", "medium", "high"}


def test_transitions_catalog_has_at_least_seven():
    assert len(TRANSITIONS) >= 7, f"expected >=7 transitions, got {len(TRANSITIONS)}"


def test_transitions_all_have_required_fields():
    for name, spec in TRANSITIONS.items():
        assert "kind" in spec
        assert "duration" in spec


# ─── P3.3 — narration-driven seed routing tests ───

def test_method_routes_to_framework_quadrant_by_keyword():
    from video_director_v3.director.storyboard_builder import _pick_seed_id
    assert _pick_seed_id("method", "这四个象限分别对应不同的处理阶段") == "scene.method.framework_quadrant"
    assert _pick_seed_id("method", "知识管理矩阵") == "scene.method.framework_quadrant"


def test_method_routes_to_decision_tree_by_keyword():
    from video_director_v3.director.storyboard_builder import _pick_seed_id
    assert _pick_seed_id("method", "你要不要先做这一步？") == "scene.method.decision_tree"
    assert _pick_seed_id("method", "是否现在就开始取决于你的现状") == "scene.method.decision_tree"


def test_evidence_routes_to_metric_dashboard_by_keyword():
    from video_director_v3.director.storyboard_builder import _pick_seed_id
    assert _pick_seed_id("evidence", "效率提升 40%") == "scene.evidence.metric_dashboard"
    assert _pick_seed_id("evidence", "完播率指标 61%") == "scene.evidence.metric_dashboard"


def test_evidence_routes_to_case_study_by_keyword():
    from video_director_v3.director.storyboard_builder import _pick_seed_id
    assert _pick_seed_id("evidence", "李同学用了一周就上手") == "scene.evidence.case_study_card"
    assert _pick_seed_id("evidence", "这位博主做到了") == "scene.evidence.case_study_card"


def test_proof_routes_to_section_board_by_keyword():
    from video_director_v3.director.storyboard_builder import _pick_seed_id
    assert _pick_seed_id("proof", "从三个维度来判断") == "scene.proof.section_board"
    assert _pick_seed_id("proof", "这次有四条判断标准") == "scene.proof.section_board"


def test_proof_routes_to_comment_question_by_keyword():
    from video_director_v3.director.storyboard_builder import _pick_seed_id
    assert _pick_seed_id("proof", "你愿意先跑通最小闭环吗？") == "scene.proof.comment_question"
    assert _pick_seed_id("proof", "评论区告诉我你的状态") == "scene.proof.comment_question"


def test_unmatched_method_falls_back_to_pipeline_nodes():
    from video_director_v3.director.storyboard_builder import _pick_seed_id
    assert _pick_seed_id("method", "先把输入统一到一个入口") == "scene.retrieval.pipeline_nodes"


# ─── P3.4 — 8 new narration-driven seed routing tests ───

def test_hook_routes_to_countdown_strike_by_keyword():
    from video_director_v3.director.storyboard_builder import _pick_seed_id
    assert _pick_seed_id("hook", "你只剩 3 天时间了") == "scene.hook.countdown_strike"
    assert _pick_seed_id("hook", "最后几天决定一切") == "scene.hook.countdown_strike"


def test_hook_routes_to_keyword_punchline_by_keyword():
    from video_director_v3.director.storyboard_builder import _pick_seed_id
    assert _pick_seed_id("hook", "重点是：把链路接通") == "scene.hook.keyword_punchline"
    assert _pick_seed_id("hook", "记住一个核心") == "scene.hook.keyword_punchline"


def test_pain_routes_to_data_dense_table_by_keyword():
    from video_director_v3.director.storyboard_builder import _pick_seed_id
    assert _pick_seed_id("pain", "看输入流的状态列表") == "scene.pain.data_dense_table"
    assert _pick_seed_id("pain", "这些素材现在什么状态") == "scene.pain.data_dense_table"


def test_method_routes_to_step_ladder_by_keyword():
    from video_director_v3.director.storyboard_builder import _pick_seed_id
    assert _pick_seed_id("method", "从 0 到可用，你需要 4 步") == "scene.method.step_ladder"
    assert _pick_seed_id("method", "把流程做成阶梯") == "scene.method.step_ladder"


def test_method_routes_to_concept_layers_by_keyword():
    from video_director_v3.director.storyboard_builder import _pick_seed_id
    assert _pick_seed_id("method", "三个层次递进：L1 收集 / L2 结构 / L3 调用") == "scene.method.concept_layers"
    assert _pick_seed_id("method", "层层深入每一层") == "scene.method.concept_layers"


def test_evidence_routes_to_progress_tracker_by_keyword():
    from video_director_v3.director.storyboard_builder import _pick_seed_id
    assert _pick_seed_id("evidence", "8 周能力曲线变化") == "scene.evidence.progress_tracker"
    assert _pick_seed_id("evidence", "每周的进度跟踪") == "scene.evidence.progress_tracker"


def test_proof_routes_to_knowledge_graph_by_keyword():
    from video_director_v3.director.storyboard_builder import _pick_seed_id
    assert _pick_seed_id("proof", "你的知识网络节点关系") == "scene.proof.knowledge_graph"
    assert _pick_seed_id("proof", "看这个知识图谱") == "scene.proof.knowledge_graph"


def test_cta_routes_to_quote_close_by_keyword():
    from video_director_v3.director.storyboard_builder import _pick_seed_id
    assert _pick_seed_id("cta", "用一句话总结一下") == "scene.cta.quote_close"
    assert _pick_seed_id("cta", "最后一句金句送给你") == "scene.cta.quote_close"


# ─── P3.4 — 8 new render-distinct & data-helper tests ───

def test_eight_new_renderers_produce_visually_distinct_html():
    from video_director_v3.renderers.hyperframes.publish_templates import get_scene_body
    templates = [
        "countdown_strike", "keyword_punchline", "data_dense_table",
        "step_ladder", "concept_layers", "progress_tracker",
        "knowledge_graph", "quote_close",
    ]
    htmls = {t: get_scene_body("S01", "method", {"visual_template": t}) for t in templates}
    assert len(set(htmls.values())) == 8, "Some P3.4 templates produced identical HTML"
    assert "countdown-row" in htmls["countdown_strike"]
    assert "KEYWORD / PUNCH" in htmls["keyword_punchline"]
    assert "data-row" in htmls["data_dense_table"]
    assert "ladder-rung" in htmls["step_ladder"]
    assert "layer-bar" in htmls["concept_layers"]
    assert "progress-bar" in htmls["progress_tracker"]
    assert "kg-node" in htmls["knowledge_graph"]
    assert "QUOTE / CLOSE" in htmls["quote_close"]


def test_hud_scene_config_supplies_data_for_each_p34_template():
    from video_director_v3.renderers.hyperframes.studio_native_project_builder import _hud_scene_config

    cs = _hud_scene_config({"visual_template": "countdown_strike"}, 0, "你只剩 3 天")
    assert len(cs["countdown_steps"]) == 3
    assert cs["final_label"]

    kp = _hud_scene_config({"visual_template": "keyword_punchline"}, 0, "记住不是多一个工具")
    assert kp["keyword"]
    assert kp["punchline"]

    dt = _hud_scene_config({"visual_template": "data_dense_table"}, 0, "素材流汇聚状态")
    assert len(dt["rows"]) == 4
    assert dt["summary"]

    sl = _hud_scene_config({"visual_template": "step_ladder"}, 0, "从 0 到可用")
    assert len(sl["steps"]) == 4

    cl = _hud_scene_config({"visual_template": "concept_layers"}, 0, "三个层次递进")
    assert len(cl["layers"]) == 3

    pt = _hud_scene_config({"visual_template": "progress_tracker"}, 0, "8 周能力曲线")
    assert len(pt["tracks"]) == 3
    assert all(len(t["weeks"]) == 8 for t in pt["tracks"])

    kg = _hud_scene_config({"visual_template": "knowledge_graph"}, 0, "你的知识网络")
    assert len(kg["nodes"]) >= 4
    assert len(kg["edges"]) >= 4
    assert kg["central_node"]

    qc = _hud_scene_config({"visual_template": "quote_close"}, 0, "最后一句金句")
    assert qc["quote"]
    assert qc["attribution"]
    assert qc["action"]


# ─── P3.3 — old seed data-helper tests (retained) ───

def test_hud_scene_config_supplies_data_for_each_p33_template():
    from video_director_v3.renderers.hyperframes.studio_native_project_builder import _hud_scene_config

    fq = _hud_scene_config({"visual_template": "framework_quadrant"}, 0, "这四个象限分别代表不同的处理阶段")
    assert len(fq["quadrants"]) == 4
    assert fq["center_label"]

    dt = _hud_scene_config({"visual_template": "decision_tree"}, 0, "你要不要先做这一步？")
    assert dt["root_question"]
    assert len(dt["branches"]) == 2
    assert len(dt["outcomes"]) == 2

    md = _hud_scene_config({"visual_template": "metric_dashboard"}, 0, "效率提升 40%，复盘时间下降")
    assert len(md["metrics"]) == 4
    assert md["metrics"][0]["value"]

    cs = _hud_scene_config({"visual_template": "case_study_card"}, 0, "李同学用了一周就上手")
    assert cs["case_subject"]
    assert cs["before"]
    assert cs["after"]
    assert len(cs["highlights"]) >= 3

    sb = _hud_scene_config({"visual_template": "section_board"}, 0, "这次我们从三个维度判断")
    assert len(sb["sections"]) == 4

    cq = _hud_scene_config({"visual_template": "comment_question"}, 0, "你愿意先跑通最小闭环吗？")
    assert cq["fake_comment"]
    assert cq["guide_question"]


def test_six_new_renderers_produce_visually_distinct_html():
    from video_director_v3.renderers.hyperframes.publish_templates import get_scene_body
    templates = [
        "framework_quadrant", "decision_tree", "metric_dashboard",
        "case_study_card", "section_board", "comment_question",
    ]
    htmls = {t: get_scene_body("S01", "method", {"visual_template": t}) for t in templates}
    assert len(set(htmls.values())) == 6, "Some P3.3 templates produced identical HTML"
    assert "framework-quad" in htmls["framework_quadrant"]
    assert "DECISION / ROOT" in htmls["decision_tree"]
    assert "metric-tile" in htmls["metric_dashboard"]
    assert "BEFORE / 之前" in htmls["case_study_card"]
    assert "board-section" in htmls["section_board"]
    assert "comment-bubble" in htmls["comment_question"]


# ─── P3.4 — narration_planner role classification refinement ───

def test_narration_planner_classifies_method_keywords_correctly():
    from video_director_v3.director.narration_planner import classify_role
    assert classify_role("四象限整理法", 1, 5) == "method"
    assert classify_role("第一步先建立入口", 1, 5) == "method"
    assert classify_role("三个层次递进", 1, 5) == "method"


def test_narration_planner_classifies_proof_keywords_correctly():
    from video_director_v3.director.narration_planner import classify_role
    assert classify_role("从三个维度来判断", 1, 5) == "proof"
    assert classify_role("评论区告诉我你的状态", 1, 5) == "proof"
    assert classify_role("你的知识网络节点关系", 1, 5) == "proof"


def test_narration_planner_classifies_evidence_keywords_correctly():
    from video_director_v3.director.narration_planner import classify_role
    assert classify_role("效率提升 40%", 1, 5) == "evidence"
    assert classify_role("8 周能力曲线", 1, 5) == "evidence"
    assert classify_role("李同学用了一周上手", 1, 5) == "evidence"
