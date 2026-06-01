#!/usr/bin/env python3
"""Publishable Visual Templates for V3-P1.2 — 6 fixed templates."""
from typing import Any


# ─── Template Registry ────────────────────────────────────────────

def get_scene_body(sid: str, role: str, scene: dict[str, Any]) -> str:
    """Dispatch to the correct template based on visual_template field."""
    template = scene.get("visual_template", _default_template(role))
    fn = _TEMPLATES.get(template, _template_hook_big_claim)
    return fn(sid, role, scene)


def get_scene_css(sid: str, role: str, scene: dict[str, Any]) -> str:
    template = scene.get("visual_template", _default_template(role))
    fn = _CSS_FUNCTIONS.get(template, _css_fallback)
    return fn(sid, role, scene)


def get_scene_gsap(sid: str, role: str, scene: dict[str, Any], start: float, duration: float) -> str:
    template = scene.get("visual_template", _default_template(role))
    fn = _GSAP_FUNCTIONS.get(template, _gsap_fallback)
    return fn(sid, role, scene, start, duration)


def _default_template(role: str) -> str:
    return f"{role}_centered"


# ─── Colour palettes per role ─────────────────────────────────────

_ACCENT = {
    "hook": "#FF4757",
    "pain": "#FF6B35",
    "method": "#2ED573",
    "evidence": "#4D9FFF",
    "proof": "#4D9FFF",
    "cta": "#2ED573",
}

_BG = {
    "hook": "#0A1628",
    "pain": "#1A0A0A",
    "method": "#0A1A28",
    "evidence": "#0A1428",
    "proof": "#0A1A28",
    "cta": "#0A2818",
}

def _accent(role): return _ACCENT.get(role, "#25D8FF")
def _bg(role): return _BG.get(role, "#050814")


# ─────────────────────────────────────────────────────────────────
# TEMPLATE 1 — hook_big_claim
# S01: Big single headline, keyword highlight, no metric-card
# ─────────────────────────────────────────────────────────────────

def _template_hook_big_claim(sid: str, role: str, scene: dict[str, Any]) -> str:
    acc = _accent(role)
    narration = scene.get("narration", "")
    layout_variant = scene.get("layout_variant", "center_claim")
    # Use first 40 chars as main headline
    headline = narration[:40] if narration else "你有没有发现，收藏越多，反而越写不出来？"
    # Support custom headline override
    headline = scene.get("headline", headline)
    sub = scene.get("subheadline", "")
    keyword = scene.get("keyword", "")
    if keyword:
        safe_headline = headline.replace(keyword, f"<b style='color:{acc}'>{keyword}</b>")
    else:
        safe_headline = headline

    sub_html = f"<div class='hook-sub' style='font-size:32px;color:rgba(255,255,255,0.65);margin-top:20px;'>{sub}</div>" if sub else ""

    if layout_variant == "quote_punch":
        return _render_hook_quote_punch(sid, role, safe_headline, sub, acc)
    if layout_variant == "big_number_left":
        return _render_hook_big_number_left(sid, role, safe_headline, sub, acc)

    return f"""
    <div data-motion-target="scene-bg" style="position:absolute;inset:0;background:{_bg(role)};">
      <div class="bg-grid"></div>
      <div class="bg-glow bg-glow-1" style="background:radial-gradient(circle,{acc}22 0%,transparent 70%);"></div>
      <div class="bg-glow bg-glow-2" style="background:radial-gradient(circle,{acc}18 0%,transparent 70%);"></div>
    </div>
    <div data-motion-target="hook-main" class="hook-main" style="position:absolute;top:420px;left:72px;right:72px;text-align:center;">
      <div class="hook-title" style="font-size:72px;font-weight:700;color:#fff;line-height:1.15;letter-spacing:-1px;">{safe_headline}</div>
      {sub_html}
    </div>
    <div class="scene-label" style="position:absolute;top:24px;left:24px;font-size:14px;color:{acc};opacity:0.7;">{sid} · {role}</div>
"""


def _render_hook_quote_punch(sid: str, role: str, headline: str, sub: str, acc: str) -> str:
    sub_html = f"<div style='font-size:28px;color:rgba(255,255,255,0.58);margin-top:18px;max-width:520px;line-height:1.5;'>{sub}</div>" if sub else ""
    return f"""
    <div data-motion-target="scene-bg" style="position:absolute;inset:0;background:linear-gradient(135deg,#071124 0%,#0A1628 52%,#101B32 100%);">
      <div class="bg-grid"></div>
      <div class="bg-glow bg-glow-1" style="background:radial-gradient(circle,{acc}22 0%,transparent 68%);"></div>
      <div style="position:absolute;top:0;right:0;width:360px;height:100%;background:linear-gradient(180deg,rgba(37,216,255,0.12),transparent 32%,rgba(255,71,87,0.08));clip-path:polygon(24% 0,100% 0,100% 100%,0 100%);"></div>
      <div style="position:absolute;top:56px;right:56px;font-size:18px;letter-spacing:0.2em;color:{acc};opacity:0.88;">QUOTE / PUNCH</div>
    </div>
    <div style="position:absolute;top:160px;left:72px;right:72px;">
      <div style="display:inline-flex;padding:10px 18px;border-radius:999px;background:rgba(255,255,255,0.06);border:1px solid {acc}44;color:{acc};font-size:18px;letter-spacing:0.18em;margin-bottom:26px;">HIGHLIGHT</div>
      <div style="max-width:700px;font-size:70px;font-weight:900;line-height:1.08;letter-spacing:-1.8px;color:#fff;">
        “{headline}”
      </div>
      {sub_html}
    </div>
    <div style="position:absolute;left:72px;bottom:220px;width:330px;height:4px;background:linear-gradient(90deg,{acc},transparent);box-shadow:0 0 22px {acc};border-radius:999px;"></div>
    <div style="position:absolute;right:72px;bottom:180px;width:260px;height:260px;border-radius:34px;background:rgba(255,255,255,0.05);border:1px solid rgba(255,255,255,0.1);backdrop-filter:blur(12px);padding:26px 22px;">
      <div style="font-size:20px;letter-spacing:0.16em;color:rgba(255,255,255,0.6);margin-bottom:12px;">KEYWORD</div>
      <div style="font-size:46px;font-weight:900;color:{acc};line-height:1.05;">记不住</div>
      <div style="margin-top:18px;font-size:20px;color:rgba(255,255,255,0.65);line-height:1.5;">把“记住”变成系统行为，而不是脑力消耗。</div>
    </div>
    <div class="scene-label" style="position:absolute;top:24px;left:24px;font-size:14px;color:{acc};opacity:0.7;">{sid} · {role}</div>
    """


def _render_hook_big_number_left(sid: str, role: str, headline: str, sub: str, acc: str) -> str:
    sub_html = f"<div style='font-size:28px;color:rgba(255,255,255,0.62);margin-top:18px;max-width:480px;line-height:1.5;'>{sub}</div>" if sub else ""
    return f"""
    <div data-motion-target="scene-bg" style="position:absolute;inset:0;background:linear-gradient(135deg,#0A1628 0%,#07121C 58%,#0A1A2E 100%);">
      <div class="bg-grid"></div>
      <div class="bg-glow bg-glow-1" style="background:radial-gradient(circle,{acc}28 0%,transparent 66%);"></div>
    </div>
    <div style="position:absolute;top:150px;left:72px;width:360px;">
      <div style="font-size:18px;letter-spacing:0.22em;color:{acc};margin-bottom:16px;">DATA / IMPACT</div>
      <div style="font-size:138px;font-weight:900;line-height:0.9;color:{acc};text-shadow:0 0 42px {acc}80;">100</div>
      <div style="font-size:28px;font-weight:700;color:#fff;margin-top:8px;">本书</div>
    </div>
    <div style="position:absolute;top:190px;right:72px;width:500px;padding:28px 26px;border-radius:28px;background:rgba(255,255,255,0.05);border:1px solid rgba(255,255,255,0.1);">
      <div style="font-size:22px;letter-spacing:0.18em;color:rgba(255,255,255,0.55);margin-bottom:18px;">HOOK</div>
      <div style="font-size:62px;font-weight:900;line-height:1.1;letter-spacing:-1.2px;color:#fff;">{headline}</div>
      {sub_html}
    </div>
    <div style="position:absolute;left:72px;bottom:180px;width:880px;height:2px;background:linear-gradient(90deg,{acc},transparent);box-shadow:0 0 18px {acc};"></div>
    <div class="scene-label" style="position:absolute;top:24px;left:24px;font-size:14px;color:{acc};opacity:0.7;">{sid} · {role}</div>
    """


def _css_hook_big_claim(sid: str, role: str, scene: dict[str, Any]) -> str:
    acc = _accent(role)
    return f"""
.{sid.lower()}-hook-main {{ position:absolute; top:420px; left:72px; right:72px; text-align:center; }}
.{sid.lower()}-hook-title {{ font-size:72px; font-weight:700; color:#fff; line-height:1.15; letter-spacing:-1px; }}
.{sid.lower()}-hook-sub {{ font-size:32px; color:rgba(255,255,255,0.65); margin-top:20px; }}
.{sid.lower()}-bg-grid {{ position:absolute; inset:0; pointer-events:none; background-image:linear-gradient({acc}08 1px,transparent 1px),linear-gradient(90deg,{acc}08 1px,transparent 1px); background-size:72px 72px; animation:grid-drift 18s linear infinite; }}
.{sid.lower()}-bg-glow {{ position:absolute; width:420px; height:420px; border-radius:50%; animation:glow-pulse 3.5s ease-in-out infinite; pointer-events:none; }}
.{sid.lower()}-bg-glow-1 {{ top:-120px; left:-80px; animation-delay:0s; }}
.{sid.lower()}-bg-glow-2 {{ bottom:-140px; right:-60px; animation-delay:1.8s; }}
@keyframes grid-drift {{ 0%{{background-position:0 0;}} 100%{{background-position:72px 72px;}} }}
@keyframes glow-pulse {{ 0%,100%{{opacity:0.5;transform:scale(1);}} 50%{{opacity:0.8;transform:scale(1.15);}} }}
"""


def _gsap_hook_big_claim(sid: str, role: str, scene: dict[str, Any], start: float, duration: float) -> str:
    return f"""
const tl_{sid}=gsap.timeline({{paused:true}});
window.__timelines['{sid}']=tl_{sid};
tl_{sid}.fromTo('[data-scene-id="{sid}"] .hook-title',{{y:80,opacity:0}},{{y:0,opacity:1,duration:1.0,ease:'power3.out'}},0);
tl_{sid}.fromTo('[data-scene-id="{sid}"] .hook-sub',{{y:40,opacity:0}},{{y:0,opacity:1,duration:0.7,ease:'power2.out'}},0.4);
tl_{sid}.fromTo('[data-scene-id="{sid}"] .bg-grid',{{opacity:0}},{{opacity:1,duration:1.2}},0);
"""


# ─────────────────────────────────────────────────────────────────
# TEMPLATE 2 — pain_card_stack
# S02: 4 stacked cards showing scattered collection types
# ─────────────────────────────────────────────────────────────────

def _template_pain_card_stack(sid: str, role: str, scene: dict[str, Any]) -> str:
    acc = _accent(role)
    # Cards data from scene or defaults
    cards = scene.get("cards", [
        {"icon": "📱", "text": "微信收藏", "sub": "999+ 条"},
        {"icon": "🔖", "text": "浏览器书签", "sub": "500+ 条"},
        {"icon": "📚", "text": "读书笔记", "sub": "100 本书"},
        {"icon": "🎙️", "text": "会议录音", "sub": "随时找不到了"},
    ])
    conclusion = scene.get("conclusion", "真正要写时，还是一片空白")
    card_htmls = []
    for i, card in enumerate(cards):
        top = 280 + i * 160
        opacity = 1.0 - i * 0.12
        card_htmls.append(f"""
        <div class="pain-card" id="{sid.lower()}-card-{i}" style="
            position:absolute;top:{top}px;left:72px;right:72px;
            background:rgba(255,255,255,0.05);border:1px solid rgba(255,255,255,0.12);
            border-radius:16px;padding:24px 28px;display:flex;align-items:center;gap:20px;
            opacity:{opacity};
        ">
            <span style="font-size:40px;">{card['icon']}</span>
            <div>
                <div style="font-size:36px;font-weight:600;color:#fff;">{card['text']}</div>
                <div style="font-size:24px;color:rgba(255,255,255,0.5);margin-top:4px;">{card['sub']}</div>
            </div>
            <div style="margin-left:auto;font-size:28px;color:{acc};opacity:0.6;">→</div>
        </div>
        """)
    cards_html = "\n".join(card_htmls)
    conclusion_html = f"""
    <div class="pain-conclusion" style="
        position:absolute;bottom:200px;left:72px;right:72px;text-align:center;
        font-size:36px;font-weight:600;color:{acc};
    ">{conclusion}</div>
    """
    return f"""
    <div data-motion-target="scene-bg" style="position:absolute;inset:0;background:{_bg(role)};">
      <div class="bg-grid"></div>
    </div>
    {cards_html}
    {conclusion_html}
    <div class="scene-label" style="position:absolute;top:24px;left:24px;font-size:14px;color:{acc};opacity:0.7;">{sid} · {role}</div>
"""


def _css_pain_card_stack(sid: str, role: str, scene: dict[str, Any]) -> str:
    acc = _accent(role)
    return f"""
.{sid.lower()}-pain-card {{ transition: transform 0.3s ease; }}
.{sid.lower()}-pain-card:hover {{ transform: translateX(8px); }}
.{sid.lower()}-pain-conclusion {{ font-size:36px; font-weight:600; color:{acc}; text-align:center; }}
.{sid.lower()}-bg-grid {{ position:absolute; inset:0; pointer-events:none; background-image:linear-gradient({acc}06 1px,transparent 1px),linear-gradient(90deg,{acc}06 1px,transparent 1px); background-size:72px 72px; animation:grid-drift 18s linear infinite; }}
@keyframes grid-drift {{ 0%{{background-position:0 0;}} 100%{{background-position:72px 72px;}} }}
"""


def _gsap_pain_card_stack(sid: str, role: str, scene: dict[str, Any], start: float, duration: float) -> str:
    return f"""
const tl_{sid}=gsap.timeline({{paused:true}});
window.__timelines['{sid}']=tl_{sid};
tl_{sid}.fromTo('[data-scene-id="{sid}"] .pain-card',{{y:60,opacity:0}},{{y:0,opacity:1,duration:0.5,ease:'power2.out'}},0);
tl_{sid}.fromTo('[data-scene-id="{sid}"] .pain-conclusion',{{y:30,opacity:0}},{{y:0,opacity:1,duration:0.5,ease:'power2.out'}},0.8);
tl_{sid}.fromTo('[data-scene-id="{sid}"] .bg-grid',{{opacity:0}},{{opacity:1,duration:1.0}},0);
"""


# ─────────────────────────────────────────────────────────────────
# TEMPLATE 3 — broken_chain
# S03/S04: 4-node chain with broken connectors
# ─────────────────────────────────────────────────────────────────

def _template_broken_chain(sid: str, role: str, scene: dict[str, Any]) -> str:
    acc = _accent(role)
    layout_variant = scene.get("layout_variant", "chain_flow")
    headline = scene.get("headline", "输入→整理→回顾→输出，四个环节全断开")
    headline_html = f"""
    <div style="position:absolute;top:240px;left:72px;right:72px;text-align:center;">
        <div style="font-size:52px;font-weight:700;color:#fff;line-height:1.2;">{headline}</div>
    </div>
    """
    layout_html = _render_broken_chain_layout(scene, acc, layout_variant)
    return f"""
    <div data-motion-target="scene-bg" style="position:absolute;inset:0;background:{_bg(role)};">
      <div class="bg-grid"></div>
    </div>
    {headline_html}
    {layout_html}
    <div class="scene-label" style="position:absolute;top:24px;left:24px;font-size:14px;color:{acc};opacity:0.7;">{sid} · {role}</div>
"""


def _css_broken_chain(sid: str, role: str, scene: dict[str, Any]) -> str:
    acc = _accent(role)
    return f"""
.{sid.lower()}-chain-node {{ transition: border-color 0.3s ease; }}
.{sid.lower()}-bg-grid {{ position:absolute; inset:0; pointer-events:none; background-image:linear-gradient({acc}06 1px,transparent 1px),linear-gradient(90deg,{acc}06 1px,transparent 1px); background-size:72px 72px; animation:grid-drift 18s linear infinite; }}
@keyframes grid-drift {{ 0%{{background-position:0 0;}} 100%{{background-position:72px 72px;}} }}
"""


def _gsap_broken_chain(sid: str, role: str, scene: dict[str, Any], start: float, duration: float) -> str:
    return f"""
const tl_{sid}=gsap.timeline({{paused:true}});
window.__timelines['{sid}']=tl_{sid};
tl_{sid}.fromTo('[data-scene-id="{sid}"] .chain-node',{{y:60,opacity:0}},{{y:0,opacity:1,duration:0.6,ease:'back.out(1.2)'}},0);
tl_{sid}.fromTo('[data-scene-id="{sid}"] .bg-grid',{{opacity:0}},{{opacity:1,duration:1.0}},0);
"""


def _render_broken_chain_layout(scene: dict[str, Any], acc: str, layout_variant: str) -> str:
    if layout_variant == "responsibility_split":
        return _render_responsibility_split_layout(scene, acc)
    if layout_variant == "binary_choice_split":
        return _render_binary_choice_split_layout(scene, acc)
    return _render_chain_flow_layout(scene, acc)


def _render_chain_flow_layout(scene: dict[str, Any], acc: str) -> str:
    nodes = scene.get("chain_nodes", ["输入", "整理", "回顾", "输出"])
    node_width = 180
    gap = 60
    total_w = 4 * node_width + 3 * gap
    start_x = (1080 - total_w) // 2
    node_y = 500
    broken_slots = scene.get("broken_slots", [1, 2, 3])
    node_htmls = []
    connector_htmls = []
    for i, node in enumerate(nodes):
        x = start_x + i * (node_width + gap)
        node_color = "#FF4757" if i in broken_slots else acc
        node_htmls.append(f"""
        <div class="chain-node" style="
            position:absolute;top:{node_y}px;left:{x}px;width:{node_width}px;height:120px;
            background:rgba(255,255,255,0.08);border:2px solid {node_color};
            border-radius:20px;display:flex;align-items:center;justify-content:center;
            font-size:32px;font-weight:700;color:#fff;
        ">{node}</div>
        """)
        if i < 3:
            conn_x = x + node_width
            is_broken = i in broken_slots
            conn_color = "#FF4757" if is_broken else acc
            conn_icon = "✗" if is_broken else "→"
            connector_htmls.append(f"""
            <div class="tool-connector" style="
                position:absolute;top:{node_y + 40}px;left:{conn_x}px;width:{gap}px;text-align:center;
                font-size:36px;color:{conn_color};
            ">{conn_icon}</div>
            """)
    return "\n".join(node_htmls + connector_htmls)


def _render_responsibility_split_layout(scene: dict[str, Any], acc: str) -> str:
    left = scene.get("left_panel", {"label": "大脑", "title": "思考与创造", "items": ["判断重点", "提出观点", "做最终决策"]})
    right = scene.get("right_panel", {"label": "第二大脑", "title": "存储与检索", "items": ["统一收纳", "随时回查", "给 AI 提供上下文"]})
    footer = scene.get("footer_note", "把记忆负担迁出去，让创造力留在脑内")
    bridge = scene.get("bridge_label", "职责分工")
    panels = []
    for panel, x, label_color, panel_bg in (
        (left, 80, "#FF6B35", "linear-gradient(180deg, rgba(255,107,53,0.12), rgba(255,255,255,0.04))"),
        (right, 540, acc, "linear-gradient(180deg, rgba(37,216,255,0.12), rgba(255,255,255,0.04))"),
    ):
        items_html = "".join(
            f"<div class='chain-node' style='margin-bottom:16px;padding:16px 18px;background:rgba(255,255,255,0.05);border-radius:14px;font-size:28px;color:#fff;border-left:3px solid {label_color};'>{item}</div>"
            for item in panel.get("items", [])
        )
        panels.append(f"""
        <div class="chain-node" style="
            position:absolute;top:420px;left:{x}px;width:456px;height:620px;
            background:{panel_bg};border:2px solid {label_color};
            border-radius:30px;padding:30px 26px 24px;box-shadow:0 0 38px {label_color}18;
        ">
            <div style="font-size:22px;letter-spacing:0.18em;color:{label_color};margin-bottom:12px;">{panel.get('label', '')}</div>
            <div style="font-size:44px;font-weight:900;color:#fff;margin-bottom:18px;line-height:1.08;">{panel.get('title', '')}</div>
            {items_html}
        </div>
        """)
    return f"""
    {''.join(panels)}
    <div class="tool-connector" style="position:absolute;top:760px;left:468px;width:144px;height:2px;background:linear-gradient(90deg,#FF6B35,{acc});box-shadow:0 0 18px {acc};"></div>
    <div style="position:absolute;top:708px;left:432px;width:216px;text-align:center;font-size:22px;letter-spacing:0.14em;color:rgba(255,255,255,0.62);">{bridge}</div>
    <div style="position:absolute;top:1090px;left:150px;right:150px;padding:20px 24px;border:1px solid rgba(255,255,255,0.14);border-radius:18px;background:rgba(255,255,255,0.04);text-align:center;font-size:28px;color:rgba(255,255,255,0.72);">{footer}</div>
    """


def _render_binary_choice_split_layout(scene: dict[str, Any], acc: str) -> str:
    left = scene.get("left_choice", {"label": "不要", "title": "一上来堆插件", "items": ["界面越来越复杂", "系统还没开始工作"]})
    right = scene.get("right_choice", {"label": "先做", "title": "跑通最小闭环", "items": ["先统一输入", "再补检索和输出"]})
    footer = scene.get("footer_note", "先让系统跑起来，再决定哪里该加复杂度")
    left_items = "".join(
        f"<div class='chain-node' style='margin-bottom:14px;padding:14px 16px;background:rgba(255,71,87,0.08);border-radius:14px;font-size:26px;color:#fff;'>{item}</div>"
        for item in left.get("items", [])
    )
    right_items = "".join(
        f"<div class='chain-node' style='margin-bottom:14px;padding:14px 16px;background:rgba(46,213,115,0.08);border-radius:14px;font-size:26px;color:#fff;'>{item}</div>"
        for item in right.get("items", [])
    )
    return f"""
    <div class="chain-node" style="position:absolute;top:390px;left:72px;width:444px;height:700px;background:linear-gradient(180deg,rgba(255,71,87,0.14),rgba(255,255,255,0.04));border:2px solid #FF4757;border-radius:32px;padding:30px 26px;box-shadow:0 0 40px rgba(255,71,87,0.16);">
        <div style="font-size:20px;letter-spacing:0.16em;color:#FF4757;margin-bottom:10px;">{left.get('label', '不要')}</div>
        <div style="font-size:44px;font-weight:900;color:#fff;margin-bottom:20px;line-height:1.08;">{left.get('title', '')}</div>
        {left_items}
    </div>
    <div style="position:absolute;top:650px;left:512px;width:56px;height:56px;border-radius:50%;display:flex;align-items:center;justify-content:center;background:rgba(255,255,255,0.06);border:1px solid rgba(255,255,255,0.14);font-size:24px;color:rgba(255,255,255,0.7);">VS</div>
    <div class="chain-node" style="position:absolute;top:390px;right:72px;width:444px;height:700px;background:linear-gradient(180deg,rgba(46,213,115,0.14),rgba(255,255,255,0.04));border:2px solid {acc};border-radius:32px;padding:30px 26px;box-shadow:0 0 40px rgba(46,213,115,0.12);">
        <div style="font-size:20px;letter-spacing:0.16em;color:{acc};margin-bottom:10px;">{right.get('label', '先做')}</div>
        <div style="font-size:44px;font-weight:900;color:#fff;margin-bottom:20px;line-height:1.08;">{right.get('title', '')}</div>
        {right_items}
    </div>
    <div class="tool-connector" style="position:absolute;top:1130px;left:214px;right:214px;height:2px;background:linear-gradient(90deg,#FF4757,{acc});box-shadow:0 0 18px {acc};"></div>
    <div style="position:absolute;top:1170px;left:164px;right:164px;padding:20px 24px;border-radius:18px;background:rgba(255,255,255,0.04);border:1px solid rgba(255,255,255,0.14);text-align:center;font-size:28px;color:rgba(255,255,255,0.72);">{footer}</div>
    """


# ─────────────────────────────────────────────────────────────────
# TEMPLATE 4 — tool_chain_three_cols
# S05/S06/S07/S08: Three-column tool chain
# ─────────────────────────────────────────────────────────────────

def _template_tool_chain_three_cols(sid: str, role: str, scene: dict[str, Any]) -> str:
    acc = _accent(role)
    col_data = scene.get("three_cols", [
        {"name": "Obsidian", "func": "统一入口", "icon": "📥", "detail": "所有素材进一个库"},
        {"name": "Codex", "func": "整理结构", "icon": "✍️", "detail": "AI读笔记写草稿"},
        {"name": "Hermes", "func": "定时回顾", "icon": "⏰", "detail": "采集·评分·复盘"},
    ])
    layout_variant = scene.get("layout_variant", "three_col_row")
    headline = scene.get("headline", "三个工具串起来，各司其职")
    headline_html = f"""
    <div style="position:absolute;top:240px;left:72px;right:72px;text-align:center;">
        <div style="font-size:52px;font-weight:700;color:#fff;line-height:1.2;">{headline}</div>
    </div>
    """
    cols_html = _render_tool_chain_layout(col_data, acc, layout_variant)
    return f"""
    <div data-motion-target="scene-bg" style="position:absolute;inset:0;background:{_bg(role)};">
      <div class="bg-grid"></div>
    </div>
    {headline_html}
    {cols_html}
    <div class="scene-label" style="position:absolute;top:24px;left:24px;font-size:14px;color:{acc};opacity:0.7;">{sid} · {role}</div>
"""


def _css_tool_chain_three_cols(sid: str, role: str, scene: dict[str, Any]) -> str:
    acc = _accent(role)
    return f"""
.{sid.lower()}-tool-col {{ transition: transform 0.3s ease; }}
.{sid.lower()}-tool-col:hover {{ transform: translateY(-8px); }}
.{sid.lower()}-bg-grid {{ position:absolute; inset:0; pointer-events:none; background-image:linear-gradient({acc}06 1px,transparent 1px),linear-gradient(90deg,{acc}06 1px,transparent 1px); background-size:72px 72px; animation:grid-drift 18s linear infinite; }}
@keyframes grid-drift {{ 0%{{background-position:0 0;}} 100%{{background-position:72px 72px;}} }}
"""


def _gsap_tool_chain_three_cols(sid: str, role: str, scene: dict[str, Any], start: float, duration: float) -> str:
    return f"""
const tl_{sid}=gsap.timeline({{paused:true}});
window.__timelines['{sid}']=tl_{sid};
tl_{sid}.fromTo('[data-scene-id="{sid}"] .tool-col',{{y:60,opacity:0}},{{y:0,opacity:1,duration:0.6,ease:'back.out(1.2)'}},0);
tl_{sid}.fromTo('[data-scene-id="{sid}"] .tool-connector',{{opacity:0}},{{opacity:1,duration:0.5,ease:'power2.out'}},0.2);
tl_{sid}.fromTo('[data-scene-id="{sid}"] .bg-grid',{{opacity:0}},{{opacity:1,duration:1.0}},0);
"""


def _render_tool_chain_layout(col_data: list[dict[str, Any]], acc: str, layout_variant: str) -> str:
    if layout_variant == "source_ingest":
        return _render_source_ingest_layout(col_data, acc)
    if layout_variant == "knowledge_triangle":
        return _render_knowledge_triangle_layout(col_data, acc)
    if layout_variant == "vertical_flow":
        return _render_vertical_flow_layout(col_data, acc)
    if layout_variant == "matrix_glossary_wall":
        return _render_matrix_glossary_wall_layout(col_data, acc)
    if layout_variant == "intro_offset":
        return _render_intro_offset_layout(col_data, acc)
    return _render_three_col_row_layout(col_data, acc)


def _render_tool_col(
    *,
    col: dict[str, Any],
    acc: str,
    x: int,
    y: int,
    width: int,
    padding: str = "28px 20px",
) -> str:
    return f"""
    <div class="tool-col" style="
        position:absolute;top:{y}px;left:{x}px;width:{width}px;
        background:rgba(255,255,255,0.06);border:2px solid {acc};
        border-radius:20px;padding:{padding};text-align:center;
    ">
        <div style="font-size:56px;margin-bottom:12px;">{col['icon']}</div>
        <div style="font-size:32px;font-weight:700;color:#fff;margin-bottom:8px;">{col['name']}</div>
        <div style="font-size:28px;font-weight:600;color:{acc};margin-bottom:8px;">{col['func']}</div>
        <div style="font-size:22px;color:rgba(255,255,255,0.55);">{col['detail']}</div>
    </div>
    """


def _render_three_col_row_layout(col_data: list[dict[str, Any]], acc: str) -> str:
    col_width = 280
    gap = 60
    total_w = 3 * col_width + 2 * gap
    start_x = (1080 - total_w) // 2
    col_y = 520
    parts: list[str] = []
    for i, col in enumerate(col_data):
        x = start_x + i * (col_width + gap)
        parts.append(_render_tool_col(col=col, acc=acc, x=x, y=col_y, width=col_width))
        if i < 2:
            arrow_x = x + col_width
            parts.append(
                f'<div class="tool-connector" style="position:absolute;top:{col_y + 60}px;left:{arrow_x}px;width:{gap}px;text-align:center;font-size:40px;color:{acc};">→</div>'
            )
    return "\n".join(parts)


def _render_source_ingest_layout(col_data: list[dict[str, Any]], acc: str) -> str:
    card_width = 250
    gap = 40
    start_x = (1080 - (3 * card_width + 2 * gap)) // 2
    top_y = 500
    hub_y = 980
    parts: list[str] = []
    for i, col in enumerate(col_data):
        x = start_x + i * (card_width + gap)
        parts.append(_render_tool_col(col=col, acc=acc, x=x, y=top_y, width=card_width, padding="24px 18px"))
        center_x = x + card_width // 2 - 16
        parts.append(
            f'<div class="tool-connector" style="position:absolute;top:{top_y + 270}px;left:{center_x}px;font-size:40px;color:{acc};">↓</div>'
        )
    parts.append(f"""
    <div class="tool-connector" style="
        position:absolute;top:{hub_y - 22}px;left:240px;right:240px;height:2px;
        background:linear-gradient(90deg,transparent,{acc},transparent);
        box-shadow:0 0 18px {acc};
    "></div>
    <div class="tool-col" style="
        position:absolute;top:{hub_y}px;left:270px;right:270px;
        background:rgba(37,216,255,0.09);border:2px solid {acc};
        border-radius:22px;padding:28px 24px;text-align:center;
    ">
        <div style="font-size:28px;letter-spacing:0.2em;color:{acc};margin-bottom:10px;">INGEST HUB</div>
        <div style="font-size:42px;font-weight:800;color:#fff;margin-bottom:8px;">统一进入 Obsidian</div>
        <div style="font-size:24px;color:rgba(255,255,255,0.62);">把读书、网页、语音、视频素材汇到同一个入口</div>
    </div>
    """)
    return "\n".join(parts)


def _render_knowledge_triangle_layout(col_data: list[dict[str, Any]], acc: str) -> str:
    positions = [(360, 470), (80, 900), (640, 900)]
    widths = [360, 280, 280]
    parts: list[str] = []
    for col, (x, y), width in zip(col_data, positions, widths):
        parts.append(_render_tool_col(col=col, acc=acc, x=x, y=y, width=width, padding="26px 20px"))
    parts.append(f"""
    <div class="tool-connector" style="position:absolute;top:780px;left:270px;width:180px;height:2px;background:{acc};transform:rotate(35deg);transform-origin:left center;box-shadow:0 0 16px {acc};"></div>
    <div class="tool-connector" style="position:absolute;top:780px;left:630px;width:180px;height:2px;background:{acc};transform:rotate(-35deg);transform-origin:left center;box-shadow:0 0 16px {acc};"></div>
    <div class="tool-connector" style="position:absolute;top:1090px;left:360px;width:360px;height:2px;background:linear-gradient(90deg,{acc},rgba(37,216,255,0.35),{acc});box-shadow:0 0 16px {acc};"></div>
    <div style="position:absolute;top:1220px;left:220px;right:220px;text-align:center;font-size:28px;color:rgba(255,255,255,0.62);">观点、例子、方法在同一网络里互相可达</div>
    """)
    return "\n".join(parts)


def _render_vertical_flow_layout(col_data: list[dict[str, Any]], acc: str) -> str:
    x = 140
    width = 800
    start_y = 470
    gap = 210
    parts: list[str] = []
    for i, col in enumerate(col_data):
        y = start_y + i * gap
        parts.append(f"""
        <div class="tool-col" style="
            position:absolute;top:{y}px;left:{x}px;width:{width}px;
            background:rgba(255,255,255,0.06);border:2px solid {acc};
            border-radius:20px;padding:24px 28px;display:flex;align-items:center;gap:24px;
        ">
            <div style="width:86px;height:86px;border-radius:18px;background:rgba(37,216,255,0.12);display:flex;align-items:center;justify-content:center;font-size:44px;flex-shrink:0;">{i+1}</div>
            <div style="width:84px;font-size:38px;text-align:center;flex-shrink:0;">{col['icon']}</div>
            <div style="flex:1;">
                <div style="font-size:34px;font-weight:700;color:#fff;margin-bottom:6px;">{col['name']}</div>
                <div style="font-size:28px;font-weight:600;color:{acc};margin-bottom:8px;">{col['func']}</div>
                <div style="font-size:22px;color:rgba(255,255,255,0.55);">{col['detail']}</div>
            </div>
        </div>
        """)
        if i < len(col_data) - 1:
            parts.append(
                f'<div class="tool-connector" style="position:absolute;top:{y + 150}px;left:510px;font-size:40px;color:{acc};">↓</div>'
            )
    return "\n".join(parts)


def _render_intro_offset_layout(col_data: list[dict[str, Any]], acc: str) -> str:
    base_x = 78
    top_y = 430
    parts: list[str] = []
    intro = col_data[0] if col_data else {"name": "Obsidian", "func": "先搭系统", "icon": "📥", "detail": "把素材统一收进来"}
    middle = col_data[1] if len(col_data) > 1 else {"name": "AI", "func": "再找结构", "icon": "✍️", "detail": "从笔记里拉出草稿"}
    tail = col_data[2] if len(col_data) > 2 else {"name": "输出", "func": "最后成稿", "icon": "⏰", "detail": "输出时不从零开始"}
    parts.append(f"""
    <div class="tool-col" style="
        position:absolute;top:{top_y}px;left:{base_x}px;width:520px;height:360px;
        background:linear-gradient(180deg,rgba(37,216,255,0.12),rgba(255,255,255,0.05));border:2px solid {acc};
        border-radius:28px;padding:28px 24px;box-shadow:0 0 40px {acc}16;text-align:left;
    ">
        <div style="font-size:22px;letter-spacing:0.18em;color:{acc};margin-bottom:10px;">INTRO / ANCHOR</div>
        <div style="font-size:54px;font-weight:900;color:#fff;line-height:1.05;margin-bottom:14px;">{intro['name']}</div>
        <div style="font-size:30px;font-weight:700;color:{acc};margin-bottom:12px;">{intro['func']}</div>
        <div style="font-size:24px;color:rgba(255,255,255,0.68);max-width:400px;line-height:1.45;">{intro['detail']}</div>
    </div>
    """)
    parts.append(f"""
    <div class="tool-connector" style="position:absolute;top:{top_y + 150}px;left:638px;width:160px;height:2px;background:linear-gradient(90deg,{acc},transparent);box-shadow:0 0 18px {acc};"></div>
    """)
    parts.append(f"""
    <div class="tool-col" style="
        position:absolute;top:{top_y + 28}px;right:78px;width:340px;height:148px;
        background:rgba(255,255,255,0.06);border:2px solid {acc};border-radius:24px;padding:20px 18px;
    ">
        <div style="font-size:18px;letter-spacing:0.18em;color:rgba(255,255,255,0.55);margin-bottom:8px;">NEXT</div>
        <div style="font-size:36px;font-weight:800;color:#fff;">{middle['name']}</div>
        <div style="font-size:22px;color:rgba(255,255,255,0.64);margin-top:6px;">{middle['func']}</div>
    </div>
    """)
    parts.append(f"""
    <div class="tool-col" style="
        position:absolute;top:{top_y + 210}px;right:78px;width:340px;height:148px;
        background:rgba(255,255,255,0.06);border:2px solid {acc};border-radius:24px;padding:20px 18px;
    ">
        <div style="font-size:18px;letter-spacing:0.18em;color:rgba(255,255,255,0.55);margin-bottom:8px;">OUTCOME</div>
        <div style="font-size:36px;font-weight:800;color:#fff;">{tail['name']}</div>
        <div style="font-size:22px;color:rgba(255,255,255,0.64);margin-top:6px;">{tail['func']}</div>
    </div>
    """)
    parts.append("""
    <div style="position:absolute;top:1160px;left:120px;right:120px;height:1px;background:rgba(255,255,255,0.12);"></div>
    """)
    return "\n".join(parts)


def _render_matrix_glossary_wall_layout(col_data: list[dict[str, Any]], acc: str) -> str:
    positions = [(88, 470), (548, 470), (88, 940), (548, 940)]
    items = list(col_data[:4])
    while len(items) < 4:
        items.append({"name": "术语", "func": "定义", "icon": "•", "detail": "补充上下文"})
    parts: list[str] = []
    for idx, (col, (x, y)) in enumerate(zip(items, positions), start=1):
        parts.append(f"""
        <div class="tool-col" style="
            position:absolute;top:{y}px;left:{x}px;width:444px;height:330px;
            background:rgba(255,255,255,0.06);border:2px solid {acc};
            border-radius:22px;padding:24px 22px;
        ">
            <div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:18px;">
                <div style="font-size:24px;letter-spacing:0.16em;color:{acc};">TERM {idx:02d}</div>
                <div style="font-size:34px;color:#fff;">{col['icon']}</div>
            </div>
            <div style="font-size:36px;font-weight:800;color:#fff;margin-bottom:10px;">{col['name']}</div>
            <div style="font-size:28px;font-weight:600;color:{acc};margin-bottom:14px;">{col['func']}</div>
            <div style="font-size:24px;line-height:1.45;color:rgba(255,255,255,0.68);">{col['detail']}</div>
        </div>
        """)
    parts.append(f"""
    <div style="position:absolute;top:872px;left:502px;width:76px;height:76px;border-radius:50%;border:2px solid {acc};background:rgba(37,216,255,0.08);display:flex;align-items:center;justify-content:center;font-size:20px;letter-spacing:0.14em;color:{acc};">MAP</div>
    """)
    return "\n".join(parts)


# ─────────────────────────────────────────────────────────────────
# TEMPLATE 5 — before_after_compare
# S09: Left/right comparison
# ─────────────────────────────────────────────────────────────────

def _template_before_after_compare(sid: str, role: str, scene: dict[str, Any]) -> str:
    acc = _accent(role)
    layout_variant = scene.get("layout_variant", "compare_columns")
    headline = scene.get("headline", "以前每次像从零开始，现在至少能先拿到一版可改的草稿")
    headline_html = f"""
    <div style="position:absolute;top:180px;left:72px;right:72px;text-align:center;">
        <div style="font-size:46px;font-weight:700;color:#fff;line-height:1.2;">{headline}</div>
    </div>
    """
    layout_html = _render_compare_layout(scene, acc, layout_variant)
    return f"""
    <div data-motion-target="scene-bg" style="position:absolute;inset:0;background:{_bg(role)};">
      <div class="bg-grid"></div>
    </div>
    {headline_html}
    {layout_html}
    <div class="scene-label" style="position:absolute;top:24px;left:24px;font-size:14px;color:{acc};opacity:0.7;">{sid} · {role}</div>
"""


def _css_before_after_compare(sid: str, role: str, scene: dict[str, Any]) -> str:
    acc = _accent(role)
    return f"""
.{sid.lower()}-compare-item {{ transition: background 0.2s ease; }}
.{sid.lower()}-compare-item:hover {{ background: rgba(255,255,255,0.1); }}
.{sid.lower()}-bg-grid {{ position:absolute; inset:0; pointer-events:none; background-image:linear-gradient({acc}06 1px,transparent 1px),linear-gradient(90deg,{acc}06 1px,transparent 1px); background-size:72px 72px; animation:grid-drift 18s linear infinite; }}
@keyframes grid-drift {{ 0%{{background-position:0 0;}} 100%{{background-position:72px 72px;}} }}
"""


def _gsap_before_after_compare(sid: str, role: str, scene: dict[str, Any], start: float, duration: float) -> str:
    return f"""
const tl_{sid}=gsap.timeline({{paused:true}});
window.__timelines['{sid}']=tl_{sid};
tl_{sid}.fromTo('[data-scene-id="{sid}"] .compare-item',{{x:-40,opacity:0}},{{x:0,opacity:1,duration:0.5,ease:'power2.out'}},0);
tl_{sid}.fromTo('[data-scene-id="{sid}"] .bg-grid',{{opacity:0}},{{opacity:1,duration:1.0}},0);
"""


def _render_compare_layout(scene: dict[str, Any], acc: str, layout_variant: str) -> str:
    if layout_variant == "dashboard_mobile":
        return _render_dashboard_mobile_layout(scene, acc)
    if layout_variant == "parallel_lanes":
        return _render_parallel_lanes_layout(scene, acc)
    if layout_variant == "symptom_panel":
        return _render_symptom_panel_layout(scene, acc)
    return _render_compare_columns_layout(scene, acc)


def _render_compare_columns_layout(scene: dict[str, Any], acc: str) -> str:
    left_items = scene.get("left_items", ["到处找资料", "从空白文档开始", "写一半卡住"])
    right_items = scene.get("right_items", ["统一入口", "先有结构", "拿到可改草稿"])
    left_label = scene.get("left_label", "以前")
    right_label = scene.get("right_label", "现在")
    col_width = 380
    gap = 40
    total_w = 2 * col_width + gap
    start_x = (1080 - total_w) // 2
    label_y = 320
    item_y = 440

    def make_col(label, items, x, label_color):
        items_html = []
        for item in items:
            items_html.append(f"""
            <div class="compare-item" style="
                margin-bottom:20px;padding:16px 20px;
                background:rgba(255,255,255,0.05);border-radius:12px;
                display:flex;align-items:center;gap:12px;
            ">
                <span style="color:{label_color};font-size:28px;">{'✓' if label_color == '#2ED573' else '✗'}</span>
                <span style="font-size:30px;color:#fff;">{item}</span>
            </div>
            """)
        return f"""
        <div style="position:absolute;top:0;left:{x}px;width:{col_width}px;height:100%;">
            <div style="position:absolute;top:{label_y}px;left:0;right:0;text-align:center;">
                <span style="font-size:40px;font-weight:800;color:{label_color};padding:8px 28px;border:2px solid {label_color};border-radius:12px;">{label}</span>
            </div>
            <div style="position:absolute;top:{item_y}px;left:0;right:0;">{''.join(items_html)}</div>
        </div>
        """

    left_col = make_col(left_label, left_items, start_x, "#FF4757")
    right_col = make_col(right_label, right_items, start_x + col_width + gap, "#2ED573")
    return f"{left_col}{right_col}"


def _render_dashboard_mobile_layout(scene: dict[str, Any], acc: str) -> str:
    left_items = scene.get("left_items", ["翻遍多个 App", "素材散在各处", "写作前先找半天"])
    metrics = scene.get("dashboard_metrics", [
        {"label": "取材时间", "value": "30s"},
        {"label": "入口数量", "value": "1"},
        {"label": "素材包", "value": "READY"},
    ])
    old_html = "".join(
        f"<div class='compare-item' style='margin-bottom:18px;padding:18px 18px;background:rgba(255,255,255,0.05);border-radius:14px;font-size:28px;color:#fff;'><span style='color:#FF4757;margin-right:10px;'>✗</span>{item}</div>"
        for item in left_items
    )
    metrics_html = "".join(
        f"<div class='compare-item' style='margin-bottom:16px;padding:16px 18px;background:rgba(37,216,255,0.08);border-radius:14px;display:flex;align-items:center;justify-content:space-between;'><span style='font-size:24px;color:rgba(255,255,255,0.7);'>{item['label']}</span><b style='font-size:34px;color:{acc};'>{item['value']}</b></div>"
        for item in metrics
    )
    return f"""
    <div style="position:absolute;top:400px;left:86px;width:392px;">
        <div style="font-size:22px;letter-spacing:0.16em;color:#FF4757;margin-bottom:14px;">OLD FLOW</div>
        {old_html}
    </div>
    <div class="compare-item" style="position:absolute;top:360px;right:104px;width:388px;height:880px;background:linear-gradient(180deg,rgba(6,12,22,0.95),rgba(10,18,34,0.92));border:2px solid {acc};border-radius:42px;padding:26px 24px;box-shadow:0 0 40px rgba(37,216,255,0.16);">
        <div style="width:148px;height:8px;border-radius:999px;background:rgba(255,255,255,0.14);margin:4px auto 24px;"></div>
        <div style="font-size:22px;letter-spacing:0.16em;color:{acc};margin-bottom:12px;">RETRIEVAL DASHBOARD</div>
        <div style="font-size:42px;font-weight:800;color:#fff;margin-bottom:22px;">需要时直接拿到素材包</div>
        {metrics_html}
        <div style="margin-top:18px;padding:18px;border-radius:18px;background:rgba(255,255,255,0.05);">
            <div style="font-size:22px;color:rgba(255,255,255,0.62);margin-bottom:10px;">输出状态</div>
            <div style="font-size:30px;font-weight:700;color:#2ED573;">结构、观点、例子同时在线</div>
        </div>
    </div>
    """


def _render_parallel_lanes_layout(scene: dict[str, Any], acc: str) -> str:
    lanes = scene.get("parallel_lanes", [
        {"label": "旧路径", "color": "#FF4757", "steps": ["翻找素材", "手动拼接", "从零开写"]},
        {"label": "新路径", "color": acc, "steps": ["提问", "检索笔记", "拿到草稿"]},
    ])
    parts = []
    for idx, lane in enumerate(lanes):
        y = 520 + idx * 290
        chips = "".join(
            f"<div class='compare-item' style='display:inline-flex;align-items:center;padding:14px 18px;border-radius:999px;background:rgba(255,255,255,0.05);font-size:26px;color:#fff;margin-right:14px;'>{step}</div>"
            for step in lane.get("steps", [])
        )
        parts.append(f"""
        <div style="position:absolute;top:{y}px;left:92px;right:92px;">
            <div style="display:flex;align-items:center;gap:18px;margin-bottom:18px;">
                <div style="font-size:22px;letter-spacing:0.16em;color:{lane.get('color', acc)};">{lane.get('label', '')}</div>
                <div class="tool-connector" style="flex:1;height:2px;background:linear-gradient(90deg,{lane.get('color', acc)},transparent);"></div>
            </div>
            <div>{chips}</div>
        </div>
        """)
    parts.append(f"""
    <div style="position:absolute;top:1120px;left:118px;right:118px;padding:20px 24px;background:rgba(255,255,255,0.05);border:1px solid rgba(255,255,255,0.14);border-radius:18px;text-align:center;font-size:28px;color:rgba(255,255,255,0.72);">旧流程在找，新的流程在直接调用。</div>
    """)
    return "".join(parts)


def _render_symptom_panel_layout(scene: dict[str, Any], acc: str) -> str:
    left = scene.get("left_panel", {"label": "交给第二大脑", "title": "记忆负担下降", "items": ["不用强记细节", "素材随时能回查"]})
    right = scene.get("right_panel", {"label": "留给自己", "title": "创造空间上升", "items": ["注意力回到判断", "把精力放在表达"]})
    summary = scene.get("summary_badge", "记忆外包，不等于放弃思考；而是把大脑还给创造。")
    sections = []
    for panel, x, color in ((left, 88, acc), (right, 548, "#2ED573")):
        bullets = "".join(
            f"<div class='compare-item' style='margin-bottom:16px;padding:16px 18px;background:rgba(255,255,255,0.05);border-radius:14px;font-size:27px;color:#fff;'>{item}</div>"
            for item in panel.get("items", [])
        )
        sections.append(f"""
        <div class="compare-item" style="position:absolute;top:470px;left:{x}px;width:444px;background:rgba(255,255,255,0.06);border:2px solid {color};border-radius:24px;padding:26px 22px;">
            <div style="font-size:22px;letter-spacing:0.16em;color:{color};margin-bottom:10px;">{panel.get('label', '')}</div>
            <div style="font-size:40px;font-weight:800;color:#fff;margin-bottom:18px;">{panel.get('title', '')}</div>
            {bullets}
        </div>
        """)
    return f"""
    {''.join(sections)}
    <div style="position:absolute;top:1080px;left:140px;right:140px;padding:22px 24px;border-radius:18px;background:rgba(37,216,255,0.08);border:1px solid rgba(37,216,255,0.28);text-align:center;font-size:30px;color:#fff;line-height:1.45;">{summary}</div>
    """


# ─────────────────────────────────────────────────────────────────
# TEMPLATE 6 — checklist_cta
# Variants: checklist_steps (default), button_banner, end_score_goodbye, scorecard
# ─────────────────────────────────────────────────────────────────

def _template_checklist_cta(sid: str, role: str, scene: dict[str, Any]) -> str:
    acc = _accent(role)
    layout_variant = scene.get("layout_variant", "checklist_steps")
    if layout_variant == "button_banner":
        return _render_cta_button_banner(sid, role, scene, acc)
    if layout_variant == "end_score_goodbye":
        return _render_cta_end_score_goodbye(sid, role, scene, acc)
    if layout_variant == "scorecard":
        return _render_cta_scorecard(sid, role, scene, acc)
    return _render_cta_checklist_steps(sid, role, scene, acc)


def _render_cta_checklist_steps(sid: str, role: str, scene: dict[str, Any], acc: str) -> str:
    items = scene.get("checklist", [
        "找最近 10 条素材",
        "放到同一个入口",
        "给它们一个输出方向",
    ])
    final_msg = scene.get("final_message", "先用起来，比继续收藏更重要")

    item_htmls = []
    for i, item in enumerate(items):
        num = i + 1
        item_htmls.append(f"""
        <div class="check-item" style="
            margin-bottom:28px;padding:24px 32px;
            background:rgba(255,255,255,0.05);border:1px solid rgba(255,255,255,0.12);
            border-radius:16px;display:flex;align-items:center;gap:20px;
        ">
            <div style="
                width:56px;height:56px;background:{acc};border-radius:50%;
                display:flex;align-items:center;justify-content:center;
                font-size:32px;font-weight:800;color:#fff;flex-shrink:0;
            ">{num}</div>
            <span style="font-size:36px;font-weight:600;color:#fff;">{item}</span>
        </div>
        """)

    items_html = "\n".join(item_htmls)
    final_html = f"""
    <div style="
        position:absolute;bottom:180px;left:72px;right:72px;text-align:center;
        padding:24px;background:rgba(46,213,115,0.1);border:1px solid #2ED573;
        border-radius:16px;
    ">
        <span style="font-size:34px;font-weight:600;color:#2ED573;">{final_msg}</span>
    </div>
    """
    headline = scene.get("headline", "今天你先做一件事")
    headline_html = f"""
    <div style="position:absolute;top:200px;left:72px;right:72px;text-align:center;">
        <div style="font-size:52px;font-weight:700;color:#fff;margin-bottom:8px;">{headline}</div>
    </div>
    """
    return f"""
    <div data-motion-target="scene-bg" style="position:absolute;inset:0;background:{_bg(role)};">
      <div class="bg-grid"></div>
    </div>
    {headline_html}
    <div style="position:absolute;top:340px;left:120px;right:120px;">{items_html}</div>
    {final_html}
    <div class="scene-label" style="position:absolute;top:24px;left:24px;font-size:14px;color:{acc};opacity:0.7;">{sid} · {role}</div>
"""


def _css_checklist_cta(sid: str, role: str, scene: dict[str, Any]) -> str:
    acc = _accent(role)
    return f"""
.{sid.lower()}-check-item {{ transition: transform 0.2s ease; }}
.{sid.lower()}-check-item:hover {{ transform: translateX(12px); }}
.{sid.lower()}-bg-grid {{ position:absolute; inset:0; pointer-events:none; background-image:linear-gradient({acc}06 1px,transparent 1px),linear-gradient(90deg,{acc}06 1px,transparent 1px); background-size:72px 72px; animation:grid-drift 18s linear infinite; }}
@keyframes grid-drift {{ 0%{{background-position:0 0;}} 100%{{background-position:72px 72px;}} }}
"""


def _gsap_checklist_cta(sid: str, role: str, scene: dict[str, Any], start: float, duration: float) -> str:
    layout_variant = scene.get("layout_variant", "checklist_steps")
    if layout_variant == "button_banner":
        return _gsap_cta_button_banner(sid, scene)
    if layout_variant == "end_score_goodbye":
        return _gsap_cta_end_score_goodbye(sid, scene)
    if layout_variant == "scorecard":
        return _gsap_cta_scorecard(sid, scene)
    return f"""
const tl_{sid}=gsap.timeline({{paused:true}});
window.__timelines['{sid}']=tl_{sid};
tl_{sid}.fromTo('[data-scene-id="{sid}"] .check-item',{{y:40,opacity:0}},{{y:0,opacity:1,duration:0.5,ease:'power2.out'}},0);
tl_{sid}.fromTo('[data-scene-id="{sid}"] .bg-grid',{{opacity:0}},{{opacity:1,duration:1.0}},0);
"""


# ─────────────────────────────────────────────────────────────────
# CTA Variants — button_banner / end_score_goodbye / scorecard
# Reusing HUD glass card / scanline / accent palette from prior templates.
# ─────────────────────────────────────────────────────────────────

def _render_cta_button_banner(sid: str, role: str, scene: dict[str, Any], acc: str) -> str:
    """Single hero button + supporting line — strong action emphasis."""
    headline = scene.get("headline", scene.get("narration", "现在就开始")[:30] or "现在就开始")
    button_label = scene.get("button_label", "立即开始")
    subline = scene.get("final_message", scene.get("subline", "把收藏变成第一次真正的输出"))
    hint = scene.get("hint", "滑动看完 → 马上动手")
    return f"""
    <div data-motion-target="scene-bg" style="position:absolute;inset:0;background:linear-gradient(180deg,#082016 0%,#0A2818 60%,#0F3A24 100%);">
      <div class="bg-grid"></div>
      <div class="bg-glow bg-glow-1" style="background:radial-gradient(circle,{acc}22 0%,transparent 68%);"></div>
    </div>
    <div style="position:absolute;top:280px;left:72px;right:72px;text-align:center;">
      <div style="display:inline-flex;padding:10px 22px;border-radius:999px;background:rgba(255,255,255,0.06);border:1px solid {acc}66;color:{acc};font-size:20px;letter-spacing:0.2em;margin-bottom:22px;">ACTION / CTA</div>
      <div style="font-size:64px;font-weight:900;color:#fff;line-height:1.1;letter-spacing:-1.4px;">{headline}</div>
    </div>
    <div style="position:absolute;top:760px;left:120px;right:120px;padding:38px 30px;border-radius:36px;background:linear-gradient(135deg,{acc} 0%,#2ED573 100%);box-shadow:0 0 64px {acc}66;text-align:center;">
      <div style="font-size:18px;letter-spacing:0.22em;color:rgba(0,0,0,0.7);margin-bottom:6px;">STEP 01</div>
      <div style="font-size:58px;font-weight:900;color:#0A2818;letter-spacing:-0.6px;">▶  {button_label}</div>
    </div>
    <div style="position:absolute;top:980px;left:120px;right:120px;padding:20px 26px;border:1px solid rgba(255,255,255,0.16);border-radius:22px;background:rgba(255,255,255,0.04);text-align:center;font-size:28px;color:rgba(255,255,255,0.78);line-height:1.4;">{subline}</div>
    <div style="position:absolute;top:1130px;left:0;right:0;text-align:center;font-size:18px;letter-spacing:0.32em;color:rgba(255,255,255,0.42);">{hint}</div>
    <div class="scene-label" style="position:absolute;top:24px;left:24px;font-size:14px;color:{acc};opacity:0.7;">{sid} · {role}</div>
"""


def _render_cta_end_score_goodbye(sid: str, role: str, scene: dict[str, Any], acc: str) -> str:
    """Big score number + chapter close — series finale feel."""
    score = scene.get("score", scene.get("score_value", "100"))
    score_label = scene.get("score_label", "本章掌握度")
    headline = scene.get("headline", scene.get("narration", "这一章就到这里")[:30] or "这一章就到这里")
    next_teaser = scene.get("next_teaser", "下期讲：把检索真正接进 AI 流程")
    final_msg = scene.get("final_message", "先把这一章跑通，再来下期")
    return f"""
    <div data-motion-target="scene-bg" style="position:absolute;inset:0;background:linear-gradient(160deg,#0A1428 0%,#0A1A28 55%,#0F2A1A 100%);">
      <div class="bg-grid"></div>
      <div class="bg-glow bg-glow-1" style="background:radial-gradient(circle,#2ED57328 0%,transparent 70%);"></div>
      <div class="bg-glow bg-glow-2" style="background:radial-gradient(circle,{acc}18 0%,transparent 72%);"></div>
    </div>
    <div style="position:absolute;top:140px;left:0;right:0;text-align:center;">
      <div style="font-size:22px;letter-spacing:0.32em;color:rgba(255,255,255,0.5);">CHAPTER CLOSE</div>
      <div style="font-size:20px;letter-spacing:0.2em;color:{acc};margin-top:12px;">{score_label}</div>
    </div>
    <div style="position:absolute;top:230px;left:0;right:0;text-align:center;">
      <div style="font-size:280px;font-weight:900;line-height:0.9;color:{acc};text-shadow:0 0 64px {acc}80;letter-spacing:-6px;">{score}</div>
      <div style="font-size:36px;font-weight:700;color:rgba(255,255,255,0.78);margin-top:8px;letter-spacing:0.08em;">/ 100</div>
    </div>
    <div style="position:absolute;top:680px;left:72px;right:72px;padding:24px 26px;border:1px solid rgba(255,255,255,0.16);border-radius:24px;background:rgba(255,255,255,0.05);text-align:center;">
      <div style="font-size:42px;font-weight:800;color:#fff;line-height:1.2;">{headline}</div>
    </div>
    <div style="position:absolute;top:880px;left:0;right:0;text-align:center;">
      <div style="font-size:18px;letter-spacing:0.32em;color:{acc};margin-bottom:14px;">NEXT / PREVIEW</div>
      <div style="display:inline-flex;padding:16px 32px;border-radius:18px;background:rgba(46,213,115,0.12);border:1px solid {acc}66;font-size:30px;color:#fff;font-weight:600;">{next_teaser}</div>
    </div>
    <div style="position:absolute;top:1130px;left:140px;right:140px;padding:18px 22px;border-radius:18px;background:rgba(255,255,255,0.04);text-align:center;font-size:26px;color:rgba(255,255,255,0.68);line-height:1.4;">{final_msg}</div>
    <div class="scene-label" style="position:absolute;top:24px;left:24px;font-size:14px;color:{acc};opacity:0.7;">{sid} · {role}</div>
"""


def _render_cta_scorecard(sid: str, role: str, scene: dict[str, Any], acc: str) -> str:
    """Result-style scorecard — multiple metrics, before/after feel."""
    headline = scene.get("headline", scene.get("narration", "你这一轮的得分")[:30] or "你这一轮的得分")
    metrics = scene.get("scorecard_metrics", [
        {"label": "启动", "value": "READY", "color": "#2ED573"},
        {"label": "闭环", "value": "OK", "color": "#4D9FFF"},
        {"label": "下一步", "value": "GO", "color": "#FF6B35"},
    ])
    final_msg = scene.get("final_message", "三项都达到 GO，你就可以进入下一章")
    metrics_html = "".join(
        f"""
        <div class="cta-metric" style="position:absolute;top:{340 + idx * 220}px;left:72px;right:72px;padding:24px 28px;background:rgba(255,255,255,0.05);border:2px solid {metric.get('color', acc)};border-radius:24px;display:flex;align-items:center;gap:22px;box-shadow:0 0 28px {metric.get('color', acc)}22;">
            <div style="width:80px;height:80px;border-radius:50%;background:{metric.get('color', acc)};display:flex;align-items:center;justify-content:center;font-size:40px;font-weight:900;color:#0A1428;flex-shrink:0;">{idx+1}</div>
            <div style="flex:1;">
                <div style="font-size:22px;letter-spacing:0.18em;color:rgba(255,255,255,0.55);margin-bottom:6px;">{metric.get('label', '')}</div>
                <div style="font-size:46px;font-weight:900;color:{metric.get('color', acc)};letter-spacing:-0.5px;">{metric.get('value', '')}</div>
            </div>
        </div>
        """
        for idx, metric in enumerate(metrics)
    )
    return f"""
    <div data-motion-target="scene-bg" style="position:absolute;inset:0;background:linear-gradient(180deg,#0A1428 0%,#0A1A28 60%,#082016 100%);">
      <div class="bg-grid"></div>
    </div>
    <div style="position:absolute;top:170px;left:72px;right:72px;text-align:center;">
      <div style="display:inline-flex;padding:8px 20px;border-radius:999px;background:rgba(46,213,115,0.12);border:1px solid {acc}66;color:{acc};font-size:18px;letter-spacing:0.22em;margin-bottom:18px;">SCORECARD</div>
      <div style="font-size:54px;font-weight:900;color:#fff;line-height:1.12;letter-spacing:-1.2px;">{headline}</div>
    </div>
    {metrics_html}
    <div style="position:absolute;top:1090px;left:90px;right:90px;padding:22px 26px;border:1px solid rgba(255,255,255,0.16);border-radius:22px;background:rgba(46,213,115,0.08);text-align:center;font-size:28px;color:rgba(255,255,255,0.82);line-height:1.4;">{final_msg}</div>
    <div class="scene-label" style="position:absolute;top:24px;left:24px;font-size:14px;color:{acc};opacity:0.7;">{sid} · {role}</div>
"""


def _gsap_cta_button_banner(sid: str, scene: dict[str, Any]) -> str:
    return f"""
const tl_{sid}=gsap.timeline({{paused:true}});
window.__timelines['{sid}']=tl_{sid};
tl_{sid}.fromTo('[data-scene-id="{sid}"] [data-motion-target="scene-bg"] .bg-grid',{{opacity:0}},{{opacity:1,duration:0.8}},0);
tl_{sid}.fromTo('[data-scene-id="{sid}"] [data-motion-target="scene-bg"] .bg-glow-1',{{scale:0.7,opacity:0}},{{scale:1,opacity:1,duration:1.0,ease:'power2.out'}},0.1);
"""


def _gsap_cta_end_score_goodbye(sid: str, scene: dict[str, Any]) -> str:
    return f"""
const tl_{sid}=gsap.timeline({{paused:true}});
window.__timelines['{sid}']=tl_{sid};
tl_{sid}.fromTo('[data-scene-id="{sid}"] [data-motion-target="scene-bg"] .bg-grid',{{opacity:0}},{{opacity:1,duration:0.8}},0);
tl_{sid}.fromTo('[data-scene-id="{sid}"] [data-motion-target="scene-bg"] .bg-glow-1',{{scale:0.7,opacity:0}},{{scale:1,opacity:1,duration:1.0,ease:'power2.out'}},0.1);
"""


def _gsap_cta_scorecard(sid: str, scene: dict[str, Any]) -> str:
    return f"""
const tl_{sid}=gsap.timeline({{paused:true}});
window.__timelines['{sid}']=tl_{sid};
tl_{sid}.fromTo('[data-scene-id="{sid}"] [data-motion-target="scene-bg"] .bg-grid',{{opacity:0}},{{opacity:1,duration:0.8}},0);
tl_{sid}.fromTo('[data-scene-id="{sid}"] .cta-metric',{{x:-60,opacity:0}},{{x:0,opacity:1,duration:0.6,stagger:0.2,ease:'back.out(1.2)'}},0.2);
"""


# ─────────────────────────────────────────────────────────────────
# FALLBACK — old role-based template (default)
# ─────────────────────────────────────────────────────────────────

def _template_fallback(sid: str, role: str, scene: dict[str, Any]) -> str:
    """Fallback to old role-based template for backwards compat."""
    acc = _accent(role)
    narration = scene.get("narration", "")
    headline = narration[:30] if narration else f"Scene {sid}"
    return f"""
    <div data-motion-target="scene-bg" style="position:absolute;inset:0;background:{_bg(role)};">
      <div class="bg-grid"></div>
      <div class="bg-glow bg-glow-1" style="background:radial-gradient(circle,{acc}22 0%,transparent 70%);"></div>
      <div class="bg-glow bg-glow-2" style="background:radial-gradient(circle,{acc}18 0%,transparent 70%);"></div>
    </div>
    <div data-motion-target="headline" class="headline-container" style="position:absolute;top:280px;left:72px;right:72px;">
      <div class="title" style="font-size:64px;font-weight:700;color:#fff;line-height:1.15;">{headline}</div>
    </div>
    <div data-motion-target="metric-panel" class="metric-panel" style="position:absolute;top:500px;left:72px;right:72px;display:flex;flex-direction:column;gap:16px;">
      <div class="metric-card" style="background:rgba(37,216,255,0.08);border:1px solid rgba(37,216,255,0.25);border-radius:16px;padding:20px 24px;">
        <b style="font-size:48px;font-weight:800;color:{acc};">40%</b>
        <span style="font-size:22px;color:rgba(255,255,255,0.75);display:block;margin-top:8px;">效率提升</span>
      </div>
    </div>
    <div class="scene-label" style="position:absolute;top:24px;left:24px;font-size:14px;color:{acc};opacity:0.7;">{sid} · {role}</div>
"""


def _css_fallback(sid: str, role: str, scene: dict[str, Any]) -> str:
    acc = _accent(role)
    return f"""
.{sid.lower()}-hook-container {{ position:absolute; top:200px; left:72px; right:72px; }}
.{sid.lower()}-headline {{ font-size:74px; font-weight:700; color:#fff; line-height:1.1; text-shadow:0 4px 20px rgba(0,0,0,0.5); }}
.{sid.lower()}-metric-card {{ background:rgba({acc.replace('#','')},0.08); border:1px solid rgba({acc.replace('#','')},0.25); border-radius:16px; padding:20px 24px; }}
.{sid.lower()}-metric-card b {{ font-size:48px; font-weight:800; color:{acc}; line-height:1; }}
.{sid.lower()}-bg-grid {{ position:absolute; inset:0; pointer-events:none; background-image:linear-gradient({acc}08 1px,transparent 1px),linear-gradient(90deg,{acc}08 1px,transparent 1px); background-size:72px 72px; animation:grid-drift 18s linear infinite; }}
@keyframes grid-drift {{ 0%{{background-position:0 0;}} 100%{{background-position:72px 72px;}} }}
.{sid.lower()}-bg-glow {{ position:absolute; width:420px; height:420px; border-radius:50%; animation:glow-pulse 3.5s ease-in-out infinite; pointer-events:none; }}
.{sid.lower()}-bg-glow-1 {{ top:-120px; left:-80px; animation-delay:0s; }}
.{sid.lower()}-bg-glow-2 {{ bottom:-140px; right:-60px; animation-delay:1.8s; }}
@keyframes glow-pulse {{ 0%,100%{{opacity:0.5;transform:scale(1);}} 50%{{opacity:0.8;transform:scale(1.15);}} }}
"""


def _gsap_fallback(sid: str, role: str, scene: dict[str, Any], start: float, duration: float) -> str:
    return f"""
const tl_{sid}=gsap.timeline({{paused:true}});
window.__timelines['{sid}']=tl_{sid};
tl_{sid}.fromTo('[data-scene-id="{sid}"] .headline',{{y:60,opacity:0}},{{y:0,opacity:1,duration:0.8,ease:'power3.out'}},0);
tl_{sid}.fromTo('[data-scene-id="{sid}"] .metric-card',{{y:40,opacity:0}},{{y:0,opacity:1,duration:0.6,ease:'power2.out'}},0.3);
tl_{sid}.fromTo('[data-scene-id="{sid}"] .bg-grid',{{opacity:0}},{{opacity:1,duration:1.0}},0);
"""


# ─────────────────────────────────────────────────────────────────
# TEMPLATE REGISTRY
# ─────────────────────────────────────────────────────────────────

_TEMPLATES = {
    "hook_big_claim": _template_hook_big_claim,
    "pain_card_stack": _template_pain_card_stack,
    "broken_chain": _template_broken_chain,
    "tool_chain_three_cols": _template_tool_chain_three_cols,
    "before_after_compare": _template_before_after_compare,
    "checklist_cta": _template_checklist_cta,
    # fallback aliases
    "hook_centered": _template_fallback,
    "pain_centered": _template_fallback,
    "method_centered": _template_fallback,
    "evidence_centered": _template_fallback,
    "proof_centered": _template_fallback,
    "cta_centered": _template_fallback,
}

_CSS_FUNCTIONS = {
    "hook_big_claim": _css_hook_big_claim,
    "pain_card_stack": _css_pain_card_stack,
    "broken_chain": _css_broken_chain,
    "tool_chain_three_cols": _css_tool_chain_three_cols,
    "before_after_compare": _css_before_after_compare,
    "checklist_cta": _css_checklist_cta,
    "hook_centered": _css_fallback,
    "pain_centered": _css_fallback,
    "method_centered": _css_fallback,
    "evidence_centered": _css_fallback,
    "proof_centered": _css_fallback,
    "cta_centered": _css_fallback,
}

_GSAP_FUNCTIONS = {
    "hook_big_claim": _gsap_hook_big_claim,
    "pain_card_stack": _gsap_pain_card_stack,
    "broken_chain": _gsap_broken_chain,
    "tool_chain_three_cols": _gsap_tool_chain_three_cols,
    "before_after_compare": _gsap_before_after_compare,
    "checklist_cta": _gsap_checklist_cta,
    "hook_centered": _gsap_fallback,
    "pain_centered": _gsap_fallback,
    "method_centered": _gsap_fallback,
    "evidence_centered": _gsap_fallback,
    "proof_centered": _gsap_fallback,
    "cta_centered": _gsap_fallback,
}
