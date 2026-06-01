"""Build a minimal Studio-native HyperFrames preview project."""
from __future__ import annotations

import json
import shutil
import subprocess
from html import escape
from pathlib import Path
from typing import Any

from video_director_v3.renderers.hyperframes.publish_templates import get_scene_body


def _write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def scale_storyboard_to_audio(storyboard: dict[str, Any], audio_duration: float) -> dict[str, Any]:
    scenes = storyboard.get("scenes", [])
    if not scenes:
        return {**storyboard, "scenes": []}
    current_end = max(float(s.get("start", 0)) + float(s.get("duration", 0)) for s in scenes)
    factor = audio_duration / max(current_end, 0.001)
    scaled = []
    for index, scene in enumerate(scenes):
        start = round(float(scene.get("start", 0)) * factor, 3)
        end = audio_duration if index == len(scenes) - 1 else round(
            (float(scene.get("start", 0)) + float(scene.get("duration", 0))) * factor, 3
        )
        scaled.append({**scene, "start": start, "duration": round(end - start, 3)})
    return {
        **storyboard,
        "project": {**storyboard.get("project", {}), "duration": audio_duration, "audio_duration": audio_duration},
        "scenes": scaled,
    }


def build_studio_native_project(
    *,
    project_dir: Path,
    storyboard: dict[str, Any],
    narration_plan: dict[str, Any],
    tts_result: dict[str, Any],
    caption_beats: dict[str, Any],
    visual_beats: dict[str, Any],
    transitions: dict[str, Any],
) -> dict[str, Any]:
    timeline_dir = project_dir / "hyperframes_timeline"
    assets_dir = timeline_dir / "assets"
    data_dir = timeline_dir / "data"
    assets_dir.mkdir(parents=True, exist_ok=True)
    data_dir.mkdir(parents=True, exist_ok=True)
    audio_path = Path(tts_result["audio_path"])
    shutil.copy2(audio_path, assets_dir / "voiceover.mp3")
    duration = float(tts_result["real_duration"])

    scenes = storyboard.get("scenes", [])
    captions = caption_beats.get("caption_beats", [])
    scene_html = []
    director_scenes = []
    for scene in scenes:
        sid = scene.get("scene_id", "S01")
        role = scene.get("role", "explain")
        start = float(scene.get("start", 0))
        scene_duration = max(float(scene.get("duration", 0)) - 0.001, 0)
        narration = scene.get("narration", "").strip() or role
        hud_scene = _hud_scene_config(scene, len(director_scenes), narration)
        director_scenes.append({
            **hud_scene, "id": sid, "start_time": start,
            "end_time": round(start + float(scene.get("duration", 0)), 3),
        })
        scene_html.append(f"""
<section id="scene-{escape(sid.lower())}" class="scene clip role-{escape(role)}" data-start="{start}" data-duration="{round(scene_duration, 3)}" data-track-index="1">
  {get_scene_body(sid, role, hud_scene)}
  <div class="hud-frame"></div><div class="scan-sweep"></div>
  <div class="hud-top"><span>{escape(role.upper())} / HUD SYSTEM</span><b>{escape(sid)}</b></div>
  <div class="hud-bottom"><span>OBSIDIAN SECOND BRAIN</span><i>VOICEOVER DRIVEN</i></div>
</section>""")

    caption_html = []
    normalized_captions = []
    for item in captions:
        start = float(item.get("start", item.get("start_time", 0)))
        item_duration = float(item.get("duration", 0))
        normalized_captions.append({
            **item, "start_time": start, "end_time": round(start + item_duration, 3),
        })
        caption_html.append(
            f'<div id="caption-{escape(item.get("caption_id", "beat").lower())}" class="caption clip" data-start="{start}" '
            f'data-duration="{round(max(item_duration - 0.02, 0), 3)}" '
            f'data-track-index="2">{escape(item.get("text", ""))}</div>'
        )

    html = f"""<!doctype html>
<html lang="zh"><head><meta charset="utf-8"><title>{escape(narration_plan.get("title", project_dir.name))}</title>
<style>
*{{box-sizing:border-box}}html,body{{margin:0;width:1080px;height:1920px;overflow:hidden;background:#050812;color:#f4f7ff;font-family:sans-serif}}
#root,.scene{{position:absolute;inset:0;overflow:hidden}}.scene{{background:#050812}}
.bg-grid{{position:absolute;inset:0;background-image:linear-gradient(rgba(37,216,255,.08) 1px,transparent 1px),linear-gradient(90deg,rgba(37,216,255,.08) 1px,transparent 1px);background-size:64px 64px}}
.bg-glow{{position:absolute;width:720px;height:720px;border-radius:50%;filter:blur(36px);animation:glow 3.4s ease-in-out infinite}}
.bg-glow-1{{left:-220px;top:120px}}.bg-glow-2{{right:-240px;bottom:160px}}
.hud-frame{{position:absolute;inset:28px;border:1px solid rgba(37,216,255,.32);clip-path:polygon(0 0,100% 0,100% 94%,94% 100%,0 100%);pointer-events:none}}
.hud-top,.hud-bottom{{position:absolute;left:52px;right:52px;display:flex;justify-content:space-between;color:#25d8ff;font:800 18px/1 monospace;letter-spacing:.16em}}
.hud-top{{top:52px}}.hud-bottom{{bottom:318px}}.hud-bottom i{{font-style:normal;color:rgba(255,255,255,.55)}}
.scan-sweep{{position:absolute;left:0;right:0;height:3px;top:-4%;background:linear-gradient(90deg,transparent,rgba(37,216,255,.7),transparent);box-shadow:0 0 22px rgba(37,216,255,.7);animation:scan 4.5s linear infinite;pointer-events:none}}
.caption{{position:absolute;left:54px;right:54px;bottom:72px;padding:20px 30px;border:1px solid rgba(37,216,255,.35);border-radius:20px;background:rgba(6,8,16,.88);box-shadow:0 0 38px rgba(37,216,255,.12);font-size:48px;line-height:1.28;font-weight:850;text-align:center}}
@keyframes glow{{0%,100%{{opacity:.58;transform:scale(1)}}50%{{opacity:.92;transform:scale(1.12)}}}}
@keyframes scan{{0%{{top:-4%}}100%{{top:104%}}}}
</style></head><body>
<div id="root" data-composition-id="{escape(project_dir.name)}" data-start="0" data-width="1080" data-height="1920" data-duration="{duration}">
<audio id="voiceover-audio" data-start="0" data-duration="{duration}" data-track-index="0" data-volume="1" src="assets/voiceover.mp3"></audio>
{"".join(scene_html)}
{"".join(caption_html)}
</div>
<script>window.__timelines=window.__timelines||{{}};</script>
</body></html>"""
    (timeline_dir / "index.html").write_text(html, encoding="utf-8")
    _write_json(data_dir / "script.json", narration_plan)
    _write_json(data_dir / "tts_result.json", tts_result)
    _write_json(data_dir / "caption_beats.json", {"duration_sec": duration, "beats": normalized_captions})
    _write_json(data_dir / "director_timeline.json", {"total_duration_sec": duration, "scenes": director_scenes})
    _write_json(data_dir / "visual_beats.json", visual_beats)
    _write_json(data_dir / "transition_map.json", transitions)
    _write_json(timeline_dir / "meta.json", {
        "phase": "V3-P3.1-Audio-First", "project": project_dir.name,
        "canvas": {"width": 1080, "height": 1920},
        "audio_duration": duration, "scene_count": len(scenes), "caption_count": len(captions),
    })
    return {
        "timeline_dir": str(timeline_dir), "index": str(timeline_dir / "index.html"),
        "duration": duration, "scene_count": len(scenes), "caption_count": len(captions),
    }


def _hud_scene_config(scene: dict[str, Any], index: int, narration: str) -> dict[str, Any]:
    template = scene.get("visual_template", "hook_big_claim")
    config = {**scene, "visual_template": template, "headline": narration[:42]}
    if template == "hook_big_claim":
        config.setdefault("headline", narration[:24] or "读了很多书，为什么还是记不住？")
        config.setdefault("keyword", "记不住" if "记不住" in narration else "")
        config.setdefault("subheadline", "真正缺的不是努力，而是一个可检索的第二大脑")
        config.setdefault("layout_variant", _hook_layout_variant_from_narration(narration))
    elif template == "pain_card_stack":
        config.setdefault("headline", narration[:28] or "素材越存越多，输出反而越来越慢")
        config.setdefault("cards", _pain_cards_from_narration(narration))
        config.setdefault("conclusion", _pain_conclusion_from_narration(narration))
    elif template == "broken_chain":
        config.setdefault("headline", narration[:28] or "把知识从收藏夹，接入可检索的系统")
        config.setdefault("chain_nodes", _chain_nodes_from_narration(narration))
        config.setdefault("broken_slots", _broken_slots_from_narration(narration))
        config.setdefault("layout_variant", _broken_layout_variant_from_narration(narration))
        left_panel, right_panel, footer_note = _broken_panels_from_narration(narration)
        config.setdefault("left_panel", left_panel)
        config.setdefault("right_panel", right_panel)
        config.setdefault("footer_note", footer_note)
        if config["layout_variant"] == "responsibility_split":
            config.setdefault("bridge_label", "职责分工")
        if config["layout_variant"] == "binary_choice_split":
            config.setdefault("left_choice", left_panel)
            config.setdefault("right_choice", right_panel)
    elif template == "tool_chain_three_cols":
        config.setdefault("headline", narration[:30] or "输入、链接、检索，形成最小工作流")
        config.setdefault("three_cols", _three_cols_from_narration(narration))
        config.setdefault("layout_variant", _tool_layout_variant_from_narration(narration))
    elif template == "before_after_compare":
        config.setdefault("headline", narration[:30] or "找素材，从翻遍 App 到 30 秒拿到素材包")
        config.setdefault("layout_variant", _compare_layout_variant_from_narration(narration))
        left_items, right_items = _compare_items_from_narration(narration)
        config.setdefault("left_items", left_items)
        config.setdefault("right_items", right_items)
        config.setdefault("dashboard_metrics", _dashboard_metrics_from_narration(narration))
        config.setdefault("parallel_lanes", _parallel_lanes_from_narration(narration))
        left_panel, right_panel, summary_badge = _proof_panels_from_narration(narration)
        config.setdefault("left_panel", left_panel)
        config.setdefault("right_panel", right_panel)
        config.setdefault("summary_badge", summary_badge)
    elif template == "checklist_cta":
        config.setdefault("headline", narration[:30] or "先收藏，再跑通最小闭环")
        layout_variant = _cta_layout_variant_from_narration(narration)
        config.setdefault("layout_variant", layout_variant)
        checklist, final_message = _checklist_from_narration(narration)
        config.setdefault("checklist", checklist)
        config.setdefault("final_message", final_message)
        if layout_variant == "button_banner":
            config.setdefault("button_label", _cta_button_label_from_narration(narration))
            config.setdefault("hint", "滑动看完 → 马上动手")
        elif layout_variant == "end_score_goodbye":
            config.setdefault("score", "100")
            config.setdefault("score_label", "本章掌握度")
            config.setdefault("next_teaser", "下期讲：把检索真正接进 AI 流程")
        elif layout_variant == "scorecard":
            config.setdefault("scorecard_metrics", _cta_scorecard_metrics_from_narration(narration))
    return config


def _pain_cards_from_narration(narration: str) -> list[dict[str, str]]:
    cards = [
        {"icon": "📚", "text": "读了很多书", "sub": "信息进脑很快"},
        {"icon": "🧠", "text": "真正要用时", "sub": "一句都想不起来"},
        {"icon": "📉", "text": "记住的很少", "sub": "能调用的更少"},
    ]
    if "100 本书" in narration:
        cards.append({"icon": "📊", "text": "读了 100 本书", "sub": "能记住不到 10 本"})
    else:
        cards.append({"icon": "🗂️", "text": "素材越积越多", "sub": "输出反而更慢"})
    return cards


def _pain_conclusion_from_narration(narration: str) -> str:
    if "想不起来" in narration:
        return "真正要输出时，脑子里还是一片空白"
    if "插件" in narration:
        return "问题不是工具不够，而是系统没有先跑通"
    return "信息收集很多，不等于需要时能拿出来用"


def _hook_layout_variant_from_narration(narration: str) -> str:
    if "你有没有" in narration or "感觉" in narration or "?" in narration:
        return "quote_punch"
    if any(token in narration for token in ("很多", "100", "999", "30h")):
        return "big_number_left"
    return "center_claim"


def _chain_nodes_from_narration(narration: str) -> list[str]:
    if "思考" in narration and "创造" in narration:
        return ["思考", "创造", "存储", "检索"]
    if "输入" in narration and "输出" in narration:
        return ["输入", "存储", "检索", "输出"]
    return ["素材", "结构", "检索", "输出"]


def _broken_slots_from_narration(narration: str) -> list[int]:
    if "负责" in narration:
        return [1]
    if "插件" in narration or "分类" in narration:
        return [0, 2]
    return [1, 2]


def _broken_layout_variant_from_narration(narration: str) -> str:
    if "负责" in narration or ("第二大脑" in narration and "思考" in narration):
        return "responsibility_split"
    if "别" in narration or "不要" in narration:
        return "binary_choice_split"
    return "chain_flow"


def _broken_panels_from_narration(
    narration: str,
) -> tuple[dict[str, Any], dict[str, Any], str]:
    if "负责" in narration or ("第二大脑" in narration and "思考" in narration):
        return (
            {
                "label": "大脑",
                "title": "思考与创造",
                "items": ["判断重点", "提出观点", "做最终决策"],
            },
            {
                "label": "第二大脑",
                "title": "存储与检索",
                "items": ["统一收纳素材", "需要时随时回查", "给 AI 稳定上下文"],
            },
            "把记忆负担迁出去，让创造力留在脑内",
        )
    if "插件" in narration or "分类" in narration or "别" in narration:
        return (
            {
                "label": "不要",
                "title": "一上来堆复杂度",
                "items": ["装太多插件", "先设计完美分类", "系统迟迟不开始工作"],
            },
            {
                "label": "先做",
                "title": "跑通最小闭环",
                "items": ["统一输入", "补上检索", "用一次真实输出验证"],
            },
            "先让系统跑起来，再决定哪里该加复杂度",
        )
    return (
        {
            "label": "断点",
            "title": "知识链条断开",
            "items": ["收集很多", "回查很慢", "输出时还得重找"],
        },
        {
            "label": "目标",
            "title": "形成可检索系统",
            "items": ["统一入口", "链接上下文", "需要时直接调用"],
        },
        "不是多一个工具，而是把链路接通。",
    )


def _three_cols_from_narration(narration: str) -> list[dict[str, str]]:
    if "输入汇聚" in narration or "进入 Obsidian" in narration:
        return [
            {"name": "微信读书", "func": "摘录同步", "icon": "RD", "detail": "高亮和笔记汇进同一库"},
            {"name": "网页剪藏", "func": "素材归档", "icon": "WEB", "detail": "文章和片段不再散落"},
            {"name": "语音视频", "func": "转写入库", "icon": "AV", "detail": "口述与视频笔记统一检索"},
        ]
    if "双向链接" in narration:
        return [
            {"name": "主题页", "func": "集中观点", "icon": "MAP", "detail": "把分散笔记挂到同一主题"},
            {"name": "双向链接", "func": "形成网络", "icon": "LINK", "detail": "相关卡片自动互相指向"},
            {"name": "关系回查", "func": "追踪上下文", "icon": "TRACE", "detail": "例子、方法、结论能串起来"},
        ]
    if "直接问 AI" in narration or "找到观点和例子" in narration:
        return [
            {"name": "自然提问", "func": "先问问题", "icon": "ASK", "detail": "按主题或场景提需求"},
            {"name": "检索笔记", "func": "定位观点", "icon": "FIND", "detail": "从个人知识库里找材料"},
            {"name": "整理输出", "func": "拼成答案", "icon": "OUT", "detail": "把观点、例子、结构拉成草稿"},
        ]
    if "第二大脑" in narration and "AI" in narration:
        return [
            {"name": "Obsidian", "func": "存储知识", "icon": "OBS", "detail": "做你的外部记忆"},
            {"name": "AI", "func": "检索整理", "icon": "AI", "detail": "把笔记转成可用素材"},
            {"name": "输出", "func": "写作复盘", "icon": "GO", "detail": "把知识重新变成作品"},
        ]
    return [
        {"name": "统一输入", "func": "汇聚素材", "icon": "IN", "detail": "读书·网页·语音·视频"},
        {"name": "双向链接", "func": "形成网络", "icon": "LINK", "detail": "相关观点自动连接"},
        {"name": "AI 检索", "func": "随问随取", "icon": "AI", "detail": "整理观点和例子"},
    ]


def _tool_layout_variant_from_narration(narration: str) -> str:
    if "输入汇聚" in narration or "进入 Obsidian" in narration:
        return "source_ingest"
    if "双向链接" in narration:
        return "knowledge_triangle"
    if "术语" in narration or "概念" in narration or "关系" in narration:
        return "matrix_glossary_wall"
    if "直接问 AI" in narration or "找到观点和例子" in narration:
        return "vertical_flow"
    if "后来" in narration or "第二大脑" in narration:
        return "intro_offset"
    return "three_col_row"


def _compare_items_from_narration(narration: str) -> tuple[list[str], list[str]]:
    if "30 秒" in narration:
        return (
            ["翻遍多个 App", "素材散在各处", "写作前先找半天"],
            ["统一入口检索", "结构先出来", "30 秒拿到素材包"],
        )
    if "你才能" in narration or "真正的创造" in narration:
        return (
            ["大脑忙着记忆", "创作被琐事挤占", "每次都从头拼"],
            ["记忆外包出去", "精力回到判断", "把时间留给创造"],
        )
    return (
        ["到处找资料", "从空白文档开始", "写一半卡住"],
        ["统一入口", "先有结构", "拿到可改草稿"],
    )


def _compare_layout_variant_from_narration(narration: str) -> str:
    if "30 秒" in narration or "素材包" in narration:
        return "dashboard_mobile"
    if "以前" in narration and "现在" in narration:
        return "parallel_lanes"
    if "你才能" in narration or "交给第二大脑" in narration:
        return "symptom_panel"
    return "compare_columns"


def _dashboard_metrics_from_narration(narration: str) -> list[dict[str, str]]:
    if "30 秒" in narration:
        return [
            {"label": "取材时间", "value": "30s"},
            {"label": "入口数量", "value": "1"},
            {"label": "素材包", "value": "READY"},
        ]
    return [
        {"label": "入口数量", "value": "1"},
        {"label": "结构状态", "value": "READY"},
        {"label": "输出速度", "value": "FAST"},
    ]


def _parallel_lanes_from_narration(narration: str) -> list[dict[str, Any]]:
    if "以前" in narration and "现在" in narration:
        return [
            {"label": "旧路径", "color": "#FF4757", "steps": ["翻找素材", "手动拼接", "从零开写"]},
            {"label": "新路径", "color": "#4D9FFF", "steps": ["直接提问", "检索笔记", "拿到素材包"]},
        ]
    return [
        {"label": "旧路径", "color": "#FF4757", "steps": ["到处找资料", "重新组织", "写一半卡住"]},
        {"label": "新路径", "color": "#4D9FFF", "steps": ["统一入口", "直接回查", "继续输出"]},
    ]


def _proof_panels_from_narration(
    narration: str,
) -> tuple[dict[str, Any], dict[str, Any], str]:
    if "你才能" in narration or "交给第二大脑" in narration:
        return (
            {
                "label": "交给第二大脑",
                "title": "记忆负担下降",
                "items": ["不用强记细节", "素材随时能回查", "例子和观点更好找"],
            },
            {
                "label": "留给自己",
                "title": "创造空间上升",
                "items": ["注意力回到判断", "把精力放在表达", "真正去做创造"],
            },
            "记忆外包，不等于放弃思考；而是把大脑还给创造。",
        )
    return (
        {
            "label": "旧方式",
            "title": "信息在脑里堵住",
            "items": ["想用时找不到", "每次都从零开始"],
        },
        {
            "label": "新方式",
            "title": "知识在系统里流动",
            "items": ["需要时直接调用", "输出前先拿到结构"],
        },
        "让知识可检索，输出才会持续发生。",
    )


def _checklist_from_narration(narration: str) -> tuple[list[str], str]:
    if "最小闭环" in narration:
        return (
            ["输入统一到一个库", "把相关笔记连起来", "需要时直接问 AI"],
            "先把闭环跑通，再决定要不要加插件",
        )
    if "收藏" in narration:
        return (
            ["先收藏这套流程", "照着搭一遍最小版本", "用一次真实输出验证它"],
            "先用起来，比继续囤工具更重要",
        )
    return (
        ["统一输入到 Obsidian", "用双向链接组织笔记", "需要素材时直接问 AI"],
        "把记住外包出去，把精力留给创造",
    )


def _cta_layout_variant_from_narration(narration: str) -> str:
    """Route CTA scene to a layout variant based on sentence semantics.

    Rules:
      - Strong single action verb → button_banner (大按钮式行动号召)
      - Chapter close / 下期 / 完结 / 收束 → end_score_goodbye (大分数收束)
      - Score / 状态 / 评估 / 指标 → scorecard (多指标得分卡)
      - Else → checklist_steps (default, 3-step action)
    """
    if any(token in narration for token in ("完结", "收束", "下期", "再见", "下章", "合上", "结业", "系列")):
        return "end_score_goodbye"
    if any(token in narration for token in ("得分", "评分", "评级", "状态", "指标", "就绪", "READY", "GO", "PASS")):
        return "scorecard"
    if any(token in narration for token in ("立即", "马上", "现在", "现在就开始", "今晚", "明天", "下一步") ):
        return "button_banner"
    return "checklist_steps"


def _cta_button_label_from_narration(narration: str) -> str:
    if "最小闭环" in narration:
        return "先搭最小闭环"
    if "收藏" in narration:
        return "照着搭一遍"
    if "下一步" in narration:
        return "马上去做"
    if "跑通" in narration:
        return "立即跑一遍"
    return "开始第一步"


def _cta_scorecard_metrics_from_narration(narration: str) -> list[dict[str, str]]:
    if "最小闭环" in narration:
        return [
            {"label": "输入已统一", "value": "READY", "color": "#2ED573"},
            {"label": "检索已接入", "value": "OK", "color": "#4D9FFF"},
            {"label": "已生成草稿", "value": "GO", "color": "#FF6B35"},
        ]
    if "收藏" in narration:
        return [
            {"label": "流程已收藏", "value": "DONE", "color": "#2ED573"},
            {"label": "最小版本已搭", "value": "OK", "color": "#4D9FFF"},
            {"label": "第一次输出", "value": "GO", "color": "#FF6B35"},
        ]
    return [
        {"label": "系统就绪", "value": "READY", "color": "#2ED573"},
        {"label": "结构成立", "value": "OK", "color": "#4D9FFF"},
        {"label": "下一步", "value": "GO", "color": "#FF6B35"},
    ]


def capture_native_review_frames(timeline_dir: Path, frames: int = 7) -> dict[str, Any]:
    meta = json.loads((timeline_dir / "meta.json").read_text(encoding="utf-8"))
    duration = float(meta["audio_duration"])
    timestamps = [round(0.5 + index * max(duration - 1.0, 0) / max(frames - 1, 1), 3) for index in range(frames)]
    snapshots_dir = timeline_dir / "snapshots"
    if snapshots_dir.exists():
        shutil.rmtree(snapshots_dir)
    result = subprocess.run(
        ["npx", "hyperframes", "snapshot", str(timeline_dir), "--at", ",".join(map(str, timestamps)), "--describe", "false"],
        capture_output=True, text=True, timeout=180,
    )
    pngs = sorted(snapshots_dir.glob("frame-*.png"))
    review_frames_dir = timeline_dir.parent / "review_frames"
    review_frames_dir.mkdir(parents=True, exist_ok=True)
    for old_frame in review_frames_dir.glob("*"):
        if old_frame.is_file():
            old_frame.unlink()
    for snapshot in pngs:
        shutil.copy2(snapshot, review_frames_dir / snapshot.name)
    contact_sheet = snapshots_dir / "contact-sheet.jpg"
    if contact_sheet.exists():
        shutil.copy2(contact_sheet, review_frames_dir / contact_sheet.name)
    return {
        "status": "PASS" if result.returncode == 0 and len(pngs) >= frames else "FAIL",
        "ok_count": len(pngs), "snapshots_dir": str(snapshots_dir),
        "review_frames_dir": str(review_frames_dir),
        "stdout": result.stdout[-1000:], "stderr": result.stderr[-1000:],
    }
