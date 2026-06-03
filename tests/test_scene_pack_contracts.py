"""Scene pack schema and template contract tests."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from video_director_v3.director.scene_pack_schema import validate_scene_pack
from video_director_v3.director.semantic_planner import build_scene_pack
from video_director_v3.director.template_contracts import (
    CONTRACT_FALLBACK_TEMPLATES,
    TEMPLATE_CONTRACTS,
    lint_scene_against_contract,
    lint_scene_pack_contracts,
)


def _sample_scene_pack():
    storyboard = {
        "scenes": [
            {
                "scene_id": "S01",
                "role": "hook",
                "duration": 4.0,
                "narration": "你有没有发现，工具越多，执行越慢？",
                "visual_template": "hook_big_claim",
            },
            {
                "scene_id": "S02",
                "role": "pain",
                "duration": 5.0,
                "narration": "问题不是你不努力，而是流程没有形成闭环。",
                "visual_template": "broken_chain",
            },
            {
                "scene_id": "S03",
                "role": "method",
                "duration": 6.0,
                "narration": "先把输入、结构、输出三步拆开，再让系统稳定执行。",
                "visual_template": "tool_chain_three_cols",
            },
            {
                "scene_id": "S04",
                "role": "evidence",
                "duration": 5.0,
                "narration": "以前每次都从零开始，现在可以直接拿到一版素材包。",
                "visual_template": "before_after_compare",
            },
            {
                "scene_id": "S05",
                "role": "cta",
                "duration": 4.0,
                "narration": "先跑一遍最小闭环，然后再升级。",
                "visual_template": "checklist_cta",
            },
        ]
    }
    return build_scene_pack(
        project_id="scene_pack_test",
        narration_plan={"sentence_list": []},
        storyboard=storyboard,
        audio_timeline={"sentence_timings": []},
    )


def test_scene_pack_schema_accepts_minimal_planner_output():
    scene_pack = _sample_scene_pack()

    assert scene_pack["status"] == "dry_run"
    assert len(scene_pack["scenes"]) == 5
    assert validate_scene_pack(scene_pack) == []
    assert scene_pack["lint"]["status"] == "PASS"


def test_scene_pack_rebalances_early_cta_into_summary_role():
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
                "role": "cta",
                "duration": 5.0,
                "narration": "你有没有这种感觉，收藏越来越多，真正想输出的时候却一句都拼不出来？",
                "visual_template": "checklist_cta",
            },
            {
                "scene_id": "S03",
                "role": "problem",
                "duration": 5.0,
                "narration": "问题不是不努力，而是入口太散，下一步要先统一入口。",
                "visual_template": "broken_chain",
            },
            {
                "scene_id": "S04",
                "role": "cta",
                "duration": 4.0,
                "narration": "先跑通一个最小闭环，再去想扩展。",
                "visual_template": "checklist_cta",
            },
        ]
    }

    scene_pack = build_scene_pack(
        project_id="rebalance_cta",
        narration_plan={"sentence_list": []},
        storyboard=storyboard,
        audio_timeline={"sentence_timings": []},
    )
    roles = [scene["role"] for scene in scene_pack["scenes"]]
    template_types = [scene["template_type"] for scene in scene_pack["scenes"]]

    assert roles[0] == "hook"
    assert roles[1] in {"offer", "verdict"}
    assert template_types[1] == "result_summary"
    assert roles[-1] == "cta"
    assert template_types[-1] == "final_cta"


def test_scene_pack_proof_slots_use_concrete_evidence():
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
                "narration": "以前每次都从零开始，现在可以直接拿到一版素材包。",
                "visual_template": "case_study_card",
            },
            {
                "scene_id": "S03",
                "role": "cta",
                "duration": 4.0,
                "narration": "先跑通一个最小闭环，再去想扩展。",
                "visual_template": "checklist_cta",
            },
        ]
    }

    scene_pack = build_scene_pack(
        project_id="proof_concrete",
        narration_plan={"sentence_list": []},
        storyboard=storyboard,
        audio_timeline={"sentence_timings": []},
    )
    proof_scene = scene_pack["scenes"][1]
    metric = proof_scene["slots"]["metric_or_evidence"]
    note = proof_scene["slots"]["credibility_note"]

    assert proof_scene["role"] == "proof"
    assert metric in {"前后对比", "执行记录", "流程闭环"} or "记录" in metric
    assert "真实案例" not in metric
    assert "经验" not in note


def _valid_scene_for_contract(template_id: str) -> dict:
    fixtures = {
        "hook": {"role": "hook", "slots": {"main_claim": "系统先跑通", "pain_point": "收藏越多越难输出", "status_badge": "QUESTION", "visual_emphasis": "闭环"}},
        "problem_conflict": {"role": "problem", "slots": {"problem_title": "问题不是努力不够", "conflict_items": ["入口太多", "资料分散"], "consequence": "结果是总要重来", "warning_label": "RISK"}},
        "before_after": {"role": "method", "slots": {"before_label": "以前", "after_label": "现在", "before_items": ["入口分散", "检索很慢"], "after_items": ["统一入口", "直接调用"], "verdict": "先接通，再扩展"}},
        "proof": {"role": "proof", "slots": {"proof_title": "真实结果能看见", "proof_items": ["资料可复用", "过程可验证"], "metric_or_evidence": "真实案例", "credibility_note": "已经跑通过一轮"}},
        "final_cta": {"role": "cta", "slots": {"final_claim": "先跑一遍", "next_step": "今天就完成最小闭环", "cta_text": "先开始", "avoid_phrases": ["空谈"]}},
        "method_steps": {"role": "method", "slots": {"method_title": "三步法", "steps": ["统一入口", "建立结构", "开始调用"], "step_labels": ["STEP 1", "STEP 2", "STEP 3"], "final_result": "拿到可复用路径"}},
        "framework_quadrant": {"role": "method", "slots": {"framework_title": "四象限判断", "quadrants": [{"label": "Q1", "text": "输入"}, {"label": "Q2", "text": "整理"}, {"label": "Q3", "text": "检索"}, {"label": "Q4", "text": "输出"}], "center_claim": "闭环", "usage_note": "用来定位卡点"}},
        "progress_tracker": {"role": "proof", "slots": {"progress_title": "进度变化", "stages": [{"label": "阶段 1", "text": "统一入口"}, {"label": "阶段 2", "text": "建立结构"}, {"label": "阶段 3", "text": "开始输出"}], "current_stage": "阶段 2", "completion_signal": "流程已闭环"}},
        "tool_stack": {"role": "method", "slots": {"stack_title": "三件套", "tools": ["Obsidian", "Claude", "Hermes"], "tool_roles": ["存储与链接", "检索与整理", "复盘与跟进"], "workflow_result": "每个工具各司其职"}},
        "keyword_punchline": {"role": "hook", "slots": {"keyword": "闭环", "punchline": "系统先跑通，再谈效率", "contrast": "不是多收藏，而是先接通", "memory_anchor": "先跑一遍"}},
        "myth_bust": {"role": "hook", "slots": {"myth": "工具越多越高效", "truth": "先跑通最小闭环", "reason": "问题在动作没接通", "correction": "先让系统可用"}},
        "case_study_card": {"role": "proof", "slots": {"case_title": "真实案例", "situation": "资料散在多处", "action": "统一到一个入口", "result": "拿到可复用素材", "lesson": "先跑通再升级"}},
        "concept_layers": {"role": "method", "slots": {"concept_title": "三层结构", "layers": ["收集", "组织", "调用"], "layer_descriptions": ["素材进库", "链接起来", "直接调用"], "conclusion": "每层各做一件事"}},
        "knowledge_graph": {"role": "proof", "slots": {"graph_title": "知识图谱", "nodes": [{"id": "N1", "label": "输入"}, {"id": "N2", "label": "链接"}, {"id": "N3", "label": "输出"}], "edges": [{"from": "N1", "to": "N2"}, {"from": "N2", "to": "N3"}], "insight": "节点连起来以后调用更快"}},
        "result_summary": {"role": "verdict", "slots": {"result_title": "这一轮的结果", "key_results": ["流程已闭环", "阻塞点已明确", "下一步可执行"], "final_verdict": "先可用，再完美", "next_step": "继续跑第二轮"}},
    }
    data = fixtures[template_id]
    return {"id": f"{template_id}-scene", "template_type": template_id, **data}


def test_template_contract_registry_covers_fifteen_templates():
    expected = {
        "hook", "problem_conflict", "before_after", "proof", "final_cta",
        "method_steps", "framework_quadrant", "progress_tracker", "tool_stack",
        "keyword_punchline", "myth_bust", "case_study_card", "concept_layers",
        "knowledge_graph", "result_summary",
    }

    assert expected == set(TEMPLATE_CONTRACTS)
    for contract in TEMPLATE_CONTRACTS.values():
        assert contract.required_slots
        assert contract.role_compatibility
        assert contract.fallback_template in CONTRACT_FALLBACK_TEMPLATES
        assert contract.semantic_intent


def test_template_contract_lint_passes_for_all_fifteen_templates():
    for template_id in TEMPLATE_CONTRACTS:
        assert lint_scene_against_contract(_valid_scene_for_contract(template_id)) == []

def test_template_contract_lint_passes_when_required_slots_are_complete():
    scene = _valid_scene_for_contract("hook")

    assert lint_scene_against_contract(scene) == []


def test_template_contract_lint_fails_missing_required_slot():
    scene = {
        "id": "S02",
        "role": "problem",
        "template_type": "problem_conflict",
        "slots": {
            "problem_title": "问题不是努力不够",
            "consequence": "结果是你一直卡住。",
            "warning_label": "BLOCKER",
        },
    }

    errors = lint_scene_against_contract(scene)

    assert any("missing required slot 'conflict_items'" in item for item in errors)


def test_template_contract_lint_fails_placeholder_copy():
    scene = {
        "id": "S03",
        "role": "cta",
        "template_type": "final_cta",
        "slots": {
            "final_claim": "先跑一遍",
            "next_step": "TODO",
            "cta_text": "现在开始",
            "avoid_phrases": ["以后再说"],
        },
    }

    errors = lint_scene_against_contract(scene)

    assert any("placeholder/empty" in item for item in errors)


def test_template_contract_lint_fails_overlong_chinese_headline():
    scene = {
        "id": "S04",
        "role": "proof",
        "template_type": "proof",
        "slots": {
            "proof_title": "这是一个明显超过限制的超长中文标题它应该触发静态检查失败而不是被放过",
            "proof_items": ["拿到素材", "稳定输出"],
            "metric_or_evidence": "READY",
            "credibility_note": "真实执行后再判断。",
        },
    }

    errors = lint_scene_against_contract(scene)

    assert any("exceeds" in item for item in errors)


def test_template_contract_lint_fails_role_incompatible():
    scene = {
        "id": "S05",
        "role": "hook",
        "template_type": "before_after",
        "slots": {
            "before_label": "以前",
            "after_label": "现在",
            "before_items": ["散乱", "找不到"],
            "after_items": ["统一入口", "拿到草稿"],
            "verdict": "先接通再扩展。",
        },
    }

    errors = lint_scene_against_contract(scene)

    assert any("not compatible" in item for item in errors)


def test_template_contract_lint_fails_forbidden_field_and_bounds():
    scene_pack = {
        "scenes": [
            {
                "id": "S06",
                "role": "offer",
                "template_type": "before_after",
                "raw_text": "should not exist",
                "slots": {
                    "before_label": "以前",
                    "after_label": "现在",
                    "before_items": ["散乱"],
                    "after_items": [],
                    "verdict": "先接通再扩展。",
                },
            },
        ]
    }

    errors = lint_scene_pack_contracts(scene_pack)

    assert any("forbidden field" in item for item in errors)
    assert any("needs at least" in item for item in errors)
