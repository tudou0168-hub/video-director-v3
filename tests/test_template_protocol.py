"""Test P3.2.1: scene_framework protocol + 12 seed templates (P3.3)."""
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
    # P3.3 — 6 new seed templates
    "scene.method.framework_quadrant",
    "scene.method.decision_tree",
    "scene.evidence.metric_dashboard",
    "scene.evidence.case_study_card",
    "scene.proof.section_board",
    "scene.proof.comment_question",
}


def test_seed_template_count_is_twelve():
    assert len(SEED_TEMPLATES) == 12, f"expected 12 seeds, got {len(SEED_TEMPLATES)}"


def test_register_seed_templates_populates_registry():
    clear_registry()
    n = register_seed_templates()
    assert n == 12
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
    for role in ["hook", "pain", "input", "memory", "method", "retrieval",
                 "explain", "evidence", "proof", "compare", "cta", "ready", "summary",
                 "framework", "decision", "metric", "example", "board", "comment"]:
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


# ─── P3.3 — new tests for narration-driven seed routing ───

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


def test_hud_scene_config_supplies_data_for_each_new_template():
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
    """Each new template renderer should produce unique output, not just color swaps."""
    from video_director_v3.renderers.hyperframes.publish_templates import get_scene_body
    templates = [
        "framework_quadrant", "decision_tree", "metric_dashboard",
        "case_study_card", "section_board", "comment_question",
    ]
    htmls = {t: get_scene_body("S01", "method", {"visual_template": t}) for t in templates}
    # All six must be distinct
    assert len(set(htmls.values())) == 6, "Some new templates produced identical HTML"
    # Each has its own unique visual signature
    assert "framework-quad" in htmls["framework_quadrant"]
    assert "DECISION / ROOT" in htmls["decision_tree"]
    assert "metric-tile" in htmls["metric_dashboard"]
    assert "BEFORE / 之前" in htmls["case_study_card"]
    assert "board-section" in htmls["section_board"]
    assert "comment-bubble" in htmls["comment_question"]

