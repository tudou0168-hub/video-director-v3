"""Semantic scene_pack planner for contract-driven template rendering."""
from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

from video_director_v3.director.scene_pack_schema import (
    SCENE_PACK_VERSION,
    normalize_scene_role,
    validate_scene_pack,
)
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
) -> dict[str, Any]:
    scenes = []
    all_scenes = storyboard.get("scenes", [])
    for index, scene in enumerate(all_scenes):
        voiceover = _scene_voiceover(scene, narration_plan, audio_timeline or {})
        role = normalize_scene_role(scene.get("role", "method"))
        template_type = _template_type_for_scene(scene, role, index, len(all_scenes))
        headline = _headline_from_voiceover(voiceover, role)
        subtitle = _subtitle_from_voiceover(voiceover, headline)
        display_conclusion = _display_conclusion(voiceover, subtitle)
        slots = _slots_for_template(template_type, headline, subtitle, display_conclusion, voiceover, role)
        scenes.append({
            "id": scene.get("scene_id") or f"S{index + 1:02d}",
            "role": role,
            "intent": _intent_for_role(role, voiceover, template_type),
            "duration": round(float(scene.get("duration", 0) or 0), 3),
            "voiceover": voiceover,
            "display_headline": headline,
            "display_subtitle": subtitle,
            "display_conclusion": display_conclusion,
            "template_type": template_type,
            "slots": slots,
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


def _template_type_for_scene(scene: dict[str, Any], role: str, index: int, total: int) -> str:
    visual_template = str(scene.get("visual_template") or "")
    if visual_template in VISUAL_TEMPLATE_TO_CONTRACT:
        template_type = VISUAL_TEMPLATE_TO_CONTRACT[visual_template]
        if template_type == "before_after" and role == "proof":
            return "proof"
        if template_type == "problem_conflict" and role == "hook":
            return "myth_bust"
        return template_type
    if index == total - 1 and role in {"cta", "offer", "verdict"}:
        return "final_cta"
    if role == "hook":
        return "hook"
    if role in {"problem", "conflict"}:
        return "problem_conflict"
    if role == "proof":
        return "proof"
    if role in {"cta", "offer"}:
        return "final_cta"
    return "before_after"


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


def _slots_for_template(
    template_type: str,
    headline: str,
    subtitle: str,
    conclusion: str,
    voiceover: str,
    role: str,
) -> dict[str, Any]:
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
        return {
            "proof_title": headline,
            "proof_items": _split_short_phrases(voiceover, 3, defaults=["结果更稳", "资料可复用", "过程可验证"]),
            "metric_or_evidence": _metric_or_evidence_for_text(voiceover),
            "credibility_note": _clip(conclusion or "这不是空谈，而是已经跑通的路径。", 36),
        }
    if template_type == "final_cta":
        return {
            "final_claim": headline,
            "next_step": _clip(conclusion or "先完成一次真实执行，再继续升级。", 34),
            "cta_text": _cta_text_for_text(voiceover),
            "avoid_phrases": _avoid_phrases_for_cta(voiceover),
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
            "stack_title": headline,
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
        return {
            "case_title": _clip(headline, 28),
            "situation": _clip(situation, 24),
            "action": _clip(action, 24),
            "result": _clip(result, 24),
            "lesson": _clip(conclusion or "先跑通最小路径，再扩大系统规模。", 28),
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
            "key_results": _split_short_phrases(voiceover, 3, defaults=["流程已闭环", "关键阻塞点已明确", "下一步可执行"]),
            "final_verdict": _clip(conclusion or "系统不是越大越好，而是先能稳定使用。", 34),
            "next_step": _clip(_next_step_from_text(voiceover), 30),
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


def _headline_from_voiceover(voiceover: str, role: str) -> str:
    cleaned = re.sub(r"[\n\r]+", " ", voiceover).strip()
    if not cleaned:
        return {
            "hook": "先抓住这一秒",
            "problem": "问题不是工具不够",
            "method": "把步骤拆成动作",
            "proof": "结果要能被看见",
            "cta": "现在跑一遍",
        }.get(role, "这一段的重点")
    return _clip(cleaned, 30)


def _subtitle_from_voiceover(voiceover: str, headline: str) -> str:
    remainder = voiceover.replace(headline.replace("…", ""), "", 1).strip(" ，。；;:：")
    return _clip(remainder or voiceover, 52)


def _display_conclusion(voiceover: str, subtitle: str) -> str:
    if "所以" in voiceover:
        return _clip(voiceover.split("所以", 1)[1].strip(" ，。"), 38)
    if "这样" in voiceover:
        tail = voiceover.split("这样", 1)[-1].strip(" ，。")
        if tail:
            return _clip(tail, 38)
    return _clip(subtitle or voiceover, 38)


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
        tools = known[:3]
    while len(tools) < 3:
        tools.append(known[len(tools)])
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
    if "先" in text:
        return "先跑一遍"
    if "直接" in text:
        return "直接调用"
    return "记住这一句"


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
        return "前后对照"
    if "案例" in text or "真实" in text:
        return "真实案例"
    return "可复用路径"


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
