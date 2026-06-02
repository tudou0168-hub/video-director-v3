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
    headline = scene.get("headline", narration[:40] if narration else "你有没有发现，收藏越多，反而越写不出来？")
    sub = scene.get("subheadline", "")

    # V3-P3.11A — Remove 3-line hard split. Use natural CSS wrapping instead.
    cyan = "#38E1FF"
    amber = "#FFC83D"
    import html as _html
    def _highlight(s: str) -> str:
        s = _html.escape(s)
        s = s.replace("Claude Code", '<span class="accent-cyan">Claude Code</span>')
        s = s.replace("三个月后", '<span class="accent">三个月后</span>')
        return s

    safe_headline = _highlight(headline)

    sub_html = ""
    if sub:
        sub_html = f"<div class='hf-sub-title hf-animate-title' style='margin-top:32px;line-height:1.4;max-width:920px;font-size:30px;color:rgba(248,250,252,0.82);'>{sub}</div>"

    if layout_variant == "quote_punch":
        return _render_hook_quote_punch(sid, role, safe_headline, sub, acc)
    if layout_variant == "big_number_left":
        return _render_hook_big_number_left(sid, role, safe_headline, sub, acc)

    # Subtitle bar (Chinese) — "真实效率变化"
    subtitle_bar = (
        '<div class="hf-animate-stamp" style="position:absolute;top:-110px;left:0;'
        'display:inline-flex;align-items:center;gap:14px;'
        'padding:14px 24px;border-radius:14px;background:rgba(56,225,255,0.18);'
        f'border:1.5px solid {cyan};box-shadow:0 0 18px rgba(56,225,255,0.4);">'
        '<span style="font:800 18px/1 &quot;SF Mono&quot;,monospace;letter-spacing:.22em;'
        f'color:{cyan};text-transform:uppercase;">REAL EFFICIENCY SHIFT</span>'
        '<span style="font-size:24px;font-weight:700;color:#FFFFFF;'
        'letter-spacing:.04em;">真实效率变化</span></div>'
    )

    # Right-side HUD stamp cluster
    right_stamps = (
        '<div style="position:absolute;top:-110px;right:0;display:flex;gap:10px;flex-direction:column;align-items:flex-end;">'
        f'<div class="hf-status-stamp hf-status-live hf-animate-stamp" style="font-size:16px;padding:10px 18px;color:{cyan};border-width:2px;">AGENT / 12 SEC</div>'
        f'<div class="hf-status-stamp hf-status-viral hf-animate-stamp" style="font-size:16px;padding:10px 18px;color:{amber};border-width:2px;">+12 HRS / WEEK</div>'
        f'<div class="hf-status-stamp hf-status-pass hf-animate-stamp" style="font-size:16px;padding:10px 18px;color:#2EE874;border-width:2px;">3 STAGES</div>'
        '</div>'
    )

    return f"""
    <div data-motion-target="scene-bg" class="hf-bg-cinematic" style="position:absolute;inset:0;background:{_bg(role)};">
      <div class="bg-grid" style="opacity:.25"></div>
      <div class="bg-glow bg-glow-1" style="background:radial-gradient(circle,rgba(56,225,255,0.28) 0%,transparent 70%);"></div>
      <div class="bg-glow bg-glow-2" style="background:radial-gradient(circle,rgba(255,200,61,0.18) 0%,transparent 70%);"></div>
    </div>
    <div data-motion-target="hook-main" class="hook-main hf-safe-zone" style="position:absolute;top:500px;left:60px;right:60px;text-align:left;">
      {subtitle_bar}
      {right_stamps}
      <h1 class="hf-big-title hf-animate-title" style="margin:0;line-height:1.06;max-width:960px;font-size:clamp(56px,8vw,76px);word-break:keep-all;overflow-wrap:break-word;">{safe_headline}</h1>
      {sub_html}
    </div>
    <!-- V3-P3.11C — bottom anchor: accent bar + tagline for poster-like visual weight -->
    <div style="position:absolute;bottom:360px;left:50%;transform:translateX(-50%);text-align:center;">
      <div style="width:160px;height:4px;margin:0 auto 20px;background:linear-gradient(90deg,{cyan},transparent);border-radius:2px;box-shadow:0 0 12px rgba(56,225,255,0.4);"></div>
      <div style="font-size:24px;font-weight:600;color:rgba(255,255,255,0.38);letter-spacing:.06em;">· AI·Obsidian 第二大脑 ·</div>
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
    <!-- V3-P3.11B — shifted from top:160px to top:350px for better vertical balance -->
    <div style="position:absolute;top:350px;left:72px;right:72px;">
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
        <div class="pain-card hf-animate-card" id="{sid.lower()}-card-{i}" style="
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
        <div class="hf-animate-title hf-safe-zone" style="font-size:52px;font-weight:700;color:#fff;line-height:1.2;">{headline}</div>
    </div>
    """
    layout_html = _render_broken_chain_layout(scene, acc, layout_variant)
    return f"""
    <div data-motion-target="scene-bg" class="hf-bg-cinematic" style="position:absolute;inset:0;background:{_bg(role)};">
      <div class="bg-grid" style="opacity:.25"></div>
      <div class="bg-glow bg-glow-1" style="background:radial-gradient(circle,{acc}28 0%,transparent 70%);"></div>
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
    if layout_variant == "vertical_flow":
        return _render_chain_vertical_flow_layout(scene, acc)
    if layout_variant == "knowledge_triangle":
        return _render_chain_knowledge_triangle_layout(scene, acc)
    return _render_chain_flow_layout(scene, acc)


def _render_chain_vertical_flow_layout(scene: dict[str, Any], acc: str) -> str:
    """V3-P3.8: column-stacked nodes with a left-side accent rail.

    Used as a fresh visual grammar for `broken_chain` scenes so the
    2026-05-26 horizontal-row repetition doesn't recur. Reuses the
    existing chain_nodes / broken_slots data.
    """
    nodes = scene.get("chain_nodes", ["输入", "整理", "回顾", "输出"])
    broken_slots = scene.get("broken_slots", [1, 2, 3])
    node_htmls = []
    rail_segments = []
    node_h = 110
    gap = 28
    start_y = 480
    rail_x = 168
    for i, node in enumerate(nodes):
        y = start_y + i * (node_h + gap)
        node_color = "#FF4757" if i in broken_slots else acc
        # V3-P3.11D — hf-glass-panel on chain nodes
        glass_class = "hf-glass-red" if i in broken_slots else "hf-glass-cyan"
        node_htmls.append(f"""
        <div class="chain-node hf-glass-panel {glass_class} hf-animate-card" style="
            position:absolute;top:{y}px;left:{rail_x + 40}px;width:760px;height:{node_h}px;
            display:flex;align-items:center;padding:0 36px;font-size:34px;font-weight:700;color:#fff;
            background:rgba(2,4,12,0.6);border-color:{node_color};
        ">{node}</div>
        """)
        # Rail segment between consecutive nodes.
        if i < len(nodes) - 1:
            seg_y = y + node_h
            seg_h = gap
            rail_segments.append(f"""
            <div class="tool-connector" style="
                position:absolute;top:{seg_y}px;left:{rail_x + 60}px;width:6px;height:{seg_h}px;
                background:linear-gradient(180deg,{acc},rgba(37,216,255,0.2));
                border-radius:4px;
            "></div>
            """)
    rail_html = f"""
    <div style="position:absolute;top:{start_y}px;left:{rail_x}px;width:6px;height:{len(nodes) * (node_h + gap) - gap}px;background:linear-gradient(180deg,{acc},rgba(37,216,255,0.25));border-radius:4px;box-shadow:0 0 18px {acc}66;"></div>
    """
    return rail_html + "\n".join(node_htmls) + "\n" + "\n".join(rail_segments)


def _render_chain_knowledge_triangle_layout(scene: dict[str, Any], acc: str) -> str:
    """V3-P3.8: 3 nodes arranged in a triangle with 1 detached node and
    a dotted connector. Suggests "the chain has 3 connected + 1 isolated"
    in a more spatial way than the row layout.
    """
    nodes = scene.get("chain_nodes", ["输入", "整理", "检索", "输出"])
    broken_slots = scene.get("broken_slots", [3])
    # 3 connected nodes in a triangle; 4th detached to the right.
    triangle_pts = [
        (270, 720),    # bottom-left
        (540, 480),    # top
        (810, 720),    # bottom-right
    ]
    detached = (920, 1080)
    node_radius = 64
    pieces = []
    for i, (cx, cy) in enumerate(triangle_pts):
        if i < len(nodes):
            label = nodes[i]
        else:
            label = ""
        node_color = "#FF4757" if i in broken_slots else acc
        glass_class = "hf-glass-red" if i in broken_slots else "hf-glass-cyan"
        pieces.append(f"""
        <div class="chain-node hf-glass-panel {glass_class} hf-animate-card" style="
            position:absolute;top:{cy - node_radius}px;left:{cx - node_radius}px;
            width:{node_radius * 2}px;height:{node_radius * 2}px;border-radius:50%;
            display:flex;align-items:center;justify-content:center;
            font-size:28px;font-weight:800;color:#fff;
            background:rgba(2,4,12,0.6);border-color:{node_color};
            box-shadow:0 0 26px {node_color}55;
        ">{label}</div>
        """)
    # Triangle edges.
    for a, b in ((0, 1), (1, 2), (0, 2)):
        ax, ay = triangle_pts[a]
        bx, by = triangle_pts[b]
        # Use a simple line via SVG-like div with rotation.
        import math
        dx, dy = bx - ax, by - ay
        length = math.hypot(dx, dy)
        angle = math.degrees(math.atan2(dy, dx))
        midx, midy = (ax + bx) / 2, (ay + by) / 2
        edge_color = "#FF4757" if (a in broken_slots or b in broken_slots) else acc
        pieces.append(f"""
        <div class="tool-connector" style="
            position:absolute;top:{midy - 2}px;left:{midx - length / 2}px;
            width:{length}px;height:3px;
            background:linear-gradient(90deg,{edge_color},rgba(37,216,255,0.2));
            transform:rotate({angle}deg);transform-origin:center;
            box-shadow:0 0 12px {edge_color}55;
        "></div>
        """)
    # Detached node + dotted connector.
    if len(nodes) >= 4:
        cx, cy = detached
        detached_color = "#FF4757" if 3 in broken_slots else acc
        detached_glass = "hf-glass-red" if 3 in broken_slots else "hf-glass-cyan"
        pieces.append(f"""
        <div class="chain-node hf-glass-panel {detached_glass} hf-animate-card" style="
            position:absolute;top:{cy - node_radius}px;left:{cx - node_radius}px;
            width:{node_radius * 2}px;height:{node_radius * 2}px;border-radius:50%;
            display:flex;align-items:center;justify-content:center;
            font-size:28px;font-weight:800;color:#fff;opacity:0.85;
            background:rgba(2,4,12,0.5);border-color:{detached_color};
            border-style:dashed;
        ">{nodes[3]}</div>
        """)
        # Dotted connector from triangle-right to detached.
        pieces.append(f"""
        <div class="tool-connector" style="
            position:absolute;top:720px;left:880px;width:80px;height:0;
            border-top:3px dotted {acc};
        "></div>
        """)
    return "\n".join(pieces)


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
        <div class="chain-node hf-animate-card" style="
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
        <div class="chain-node hf-animate-card" style="
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
    <div class="chain-node hf-animate-card" style="position:absolute;top:390px;left:72px;width:444px;height:700px;background:linear-gradient(180deg,rgba(255,71,87,0.14),rgba(255,255,255,0.04));border:2px solid #FF4757;border-radius:32px;padding:30px 26px;box-shadow:0 0 40px rgba(255,71,87,0.16);">
        <div style="font-size:20px;letter-spacing:0.16em;color:#FF4757;margin-bottom:10px;">{left.get('label', '不要')}</div>
        <div style="font-size:44px;font-weight:900;color:#fff;margin-bottom:20px;line-height:1.08;">{left.get('title', '')}</div>
        {left_items}
    </div>
    <div style="position:absolute;top:650px;left:512px;width:56px;height:56px;border-radius:50%;display:flex;align-items:center;justify-content:center;background:rgba(255,255,255,0.06);border:1px solid rgba(255,255,255,0.14);font-size:24px;color:rgba(255,255,255,0.7);">VS</div>
    <div class="chain-node hf-animate-card" style="position:absolute;top:390px;right:72px;width:444px;height:700px;background:linear-gradient(180deg,rgba(46,213,115,0.14),rgba(255,255,255,0.04));border:2px solid {acc};border-radius:32px;padding:30px 26px;box-shadow:0 0 40px rgba(46,213,115,0.12);">
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
    # V3-P3.9 — Step Panel grammar: 3 numbered glass columns with STEP X/3
    # badge top-right; arrows between them; current step (index 0) glows.
    headline_html = f"""
    <div class="hf-safe-zone" style="position:absolute;top:200px;left:96px;right:96px;">
      <div class="hf-status-stamp hf-status-pass hf-animate-stamp" style="display:inline-flex;margin-bottom:14px;">STEP 1/3 · 流程</div>
      <h2 class="hf-animate-title" style="margin:0;font-size:54px;font-weight:900;color:#fff;line-height:1.12;letter-spacing:-1.2px;">{headline}</h2>
    </div>
    """
    cols_html = _render_tool_chain_layout(col_data, acc, layout_variant)
    return f"""
    <div data-motion-target="scene-bg" class="hf-bg-cinematic" style="position:absolute;inset:0;background:{_bg(role)};">
      <div class="bg-grid" style="opacity:.3"></div>
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
    extra_class: str = "",
) -> str:
    # V3-P3.9 — glass panel + big step number
    return f"""
    <div class="tool-col hf-glass-panel hf-animate-card{extra_class}" style="
        position:absolute;top:{y}px;left:{x}px;width:{width}px;
        padding:{padding};text-align:center;
    ">
        <div class="hf-step-number" style="font-size:64px;color:{acc};text-shadow:0 0 18px {acc}66;line-height:1;margin-bottom:8px;">{col.get('icon','')}</div>
        <div style="font-size:32px;font-weight:800;color:#fff;margin-bottom:6px;letter-spacing:.04em;">{col['name']}</div>
        <div style="font-size:22px;font-weight:700;color:{acc};margin-bottom:6px;letter-spacing:.12em;">{col['func']}</div>
        <div style="font-size:20px;color:rgba(255,255,255,0.6);line-height:1.35;">{col['detail']}</div>
    </div>
    """


def _render_three_col_row_layout(col_data: list[dict[str, Any]], acc: str) -> str:
    col_width = 300
    gap = 50
    total_w = 3 * col_width + 2 * gap
    start_x = (1080 - total_w) // 2
    col_y = 540
    parts: list[str] = []
    for i, col in enumerate(col_data):
        x = start_x + i * (col_width + gap)
        # V3-P3.9 — first step glows with hf-pulse
        glow_class = " hf-pulse" if i == 0 else ""
        parts.append(_render_tool_col(col=col, acc=acc, x=x, y=col_y, width=col_width, extra_class=glow_class))
        if i < 2:
            arrow_x = x + col_width
            parts.append(
                f'<div class="tool-connector hf-animate-title" style="position:absolute;top:{col_y + 60}px;left:{arrow_x}px;width:{gap}px;text-align:center;font-size:48px;color:{acc};text-shadow:0 0 12px {acc};">→</div>'
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
    <div data-motion-target="scene-bg" class="hf-bg-cinematic" style="position:absolute;inset:0;background:{_bg(role)};">
      <div class="bg-grid" style="opacity:.25"></div>
      <div class="bg-glow bg-glow-1" style="background:radial-gradient(circle,{acc}28 0%,transparent 70%);"></div>
    </div>
    <div class="hf-safe-zone">{headline_html}</div>
    <div class="hf-safe-zone">{layout_html}</div>
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
        lane_color = lane.get('color', acc)
        # V3-P3.11D — chips now use hf-glass-panel
        chips = "".join(
            f"<div class='compare-item hf-glass-panel hf-animate-card' style='display:inline-flex;align-items:center;padding:14px 20px;font-size:26px;color:#fff;margin-right:14px;background:rgba(2,4,12,0.5);border-color:{lane_color}66;'>{step}</div>"
            for step in lane.get("steps", [])
        )
        parts.append(f"""
        <div class="hf-safe-zone" style="position:absolute;top:{y}px;left:92px;right:92px;">
            <div style="display:flex;align-items:center;gap:18px;margin-bottom:18px;">
                <div style="font-size:22px;letter-spacing:0.16em;color:{lane_color};">{lane.get('label', '')}</div>
                <div class="tool-connector" style="flex:1;height:2px;background:linear-gradient(90deg,{lane_color},transparent);"></div>
            </div>
            <div>{chips}</div>
        </div>
        """)
    # V3-P3.11D — summary badge with glass styling
    parts.append(f"""
    <div class="hf-glass-panel hf-animate-card" style="position:absolute;top:1120px;left:118px;right:118px;padding:20px 24px;text-align:center;border-color:rgba(255,255,255,0.14);background:rgba(56,225,255,0.08);">
        <div style="font-size:28px;color:rgba(255,255,255,0.82);">旧流程在找，新的流程在直接调用。</div>
    </div>
    """)
    return "".join(parts)


def _render_symptom_panel_layout(scene: dict[str, Any], acc: str) -> str:
    left = scene.get("left_panel", {"label": "交给第二大脑", "title": "记忆负担下降", "items": ["不用强记细节", "素材随时能回查"]})
    right = scene.get("right_panel", {"label": "留给自己", "title": "创造空间上升", "items": ["注意力回到判断", "把精力放在表达"]})
    summary = scene.get("summary_badge", "记忆外包，不等于放弃思考；而是把大脑还给创造。")
    red, green = "#FF5577", "#2EE874"
    sections = []
    for panel, x, border_color, glass_tint in (
        (left, 88, red, "rgba(255,85,119,0.08)"),
        (right, 548, green, "rgba(46,232,116,0.08)"),
    ):
        bullets = "".join(
            f"<div class='compare-item' style='margin-bottom:16px;padding:16px 18px;background:rgba(255,255,255,0.05);border-radius:14px;font-size:27px;color:#fff;'>{item}</div>"
            for item in panel.get("items", [])
        )
        # V3-P3.11C — glass-panel styling with color-tinted background
        sections.append(f"""
        <div class="compare-item hf-glass-panel" style="position:absolute;top:470px;left:{x}px;width:444px;border:2px solid {border_color};padding:26px 22px;background:linear-gradient(180deg,{glass_tint},rgba(2,4,12,0.62));">
            <div style="font-size:22px;letter-spacing:0.16em;color:{border_color};margin-bottom:10px;">{panel.get('label', '')}</div>
            <div style="font-size:40px;font-weight:800;color:#fff;margin-bottom:18px;">{panel.get('title', '')}</div>
            {bullets}
        </div>
        """)
    return f"""
    {''.join(sections)}
    <!-- V3-P3.11C — summary badge with glass-style glow -->
    <div class="hf-glass-panel" style="position:absolute;top:1080px;left:140px;right:140px;padding:22px 24px;border-color:rgba(56,225,255,0.5);text-align:center;background:rgba(56,225,255,0.08);">
        <div style="font-size:30px;color:#fff;line-height:1.45;">{summary}</div>
    </div>
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
            margin-bottom:60px;padding:36px 48px;
            background:rgba(255,255,255,0.05);border:1px solid rgba(255,255,255,0.12);
            border-radius:16px;display:flex;align-items:center;gap:20px;
        ">
            <div style="
                width:60px;height:60px;background:{acc};border-radius:50%;
                display:flex;align-items:center;justify-content:center;
                font-size:34px;font-weight:800;color:#fff;flex-shrink:0;
            ">{num}</div>
            <span style="font-size:36px;font-weight:600;color:#fff;">{item}</span>
        </div>
        """)

    items_html = "\n".join(item_htmls)
    # V3-P3.11C — visual divider + "三步闭环" step summary
    step_count = len(items)
    step_label = f"共 {step_count} 步 · 最小闭环"
    step_html = f"""
    <div style="position:absolute;top:760px;left:0;right:0;text-align:center;">
        <div style="display:inline-flex;padding:8px 20px;border-radius:999px;background:rgba(46,213,115,0.1);border:1px solid {acc}66;color:{acc};font-size:18px;letter-spacing:0.16em;">{step_label}</div>
    </div>
    """
    # V3-P3.11B — visual divider between checklist and CTA; CTA moved up from bottom:180px to fill gap
    final_html = f"""
    <div class="hf-divider" style="position:absolute;top:840px;left:120px;right:120px;height:2px;
        background:linear-gradient(90deg,transparent,{acc}66,transparent);
        border-radius:1px;"></div>
    <div style="
        position:absolute;top:900px;left:72px;right:72px;text-align:center;
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
    {step_html}
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
    """V3-P3.9R1 — Final Score Board grammar: GIANT 100 + DONE / COMPLETE
    stamp + bright green glow halo + prominent NEXT PREVIEW bar."""
    score = scene.get("score", scene.get("score_value", "100"))
    score_label = scene.get("score_label", "本章掌握度")
    headline = scene.get("headline", scene.get("narration", "这一章就到这里")[:30] or "这一章就到这里")
    next_teaser = scene.get("next_teaser", "下期讲：把检索真正接进 AI 流程")
    final_msg = scene.get("final_message", "先把这一章跑通，再来下期")
    green, amber = "#2EE874", "#FFC83D"
    return f"""
    <div data-motion-target="scene-bg" class="hf-bg-cinematic" style="position:absolute;inset:0;background:linear-gradient(160deg,#04060C 0%,#0a1a14 55%,#0a1a14 100%);">
      <div class="bg-grid" style="opacity:.2"></div>
      <div class="bg-glow bg-glow-1" style="background:radial-gradient(circle,rgba(46,232,116,0.45) 0%,transparent 65%);"></div>
      <div class="bg-glow bg-glow-2" style="background:radial-gradient(circle,rgba(255,200,61,0.18) 0%,transparent 72%);"></div>
    </div>
    <div class="hf-safe-zone" style="position:absolute;top:180px;left:0;right:0;text-align:center;">
      <div style="display:flex;justify-content:center;gap:14px;margin-bottom:18px;">
        <div class="hf-status-stamp hf-status-pass hf-animate-stamp" style="font-size:18px;padding:10px 22px;border-width:2px;">DONE</div>
        <div class="hf-status-stamp hf-status-viral hf-animate-stamp" style="font-size:18px;padding:10px 22px;border-width:2px;color:{amber};">COMPLETE</div>
      </div>
      <div class="hf-animate-number" style="font-size:380px;font-weight:900;line-height:0.92;color:{green};text-shadow:0 0 72px {green}cc;letter-spacing:-12px;">{score}</div>
      <div style="font:800 48px/1 &quot;SF Mono&quot;,monospace;color:#FFFFFF;margin-top:10px;letter-spacing:.18em;text-shadow:0 0 14px rgba(255,255,255,0.4);">/ 100 · CHAPTER CLOSE</div>
      <div style="font:700 18px/1 &quot;SF Mono&quot;,monospace;letter-spacing:.22em;color:{green};margin-top:14px;text-transform:uppercase;">{score_label}</div>
    </div>
    <div class="hf-glass-panel hf-glass-green hf-pulse" style="position:absolute;top:760px;left:80px;right:80px;padding:36px 40px;min-height:120px;background:linear-gradient(180deg,rgba(46,232,116,0.22),rgba(2,4,12,0.7) 80%);">
      <div style="font-size:48px;font-weight:800;color:#FFFFFF;line-height:1.18;text-align:center;letter-spacing:-.01em;">{headline}</div>
    </div>
    <div style="position:absolute;top:950px;left:0;right:0;text-align:center;">
      <div style="font:800 18px/1 &quot;SF Mono&quot;,monospace;letter-spacing:.32em;color:{green};margin-bottom:14px;">NEXT / PREVIEW</div>
      <div class="hf-animate-stamp" style="display:inline-flex;padding:20px 40px;border-radius:18px;background:rgba(46,232,116,0.22);border:2.5px solid {green};font:800 32px/1 &quot;PingFang SC&quot;,sans-serif;color:#FFFFFF;box-shadow:0 0 32px {green}77;letter-spacing:.04em;">{next_teaser}</div>
    </div>
    <div style="position:absolute;top:1090px;left:140px;right:140px;padding:20px 24px;border-radius:18px;background:rgba(255,255,255,0.06);text-align:center;font-size:26px;color:rgba(248,250,252,0.82);line-height:1.4;letter-spacing:.02em;">{final_msg}</div>
    <!-- V3-P3.11C — END marker with ceremony feel -->
    <div style="position:absolute;bottom:300px;left:50%;transform:translateX(-50%);
        font-size:20px;letter-spacing:.32em;color:rgba(255,255,255,0.35);
        border-top:2px solid rgba(46,232,116,0.30);padding-top:20px;width:180px;text-align:center;
        box-shadow:0 -4px 12px rgba(46,232,116,0.08);">· END ·</div>
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
# P3.3 — 6 new seed template renderers
# framework_quadrant / decision_tree / metric_dashboard /
# case_study_card / section_board / comment_question
# All reuse existing HUD card / scanline / accent palette.
# ─────────────────────────────────────────────────────────────────

def _template_framework_quadrant(sid: str, role: str, scene: dict[str, Any]) -> str:
    acc = _accent(role)
    headline = scene.get("headline", scene.get("narration", "知识管理四象限")[:30] or "知识管理四象限")
    quadrants = scene.get("quadrants", [
        {"label": "Q1 收集", "text": "微信 / 网页 / 语音", "color": "#4D9FFF"},
        {"label": "Q2 整理", "text": "双向链接 / 主题页", "color": "#2ED573"},
        {"label": "Q3 检索", "text": "直接问 AI", "color": "#FF6B35"},
        {"label": "Q4 输出", "text": "写作 / 复盘", "color": "#A855F7"},
    ])
    center_label = scene.get("center_label", scene.get("quadrant_center", "Obsidian"))
    positions = [("top:480px;left:120px;", "Q1"), ("top:480px;right:120px;", "Q2"),
                 ("top:980px;left:120px;", "Q3"), ("top:980px;right:120px;", "Q4")]
    # V3-P3.9 — Knowledge Overlay grammar: 2x2 glass panels with CENTER hub.
    # Each quadrant uses hf-glass-panel + the role's accent color.
    quad_htmls = []
    color_to_glass = {
        "#4D9FFF": "hf-glass-cyan", "#25D8FF": "hf-glass-cyan",
        "#2ED573": "hf-glass-green",
        "#FF6B35": "hf-glass-amber", "#FFB627": "hf-glass-amber",
        "#A855F7": "hf-glass-purple",
    }
    for pos, qkey, quadrant in zip(positions, ["q1", "q2", "q3", "q4"], quadrants):
        top_left, _ = pos
        qcolor = quadrant.get("color", acc)
        glass_class = color_to_glass.get(qcolor.upper(), "")
        quad_htmls.append(f"""
        <div class="framework-quad hf-glass-panel {glass_class} hf-animate-card" style="position:absolute;{top_left}width:380px;height:420px;padding:34px 30px;">
            <div class="hf-step-number" style="font-size:88px;color:{qcolor};text-shadow:0 0 18px {qcolor}66;line-height:1;margin-bottom:18px;">{qkey}</div>
            <div style="font-size:18px;letter-spacing:0.18em;color:{qcolor};margin-bottom:8px;">{quadrant.get('label', '')}</div>
            <div style="font-size:30px;font-weight:800;color:#fff;line-height:1.2;">{quadrant.get('text', '')}</div>
        </div>
        """)
    # V3-P3.11C — scene context label for reduced template feel
    context_note = scene.get("narration", "")[:18] or "四象限 · 概念分层"
    return f"""
    <div data-motion-target="scene-bg" class="hf-bg-cinematic" style="position:absolute;inset:0;background:linear-gradient(135deg,#0A1628 0%,#0A1A28 60%,#0A1428 100%);">
      <div class="bg-grid" style="opacity:.3"></div>
    </div>
    <div class="hf-safe-zone" style="position:absolute;top:200px;left:96px;right:96px;">
      <div class="hf-status-stamp hf-status-live hf-animate-stamp" style="display:inline-flex;margin-bottom:10px;font-size:16px;padding:8px 18px;">FRAMEWORK / 2X2</div>
      <h2 class="hf-animate-title" style="margin:0;font-size:54px;font-weight:900;color:#fff;line-height:1.12;letter-spacing:-1.2px;">{headline}</h2>
    </div>
    {''.join(quad_htmls)}
    <!-- V3-P3.11C — larger center hub with narrative tag -->
    <div class="hf-glass-panel hf-glass-purple hf-animate-card" style="position:absolute;top:730px;left:430px;width:220px;height:220px;border-radius:50%;display:flex;align-items:center;justify-content:center;background:radial-gradient(circle,rgba(168,85,247,0.22),rgba(37,216,255,0.10));">
        <div style="text-align:center;">
            <div style="font-size:12px;letter-spacing:0.22em;color:rgba(255,255,255,0.55);margin-bottom:2px;">FRAMEWORK</div>
            <div style="font-size:34px;font-weight:900;color:#fff;margin-top:2px;">{center_label}</div>
            <div style="font-size:12px;letter-spacing:0.12em;color:rgba(255,255,255,0.35);margin-top:4px;">{context_note}</div>
        </div>
    </div>
    <div class="scene-label" style="position:absolute;top:24px;left:24px;font-size:14px;color:{acc};opacity:0.7;">{sid} · {role}</div>
"""


def _css_framework_quadrant(sid: str, role: str, scene: dict[str, Any]) -> str:
    acc = _accent(role)
    return f"""
.{sid.lower()}-bg-grid {{ position:absolute; inset:0; pointer-events:none; background-image:linear-gradient({acc}06 1px,transparent 1px),linear-gradient(90deg,{acc}06 1px,transparent 1px); background-size:72px 72px; animation:grid-drift 18s linear infinite; }}
@keyframes grid-drift {{ 0%{{background-position:0 0;}} 100%{{background-position:72px 72px;}} }}
"""


def _gsap_framework_quadrant(sid: str, role: str, scene: dict[str, Any], start: float, duration: float) -> str:
    return f"""
const tl_{sid}=gsap.timeline({{paused:true}});
window.__timelines['{sid}']=tl_{sid};
tl_{sid}.fromTo('[data-scene-id="{sid}"] .framework-quad',{{scale:0.85,opacity:0}},{{scale:1,opacity:1,duration:0.6,stagger:0.15,ease:'back.out(1.1)'}},0);
tl_{sid}.fromTo('[data-scene-id="{sid}"] [data-motion-target="scene-bg"] .bg-grid',{{opacity:0}},{{opacity:1,duration:0.8}},0);
"""


def _template_decision_tree(sid: str, role: str, scene: dict[str, Any]) -> str:
    acc = _accent(role)
    headline = scene.get("headline", scene.get("narration", "要不要用 Obsidian")[:30] or "要不要用 Obsidian")
    root_q = scene.get("root_question", scene.get("decision_root", "你素材 > 1000 条？"))
    branches = scene.get("branches", [
        {"label": "是", "leads_to": "用 Obsidian 双链管理"},
        {"label": "否", "leads_to": "先用笔记 App 足够"},
    ])
    outcomes = scene.get("outcomes", [
        {"label": "是", "text": "先搭最小闭环", "color": "#2ED573"},
        {"label": "否", "text": "先别上系统", "color": "#FF6B35"},
    ])
    # Root node at top center
    return f"""
    <div data-motion-target="scene-bg" style="position:absolute;inset:0;background:linear-gradient(180deg,#0A1A28 0%,#0A1428 60%,#0A1628 100%);">
      <div class="bg-grid"></div>
    </div>
    <div style="position:absolute;top:200px;left:72px;right:72px;text-align:center;">
      <div style="font-size:54px;font-weight:900;color:#fff;line-height:1.12;letter-spacing:-1.2px;">{headline}</div>
    </div>
    <div style="position:absolute;top:380px;left:300px;width:480px;height:140px;background:rgba(37,216,255,0.12);border:2px solid {acc};border-radius:24px;padding:20px 24px;text-align:center;box-shadow:0 0 32px {acc}22;">
        <div style="font-size:16px;letter-spacing:0.2em;color:rgba(255,255,255,0.55);margin-bottom:8px;">DECISION / ROOT</div>
        <div style="font-size:32px;font-weight:800;color:#fff;line-height:1.2;">{root_q}</div>
    </div>
    <div style="position:absolute;top:540px;left:540px;width:2px;height:80px;background:linear-gradient(180deg,{acc},transparent);"></div>
    <div style="position:absolute;top:620px;left:140px;width:760px;height:2px;background:linear-gradient(90deg,#2ED573 0%,#2ED573 50%,#FF6B35 50%,#FF6B35 100%);"></div>
    <div style="position:absolute;top:640px;left:200px;width:2px;height:80px;background:#2ED573;"></div>
    <div style="position:absolute;top:640px;left:840px;width:2px;height:80px;background:#FF6B35;"></div>
    <div style="position:absolute;top:720px;left:60px;width:340px;background:rgba(46,213,115,0.12);border:2px solid #2ED573;border-radius:22px;padding:20px 22px;">
        <div style="font-size:16px;letter-spacing:0.2em;color:#2ED573;margin-bottom:6px;">是 / YES</div>
        <div style="font-size:24px;font-weight:800;color:#fff;line-height:1.3;">{branches[0].get('leads_to', '') if branches else ''}</div>
    </div>
    <div style="position:absolute;top:720px;right:60px;width:340px;background:rgba(255,107,53,0.12);border:2px solid #FF6B35;border-radius:22px;padding:20px 22px;text-align:right;">
        <div style="font-size:16px;letter-spacing:0.2em;color:#FF6B35;margin-bottom:6px;">否 / NO</div>
        <div style="font-size:24px;font-weight:800;color:#fff;line-height:1.3;">{branches[1].get('leads_to', '') if len(branches) > 1 else ''}</div>
    </div>
    <div style="position:absolute;top:1000px;left:80px;width:380px;background:rgba(46,213,115,0.08);border:1px solid rgba(46,213,115,0.3);border-radius:18px;padding:18px 20px;">
        <div style="font-size:14px;letter-spacing:0.18em;color:rgba(255,255,255,0.55);margin-bottom:6px;">OUTCOME 1</div>
        <div style="font-size:26px;font-weight:800;color:#2ED573;line-height:1.3;">{outcomes[0].get('text', '') if outcomes else ''}</div>
    </div>
    <div style="position:absolute;top:1000px;right:80px;width:380px;background:rgba(255,107,53,0.08);border:1px solid rgba(255,107,53,0.3);border-radius:18px;padding:18px 20px;">
        <div style="font-size:14px;letter-spacing:0.18em;color:rgba(255,255,255,0.55);margin-bottom:6px;">OUTCOME 2</div>
        <div style="font-size:26px;font-weight:800;color:#FF6B35;line-height:1.3;">{outcomes[1].get('text', '') if len(outcomes) > 1 else ''}</div>
    </div>
    <div class="scene-label" style="position:absolute;top:24px;left:24px;font-size:14px;color:{acc};opacity:0.7;">{sid} · {role}</div>
"""


def _css_decision_tree(sid: str, role: str, scene: dict[str, Any]) -> str:
    acc = _accent(role)
    return f"""
.{sid.lower()}-bg-grid {{ position:absolute; inset:0; pointer-events:none; background-image:linear-gradient({acc}06 1px,transparent 1px),linear-gradient(90deg,{acc}06 1px,transparent 1px); background-size:72px 72px; animation:grid-drift 18s linear infinite; }}
@keyframes grid-drift {{ 0%{{background-position:0 0;}} 100%{{background-position:72px 72px;}} }}
"""


def _gsap_decision_tree(sid: str, role: str, scene: dict[str, Any], start: float, duration: float) -> str:
    return f"""
const tl_{sid}=gsap.timeline({{paused:true}});
window.__timelines['{sid}']=tl_{sid};
tl_{sid}.fromTo('[data-scene-id="{sid}"] [data-motion-target="scene-bg"] .bg-grid',{{opacity:0}},{{opacity:1,duration:0.8}},0);
"""


def _template_metric_dashboard(sid: str, role: str, scene: dict[str, Any]) -> str:
    acc = _accent(role)
    headline = scene.get("headline", scene.get("narration", "三个月后的实际数据")[:30] or "三个月后的实际数据")
    metrics = scene.get("metrics", [
        {"label": "日均输出", "value": "3.2 篇", "delta": "+40%"},
        {"label": "素材利用率", "value": "78%", "delta": "+52%"},
        {"label": "检索响应", "value": "12s", "delta": "-65%"},
        {"label": "完播率", "value": "61%", "delta": "+18%"},
    ])
    trend_caption = scene.get("trend_caption", "3 个月持续跑通最小闭环")
    cyan, amber, green, red = "#38E1FF", "#FFC83D", "#2EE874", "#FF5577"
    # V3-P3.9R1 — single HUGE hero number + 3 satellite metric cards.
    # The hero number is the visual anchor; satellites are supporting.
    hero_metric = metrics[0] if metrics else {"label": "—", "value": "—", "delta": "—"}
    satellites = metrics[1:4] if len(metrics) >= 4 else metrics[1:]
    # Hero color: amber if number is a percentage/ratio, else cyan
    hero_value = hero_metric.get("value", "")
    if any(c in hero_value for c in ["%", "x", "倍"]):
        hero_class = "amber"
        hero_color = amber
    elif any(c in hero_value for c in ["篇", "s"]):
        hero_class = ""
        hero_color = cyan
    else:
        hero_class = ""
        hero_color = cyan
    # Strip the unit (e.g. "3.2 篇" → "3.2" + "篇") for bigger impact
    import re as _re
    m = _re.match(r"^([\d.]+)\s*(.*)$", hero_value)
    if m:
        hero_num, hero_unit = m.group(1), m.group(2)
        hero_is_numeric = True
    else:
        hero_num = hero_value
        hero_unit = ""
        hero_is_numeric = False

    metric_htmls = []
    # Hero card — left side, takes ~55% width
    hero_delta = hero_metric.get("delta", "")
    hero_delta_color = green if hero_delta.startswith("+") else (red if hero_delta.startswith("-") else amber)
    # V3-P3.11C — non-numeric values show as status badge instead of giant number
    if not hero_is_numeric:
        hero_content = f"""
        <div style="display:flex;align-items:center;justify-content:center;margin-top:32px;">
          <div class="hf-status-stamp hf-status-live hf-animate-stamp" style="font-size:48px;padding:28px 40px;border-width:3px;color:{cyan};border-color:{cyan};background:rgba(56,225,255,0.12);box-shadow:0 0 32px rgba(56,225,255,0.3);">{hero_num}</div>
        </div>
        <div style="font-size:28px;color:rgba(255,255,255,0.55);margin-top:24px;text-align:center;letter-spacing:.08em;">系统状态</div>
        <div style="font:800 28px/1 &quot;SF Mono&quot;,monospace;color:{hero_delta_color};margin-top:16px;text-align:center;letter-spacing:.04em;">{hero_delta}</div>
        """
    else:
        hero_content = f"""
        <div style="display:flex;align-items:baseline;gap:14px;margin-top:32px;">
          <span class="hf-big-number {hero_class} hf-animate-number" style="font-size:240px;">{hero_num}</span>
          <span style="font:800 56px/1 &quot;SF Mono&quot;,monospace;letter-spacing:.04em;color:#FFFFFF;text-shadow:0 0 14px rgba(255,255,255,0.4);">{hero_unit}</span>
        </div>
        <div class="hf-progress" style="margin-top:30px;--hf-target:78%;height:14px;border-radius:7px;">
          <div class="hf-progress-fill" style="background:linear-gradient(90deg,{cyan},{amber});box-shadow:0 0 16px {cyan}cc;"></div>
        </div>
        <div style="font:800 40px/1 &quot;SF Mono&quot;,monospace;color:{hero_delta_color};margin-top:20px;letter-spacing:.04em;">{hero_delta} vs 起点</div>
        """
    metric_htmls.append(f"""
    <div class="hf-glass-panel hf-animate-card" style="position:absolute;top:420px;left:60px;width:520px;height:560px;padding:52px 48px;background:linear-gradient(180deg,rgba(2,4,12,0.78),rgba(2,4,12,0.62) 80%);">
      <div class="hf-status-stamp hf-status-viral hf-animate-stamp" style="position:absolute;top:24px;right:24px;font-size:14px;padding:6px 14px;border-width:2px;">VIRAL</div>
      <div style="font:800 20px/1 &quot;SF Mono&quot;,monospace;letter-spacing:0.22em;color:rgba(248,250,252,0.72);text-transform:uppercase;">{hero_metric.get('label', '')}</div>
      {hero_content}
    </div>
    """)
    # Satellite tiles — right column, 3 stacked
    sat_y = [420, 620, 820]
    for i, m in enumerate(satellites):
        if i >= 3: break
        delta = m.get("delta", "")
        delta_color = green if delta.startswith("+") else (red if delta.startswith("-") else amber)
        # Split value into number + unit
        mm = _re.match(r"^([\d.]+)\s*(.*)$", m.get("value", ""))
        sat_num, sat_unit = (mm.group(1), mm.group(2)) if mm else (m.get("value", ""), "")
        metric_htmls.append(f"""
        <div class="hf-glass-panel hf-animate-card" style="position:absolute;top:{sat_y[i]}px;right:60px;width:280px;padding:24px 26px;background:rgba(2,4,12,0.62);">
          <div style="font:700 16px/1 &quot;SF Mono&quot;,monospace;letter-spacing:0.22em;color:rgba(248,250,252,0.72);text-transform:uppercase;">{m.get('label', '')}</div>
          <div style="display:flex;align-items:baseline;gap:8px;margin-top:12px;">
            <span style="font:900 64px/1 &quot;SF Pro Display&quot;,Arial,sans-serif;color:#FFFFFF;letter-spacing:-.02em;text-shadow:0 0 12px rgba(255,255,255,0.3);">{sat_num}</span>
            <span style="font:800 24px/1 &quot;SF Mono&quot;,monospace;color:{acc};">{sat_unit}</span>
          </div>
          <div style="font:700 18px/1 &quot;SF Mono&quot;,monospace;color:{delta_color};margin-top:8px;">{delta}</div>
        </div>
        """)
    return f"""
    <div data-motion-target="scene-bg" class="hf-bg-cinematic" style="position:absolute;inset:0;background:linear-gradient(135deg,#0A1428 0%,#0A1A28 60%,#082016 100%);">
      <div class="bg-grid" style="opacity:.25"></div>
    </div>
    <div class="hf-safe-zone" style="position:absolute;top:200px;left:80px;right:80px;text-align:left;">
      <div class="hf-status-stamp hf-status-live hf-animate-stamp" style="display:inline-flex;margin-bottom:14px;font-size:18px;padding:10px 22px;border-width:2px;">LIVE METRICS · 实时数据</div>
      <h2 class="hf-animate-title" style="margin:0;font-size:64px;font-weight:900;color:#FFFFFF;line-height:1.1;letter-spacing:-.02em;">{headline}</h2>
    </div>
    {''.join(metric_htmls)}
    <div style="position:absolute;top:1400px;left:140px;right:140px;padding:20px 28px;border-top:2px solid rgba(255,200,61,0.4);text-align:center;font:800 26px/1 &quot;SF Mono&quot;,monospace;letter-spacing:.18em;color:#FFC83D;text-transform:uppercase;">{trend_caption}</div>
    <div class="scene-label" style="position:absolute;top:24px;left:24px;font-size:14px;color:{acc};opacity:0.7;">{sid} · {role}</div>
"""


def _css_metric_dashboard(sid: str, role: str, scene: dict[str, Any]) -> str:
    acc = _accent(role)
    return f"""
.{sid.lower()}-bg-grid {{ position:absolute; inset:0; pointer-events:none; background-image:linear-gradient({acc}06 1px,transparent 1px),linear-gradient(90deg,{acc}06 1px,transparent 1px); background-size:72px 72px; animation:grid-drift 18s linear infinite; }}
@keyframes grid-drift {{ 0%{{background-position:0 0;}} 100%{{background-position:72px 72px;}} }}
"""


def _gsap_metric_dashboard(sid: str, role: str, scene: dict[str, Any], start: float, duration: float) -> str:
    return f"""
const tl_{sid}=gsap.timeline({{paused:true}});
window.__timelines['{sid}']=tl_{sid};
tl_{sid}.fromTo('[data-scene-id="{sid}"] .metric-tile',{{y:60,opacity:0}},{{y:0,opacity:1,duration:0.55,stagger:0.18,ease:'power2.out'}},0);
tl_{sid}.fromTo('[data-scene-id="{sid}"] [data-motion-target="scene-bg"] .bg-grid',{{opacity:0}},{{opacity:1,duration:0.8}},0);
"""


def _template_case_study_card(sid: str, role: str, scene: dict[str, Any]) -> str:
    acc = _accent(role)
    headline = scene.get("headline", scene.get("narration", "真实案例")[:30] or "真实案例")
    case_subject = scene.get("case_subject", scene.get("case_label", "李同学 · 知识管理 90 天"))
    before = scene.get("before", "笔记散 5 个 App，写一篇要 6 小时")
    after = scene.get("after", "统一到 Obsidian + AI，1.5 小时成稿")
    highlights = scene.get("highlights", ["整理耗时下降 75%", "素材复用率 3.4×", "AI 草稿接受率 80%"])
    red, green, amber = "#FF5577", "#2EE874", "#FFC83D"
    # V3-P3.11D — CRITICAL FIX: BEFORE/AFTER cards no longer overlap.
    # BEFORE moved to left:80, width:420 (spans x:80-500).
    # AFTER moved to left:540, width:460 (spans x:540-1000).
    # Both at same top:460. 40px gap between them. Bottom anchor added.
    return f"""
    <div data-motion-target="scene-bg" class="hf-bg-cinematic" style="position:absolute;inset:0;background:linear-gradient(160deg,#0A1628 0%,#0A1A28 60%,#101B32 100%);">
      <div class="bg-grid" style="opacity:.25"></div>
    </div>
    <div class="hf-safe-zone" style="position:absolute;top:180px;left:80px;right:80px;">
      <div class="hf-status-stamp hf-status-viral hf-animate-stamp" style="display:inline-flex;margin-bottom:14px;font-size:18px;padding:10px 22px;">真实案例 · 90 天实践</div>
      <h2 class="hf-animate-title" style="margin:0 0 6px 0;font-size:64px;font-weight:900;color:#FFFFFF;line-height:1.1;letter-spacing:-.02em;">{headline}</h2>
      <div class="hf-animate-title" style="font-size:28px;color:rgba(248,250,252,0.78);margin-top:4px;letter-spacing:.04em;">{case_subject}</div>
    </div>
    <div class="hf-glass-panel hf-glass-red hf-animate-card" style="position:absolute;top:460px;left:80px;width:420px;padding:48px 40px;background:linear-gradient(180deg,rgba(255,85,119,0.22),rgba(2,4,12,0.62) 60%);">
      <div class="hf-status-stamp hf-status-risk hf-animate-stamp" style="position:absolute;top:24px;right:24px;font-size:18px;padding:8px 18px;border-width:2px;">BEFORE</div>
      <div style="font:800 22px/1 &quot;SF Mono&quot;,monospace;letter-spacing:0.22em;color:{red};margin-bottom:14px;text-transform:uppercase;">之前 · OLD WAY</div>
      <div style="font-size:44px;font-weight:800;color:#FFFFFF;line-height:1.2;letter-spacing:-.01em;">{before}</div>
    </div>
    <div class="hf-glass-panel hf-glass-green hf-animate-card" style="position:absolute;top:460px;left:540px;width:460px;padding:48px 40px;background:linear-gradient(180deg,rgba(46,232,116,0.22),rgba(2,4,12,0.62) 60%);">
      <div class="hf-status-stamp hf-status-pass hf-animate-stamp" style="position:absolute;top:24px;right:24px;font-size:18px;padding:8px 18px;border-width:2px;">AFTER</div>
      <div style="font:800 22px/1 &quot;SF Mono&quot;,monospace;letter-spacing:0.22em;color:{green};margin-bottom:14px;text-transform:uppercase;">之后 · NEW WAY</div>
      <div style="font-size:38px;font-weight:800;color:#FFFFFF;line-height:1.2;letter-spacing:-.01em;">{after}</div>
    </div>
    <div class="hf-animate-card" style="position:absolute;top:420px;left:50%;transform:translateX(-50%);display:flex;gap:14px;align-items:center;font:800 18px/1 &quot;SF Mono&quot;,monospace;letter-spacing:.22em;color:#FFFFFF;text-transform:uppercase;">
      <span style="color:{red};">BEFORE</span>
      <span style="font-size:36px;color:{amber};text-shadow:0 0 14px {amber}aa;">→</span>
      <span style="color:{green};">AFTER</span>
    </div>
    <!-- V3-P3.11D — bottom anchor: result summary below side-by-side cards -->
    <div style="position:absolute;bottom:360px;left:50%;transform:translateX(-50%);text-align:center;">
      <div style="width:140px;height:3px;margin:0 auto 16px;background:linear-gradient(90deg,{red},{amber},{green});border-radius:2px;"></div>
      <div style="font-size:24px;font-weight:600;color:rgba(255,255,255,0.40);letter-spacing:.06em;">· OLD → NEW · 真实变化 ·</div>
    </div>
    <div class="scene-label" style="position:absolute;top:24px;left:24px;font-size:14px;color:{acc};opacity:0.7;">{sid} · {role}</div>
"""


def _css_case_study_card(sid: str, role: str, scene: dict[str, Any]) -> str:
    acc = _accent(role)
    return f"""
.{sid.lower()}-bg-grid {{ position:absolute; inset:0; pointer-events:none; background-image:linear-gradient({acc}06 1px,transparent 1px),linear-gradient(90deg,{acc}06 1px,transparent 1px); background-size:72px 72px; animation:grid-drift 18s linear infinite; }}
@keyframes grid-drift {{ 0%{{background-position:0 0;}} 100%{{background-position:72px 72px;}} }}
"""


def _gsap_case_study_card(sid: str, role: str, scene: dict[str, Any], start: float, duration: float) -> str:
    return f"""
const tl_{sid}=gsap.timeline({{paused:true}});
window.__timelines['{sid}']=tl_{sid};
tl_{sid}.fromTo('[data-scene-id="{sid}"] [data-motion-target="scene-bg"] .bg-grid',{{opacity:0}},{{opacity:1,duration:0.8}},0);
"""


def _template_section_board(sid: str, role: str, scene: dict[str, Any]) -> str:
    acc = _accent(role)
    headline = scene.get("headline", scene.get("narration", "四个判断维度")[:30] or "四个判断维度")
    sections = scene.get("sections", [
        {"label": "获得感", "text": "学到至少 1 个能用的方法"},
        {"label": "收藏价值", "text": "可以复用的检查清单"},
        {"label": "评论触发", "text": "可执行的下一步动作"},
        {"label": "复看理由", "text": "信息密度足够高"},
    ])
    positions = [(72, 480), (548, 480), (72, 940), (548, 940)]
    section_htmls = []
    for idx, (s, (x, y)) in enumerate(zip(sections, positions), start=1):
        section_htmls.append(f"""
        <div class="board-section" style="position:absolute;top:{y}px;left:{x}px;width:444px;height:380px;background:linear-gradient(180deg,rgba(255,255,255,0.05),rgba(255,255,255,0.02));border:1px solid rgba(255,255,255,0.16);border-radius:28px;padding:30px 28px;box-shadow:0 0 28px rgba(0,0,0,0.18);">
            <div style="display:flex;align-items:center;gap:18px;margin-bottom:18px;">
                <div style="width:64px;height:64px;border-radius:16px;background:{acc}22;border:1px solid {acc}66;display:flex;align-items:center;justify-content:center;font-size:28px;font-weight:900;color:{acc};">0{idx}</div>
                <div style="font-size:24px;letter-spacing:0.16em;color:rgba(255,255,255,0.7);font-weight:700;">{s.get('label', '')}</div>
            </div>
            <div style="font-size:30px;font-weight:700;color:#fff;line-height:1.4;">{s.get('text', '')}</div>
        </div>
        """)
    return f"""
    <div data-motion-target="scene-bg" style="position:absolute;inset:0;background:linear-gradient(160deg,#1A0A0A 0%,#0A1428 50%,#0A1A28 100%);">
      <div class="bg-grid"></div>
    </div>
    <div style="position:absolute;top:230px;left:72px;right:72px;text-align:center;">
      <div style="display:inline-flex;padding:8px 20px;border-radius:999px;background:rgba(255,107,53,0.12);border:1px solid {acc}66;color:{acc};font-size:18px;letter-spacing:0.22em;margin-bottom:18px;">SECTION / BOARD</div>
      <div style="font-size:54px;font-weight:900;color:#fff;line-height:1.12;letter-spacing:-1.2px;">{headline}</div>
    </div>
    {''.join(section_htmls)}
    <div class="scene-label" style="position:absolute;top:24px;left:24px;font-size:14px;color:{acc};opacity:0.7;">{sid} · {role}</div>
"""


def _css_section_board(sid: str, role: str, scene: dict[str, Any]) -> str:
    acc = _accent(role)
    return f"""
.{sid.lower()}-bg-grid {{ position:absolute; inset:0; pointer-events:none; background-image:linear-gradient({acc}06 1px,transparent 1px),linear-gradient(90deg,{acc}06 1px,transparent 1px); background-size:72px 72px; animation:grid-drift 18s linear infinite; }}
@keyframes grid-drift {{ 0%{{background-position:0 0;}} 100%{{background-position:72px 72px;}} }}
"""


def _gsap_section_board(sid: str, role: str, scene: dict[str, Any], start: float, duration: float) -> str:
    return f"""
const tl_{sid}=gsap.timeline({{paused:true}});
window.__timelines['{sid}']=tl_{sid};
tl_{sid}.fromTo('[data-scene-id="{sid}"] .board-section',{{y:50,opacity:0}},{{y:0,opacity:1,duration:0.5,stagger:0.18,ease:'power2.out'}},0);
tl_{sid}.fromTo('[data-scene-id="{sid}"] [data-motion-target="scene-bg"] .bg-grid',{{opacity:0}},{{opacity:1,duration:0.8}},0);
"""


def _template_comment_question(sid: str, role: str, scene: dict[str, Any]) -> str:
    acc = _accent(role)
    headline = scene.get("headline", scene.get("narration", "你想先跑通哪一步？")[:30] or "你想先跑通哪一步？")
    fake_comment = scene.get("fake_comment", "“我之前用过 3 个笔记 App，最后都放弃了”")
    guide_q = scene.get("guide_question", "你愿意先只保留一个入口吗？评论区告诉我")
    return f"""
    <div data-motion-target="scene-bg" style="position:absolute;inset:0;background:linear-gradient(180deg,#0A1628 0%,#1A0A0A 60%,#0A1428 100%);">
      <div class="bg-grid"></div>
    </div>
    <div style="position:absolute;top:240px;left:72px;right:72px;text-align:center;">
      <div style="display:inline-flex;padding:8px 20px;border-radius:999px;background:rgba(255,71,87,0.12);border:1px solid {acc}66;color:{acc};font-size:18px;letter-spacing:0.22em;margin-bottom:18px;">COMMENT / ASK</div>
      <div style="font-size:56px;font-weight:900;color:#fff;line-height:1.12;letter-spacing:-1.4px;">{headline}</div>
    </div>
    <div class="comment-bubble" style="position:absolute;top:540px;left:120px;right:120px;background:linear-gradient(180deg,rgba(255,255,255,0.08),rgba(255,255,255,0.04));border:2px solid rgba(255,71,87,0.4);border-radius:28px;padding:36px 32px;box-shadow:0 0 36px rgba(255,71,87,0.14);">
        <div style="display:flex;align-items:center;gap:14px;margin-bottom:18px;">
            <div style="width:60px;height:60px;border-radius:50%;background:linear-gradient(135deg,#FF4757,#FF6B35);display:flex;align-items:center;justify-content:center;font-size:28px;font-weight:900;color:#fff;">U</div>
            <div>
                <div style="font-size:18px;letter-spacing:0.18em;color:rgba(255,255,255,0.55);">REAL USER</div>
                <div style="font-size:14px;color:rgba(255,255,255,0.4);margin-top:2px;">读者评论</div>
            </div>
        </div>
        <div style="font-size:36px;font-weight:700;color:#fff;line-height:1.32;letter-spacing:-0.4px;">{fake_comment}</div>
    </div>
    <div style="position:absolute;top:1080px;left:120px;right:120px;background:linear-gradient(135deg,rgba(37,216,255,0.18),rgba(77,159,255,0.12));border:2px solid {acc};border-radius:24px;padding:26px 28px;text-align:center;">
        <div style="font-size:18px;letter-spacing:0.2em;color:rgba(255,255,255,0.7);margin-bottom:8px;">ASK / 引导</div>
        <div style="font-size:32px;font-weight:800;color:#fff;line-height:1.32;">{guide_q}</div>
    </div>
    <div class="scene-label" style="position:absolute;top:24px;left:24px;font-size:14px;color:{acc};opacity:0.7;">{sid} · {role}</div>
"""


def _css_comment_question(sid: str, role: str, scene: dict[str, Any]) -> str:
    acc = _accent(role)
    return f"""
.{sid.lower()}-bg-grid {{ position:absolute; inset:0; pointer-events:none; background-image:linear-gradient({acc}06 1px,transparent 1px),linear-gradient(90deg,{acc}06 1px,transparent 1px); background-size:72px 72px; animation:grid-drift 18s linear infinite; }}
@keyframes grid-drift {{ 0%{{background-position:0 0;}} 100%{{background-position:72px 72px;}} }}
"""


def _gsap_comment_question(sid: str, role: str, scene: dict[str, Any], start: float, duration: float) -> str:
    return f"""
const tl_{sid}=gsap.timeline({{paused:true}});
window.__timelines['{sid}']=tl_{sid};
tl_{sid}.fromTo('[data-scene-id="{sid}"] [data-motion-target="scene-bg"] .bg-grid',{{opacity:0}},{{opacity:1,duration:0.8}},0);
"""


# ─────────────────────────────────────────────────────────────────
# P3.4 — 8 new seed renderers
# countdown_strike / keyword_punchline / data_dense_table /
# step_ladder / concept_layers / progress_tracker /
# knowledge_graph / quote_close
# All reuse existing HUD card / scanline / accent palette.
# ─────────────────────────────────────────────────────────────────

def _template_countdown_strike(sid: str, role: str, scene: dict[str, Any]) -> str:
    acc = _accent(role)
    headline = scene.get("headline", scene.get("narration", "你只剩 3 天")[:30] or "你只剩 3 天")
    steps = scene.get("countdown_steps", [
        {"num": "03", "label": "找到入口"},
        {"num": "02", "label": "跑通最小"},
        {"num": "01", "label": "开始输出"},
    ])
    final_label = scene.get("final_label", "GO / NOW")
    rows = []
    for idx, step in enumerate(steps):
        y = 500 + idx * 220
        rows.append(f"""
        <div class="countdown-row" style="position:absolute;top:{y}px;left:120px;width:840px;display:flex;align-items:center;gap:32px;padding:20px 28px;background:rgba(255,71,87,0.08);border:2px solid {acc};border-radius:24px;box-shadow:0 0 28px {acc}22;">
            <div style="font-size:96px;font-weight:900;color:{acc};line-height:0.9;letter-spacing:-2px;text-shadow:0 0 32px {acc}66;">{step.get('num', '')}</div>
            <div style="flex:1;font-size:38px;font-weight:700;color:#fff;line-height:1.2;">{step.get('label', '')}</div>
        </div>
        """)
    return f"""
    <div data-motion-target="scene-bg" style="position:absolute;inset:0;background:linear-gradient(180deg,#0A1628 0%,#1A0A0A 60%,#0A1628 100%);">
      <div class="bg-grid"></div>
      <div class="bg-glow bg-glow-1" style="background:radial-gradient(circle,{acc}22 0%,transparent 70%);"></div>
    </div>
    <div style="position:absolute;top:240px;left:72px;right:72px;text-align:center;">
      <div style="display:inline-flex;padding:8px 20px;border-radius:999px;background:rgba(255,71,87,0.12);border:1px solid {acc}66;color:{acc};font-size:18px;letter-spacing:0.22em;margin-bottom:18px;">COUNTDOWN / STRIKE</div>
      <div style="font-size:64px;font-weight:900;color:#fff;line-height:1.1;letter-spacing:-1.4px;">{headline}</div>
    </div>
    {''.join(rows)}
    <div style="position:absolute;top:1230px;left:0;right:0;text-align:center;">
      <div style="display:inline-flex;padding:18px 42px;border-radius:22px;background:{acc};color:#0A1628;font-size:42px;font-weight:900;letter-spacing:-0.6px;box-shadow:0 0 48px {acc}66;">▶ {final_label}</div>
    </div>
    <div class="scene-label" style="position:absolute;top:24px;left:24px;font-size:14px;color:{acc};opacity:0.7;">{sid} · {role}</div>
"""


def _css_countdown_strike(sid: str, role: str, scene: dict[str, Any]) -> str:
    acc = _accent(role)
    return f"""
.{sid.lower()}-bg-grid {{ position:absolute; inset:0; pointer-events:none; background-image:linear-gradient({acc}06 1px,transparent 1px),linear-gradient(90deg,{acc}06 1px,transparent 1px); background-size:72px 72px; animation:grid-drift 18s linear infinite; }}
@keyframes grid-drift {{ 0%{{background-position:0 0;}} 100%{{background-position:72px 72px;}} }}
"""


def _gsap_countdown_strike(sid: str, role: str, scene: dict[str, Any], start: float, duration: float) -> str:
    return f"""
const tl_{sid}=gsap.timeline({{paused:true}});
window.__timelines['{sid}']=tl_{sid};
tl_{sid}.fromTo('[data-scene-id="{sid}"] .countdown-row',{{x:80,opacity:0}},{{x:0,opacity:1,duration:0.5,stagger:0.2,ease:'back.out(1.2)'}},0);
"""


def _template_keyword_punchline(sid: str, role: str, scene: dict[str, Any]) -> str:
    acc = _accent(role)
    keyword = scene.get("keyword", "记住")
    punchline = scene.get("punchline", scene.get("narration", "不是多一个工具，而是把链路接通")[:30] or "不是多一个工具")
    amber, cyan, green = "#FFC83D", "#38E1FF", "#2EE874"
    return f"""
    <div data-motion-target="scene-bg" class="hf-bg-cinematic" style="position:absolute;inset:0;background:{_bg(role)};">
      <div class="bg-grid" style="opacity:.25"></div>
      <div class="bg-glow bg-glow-1" style="background:radial-gradient(circle,rgba(255,200,61,0.3) 0%,transparent 70%);"></div>
    </div>
    <!-- KEYWORD label -->
    <div style="position:absolute;top:180px;left:0;right:0;text-align:center;">
      <div style="font-size:18px;letter-spacing:0.32em;color:rgba(255,255,255,0.5);">KEYWORD / INSIGHT</div>
    </div>
    <!-- V3-P3.11E — big keyword with glow block -->
    <div style="position:absolute;top:300px;left:50%;transform:translateX(-50%);text-align:center;">
      <div style="display:inline-flex;padding:28px 72px;border-radius:36px;background:linear-gradient(135deg,rgba(255,200,61,0.25),rgba(255,107,53,0.15));box-shadow:0 0 80px rgba(255,200,61,0.4);border:2px solid {amber}55;">
        <div class="hf-animate-title" style="font-size:180px;font-weight:900;color:{amber};letter-spacing:-6px;line-height:0.9;text-shadow:0 0 40px {amber}88;">{keyword}</div>
      </div>
    </div>
    <!-- Two explanation cards -->
    <div class="hf-glass-panel hf-animate-card" style="position:absolute;top:680px;left:120px;width:820px;height:100px;padding:20px 28px;display:flex;align-items:center;gap:20px;background:rgba(56,225,255,0.08);border-color:rgba(56,225,255,0.3);">
      <div style="width:48px;height:48px;border-radius:12px;background:{cyan};display:flex;align-items:center;justify-content:center;font-size:24px;flex-shrink:0;">1</div>
      <div style="font-size:30px;font-weight:700;color:#fff;">不是背下来，是写作时能被调用</div>
    </div>
    <div class="hf-glass-panel hf-animate-card" style="position:absolute;top:810px;left:120px;width:820px;height:100px;padding:20px 28px;display:flex;align-items:center;gap:20px;background:rgba(199,125,255,0.08);border-color:rgba(199,125,255,0.3);">
      <div style="width:48px;height:48px;border-radius:12px;background:#C77DFF;display:flex;align-items:center;justify-content:center;font-size:24px;flex-shrink:0;">2</div>
      <div style="font-size:30px;font-weight:700;color:#fff;">不是收藏更多，是让素材进入系统</div>
    </div>
    <!-- Result anchor -->
    <div class="hf-result-card hf-page-anchor" style="border-color:{green}44;background:rgba(46,232,116,0.08);">
      <div class="hf-glow-divider" style="background:linear-gradient(90deg,{green},transparent);"></div>
      <span class="hf-mini-badge" style="background:{green}22;color:{green};margin-bottom:8px;">INSIGHT</span>
      <div style="font-size:28px;font-weight:700;color:#fff;line-height:1.3;">记住 = 能在需要时立刻调用</div>
    </div>
    <div class="scene-label" style="position:absolute;top:24px;left:24px;font-size:14px;color:{acc};opacity:0.7;">{sid} · {role}</div>
"""


def _css_keyword_punchline(sid: str, role: str, scene: dict[str, Any]) -> str:
    acc = _accent(role)
    return f"""
.{sid.lower()}-bg-grid {{ position:absolute; inset:0; pointer-events:none; background-image:linear-gradient({acc}06 1px,transparent 1px),linear-gradient(90deg,{acc}06 1px,transparent 1px); background-size:72px 72px; animation:grid-drift 18s linear infinite; }}
@keyframes grid-drift {{ 0%{{background-position:0 0;}} 100%{{background-position:72px 72px;}} }}
"""


def _gsap_keyword_punchline(sid: str, role: str, scene: dict[str, Any], start: float, duration: float) -> str:
    return f"""
const tl_{sid}=gsap.timeline({{paused:true}});
window.__timelines['{sid}']=tl_{sid};
tl_{sid}.fromTo('[data-scene-id="{sid}"] [data-motion-target="scene-bg"] .bg-grid',{{opacity:0}},{{opacity:1,duration:0.8}},0);
"""


def _template_data_dense_table(sid: str, role: str, scene: dict[str, Any]) -> str:
    acc = _accent(role)
    headline = scene.get("headline", scene.get("narration", "输入流汇聚状态")[:30] or "输入流汇聚状态")
    rows = scene.get("rows", [
        {"label": "微信读书笔记", "status": "SYNC", "value": "1,234"},
        {"label": "网页剪藏", "status": "SYNC", "value": "568"},
        {"label": "语音转写", "status": "PENDING", "value": "21"},
        {"label": "视频笔记", "status": "STALE", "value": "12"},
    ])
    summary = scene.get("summary", "87% 已同步，13% 待处理")
    status_color = {"SYNC": "#2ED573", "PENDING": "#FBBF24", "STALE": "#FF4757", "OK": "#2ED573", "FAIL": "#FF4757"}
    row_htmls = []
    for idx, row in enumerate(rows):
        y = 460 + idx * 130
        sc = status_color.get(row.get("status", "OK"), acc)
        row_htmls.append(f"""
        <div class="data-row" style="position:absolute;top:{y}px;left:72px;right:72px;height:100px;background:rgba(255,255,255,0.05);border:1px solid rgba(255,255,255,0.12);border-left:4px solid {sc};border-radius:14px;padding:20px 28px;display:flex;align-items:center;gap:24px;">
            <div style="font-size:30px;font-weight:700;color:#fff;flex:1;">{row.get('label', '')}</div>
            <div style="font-size:34px;font-weight:900;color:{sc};padding:6px 18px;border-radius:10px;background:{sc}22;letter-spacing:0.06em;">{row.get('status', '')}</div>
            <div style="font-size:32px;font-weight:900;color:rgba(255,255,255,0.85);width:140px;text-align:right;">{row.get('value', '')}</div>
        </div>
        """)
    return f"""
    <div data-motion-target="scene-bg" style="position:absolute;inset:0;background:{_bg(role)};">
      <div class="bg-grid"></div>
    </div>
    <div style="position:absolute;top:220px;left:72px;right:72px;text-align:center;">
      <div style="display:inline-flex;padding:8px 20px;border-radius:999px;background:rgba(251,191,36,0.12);border:1px solid {acc}66;color:{acc};font-size:18px;letter-spacing:0.22em;margin-bottom:18px;">DATA / DENSE</div>
      <div style="font-size:54px;font-weight:900;color:#fff;line-height:1.12;letter-spacing:-1.2px;">{headline}</div>
    </div>
    {''.join(row_htmls)}
    <div style="position:absolute;top:1280px;left:120px;right:120px;padding:18px 24px;border-top:1px solid rgba(255,255,255,0.18);text-align:center;font-size:24px;color:rgba(255,255,255,0.7);">{summary}</div>
    <div class="scene-label" style="position:absolute;top:24px;left:24px;font-size:14px;color:{acc};opacity:0.7;">{sid} · {role}</div>
"""


def _css_data_dense_table(sid: str, role: str, scene: dict[str, Any]) -> str:
    acc = _accent(role)
    return f"""
.{sid.lower()}-bg-grid {{ position:absolute; inset:0; pointer-events:none; background-image:linear-gradient({acc}06 1px,transparent 1px),linear-gradient(90deg,{acc}06 1px,transparent 1px); background-size:72px 72px; animation:grid-drift 18s linear infinite; }}
@keyframes grid-drift {{ 0%{{background-position:0 0;}} 100%{{background-position:72px 72px;}} }}
"""


def _gsap_data_dense_table(sid: str, role: str, scene: dict[str, Any], start: float, duration: float) -> str:
    return f"""
const tl_{sid}=gsap.timeline({{paused:true}});
window.__timelines['{sid}']=tl_{sid};
tl_{sid}.fromTo('[data-scene-id="{sid}"] .data-row',{{x:60,opacity:0}},{{x:0,opacity:1,duration:0.45,stagger:0.12,ease:'power2.out'}},0);
"""


def _template_step_ladder(sid: str, role: str, scene: dict[str, Any]) -> str:
    acc = _accent(role)
    headline = scene.get("headline", scene.get("narration", "从 0 到可用")[:30] or "从 0 到可用")
    steps = scene.get("steps", [
        {"label": "1. 入口", "text": "Obsidian 库"},
        {"label": "2. 链接", "text": "双向链接"},
        {"label": "3. 检索", "text": "AI 提问"},
        {"label": "4. 输出", "text": "草稿 + 复盘"},
    ])
    top_label = scene.get("top_label", "MILESTONE")
    green = "#2EE874"
    # V3-P3.9R1 — Step Panel grammar: shorter headline, larger 4 steps
    # occupying center 60% of canvas, brighter green step numbers, vertical
    # connector line through the centers of the step badges.
    # Vertical connector line — runs through the centers of step badges
    connector_y_start = 800
    connector_y_end = 800 + (len(steps) - 1) * 130
    connector = f"""
    <div style="position:absolute;top:{connector_y_start}px;left:60px;width:6px;height:{connector_y_end - connector_y_start}px;
        background:linear-gradient(180deg,rgba(46,232,116,0.85),rgba(46,232,116,0.25));
        box-shadow:0 0 18px rgba(46,232,116,0.6);border-radius:3px;z-index:3;"></div>
    """
    rung_htmls = []
    rung_height = 110
    rung_gap = 20
    for idx, step in enumerate(steps):
        y = 750 + idx * (rung_height + rung_gap)
        indent = idx * 30
        is_current = (idx == 0)  # first step is "current"
        glow = " hf-pulse" if is_current else ""
        border_color = green if is_current else "rgba(46,232,116,0.45)"
        badge_bg = "rgba(46,232,116,0.28)" if is_current else "rgba(46,232,116,0.12)"
        badge_shadow = "0 0 32px rgba(46,232,116,0.75)" if is_current else "0 0 18px rgba(46,232,116,0.4)"
        rung_htmls.append(f"""
        <div class="ladder-rung hf-glass-panel hf-glass-green hf-animate-card{glow}" style="position:absolute;top:{y}px;left:{110 + indent}px;right:{110 - indent}px;height:{rung_height}px;padding:14px 32px;display:flex;align-items:center;gap:28px;background:linear-gradient(90deg,{badge_bg},rgba(2,4,12,0.7) 70%);border-color:{border_color};">
            <div style="width:90px;height:90px;border-radius:50%;background:rgba(46,232,116,0.18);border:4px solid {green};display:flex;align-items:center;justify-content:center;font-size:48px;font-weight:900;color:{green};flex-shrink:0;box-shadow:{badge_shadow};line-height:1;">{idx+1}</div>
            <div style="flex:1;">
                <div style="font:800 18px/1 &quot;SF Mono&quot;,monospace;letter-spacing:0.18em;color:{green};margin-bottom:6px;text-transform:uppercase;">{step.get('label', '')}</div>
                <div style="font-size:36px;font-weight:800;color:#FFFFFF;line-height:1.18;letter-spacing:-.01em;">{step.get('text', '')}</div>
            </div>
        </div>
        """)
    return f"""
    <div data-motion-target="scene-bg" class="hf-bg-cinematic" style="position:absolute;inset:0;background:linear-gradient(180deg,#0A1628 0%,#0A1A28 60%,#082016 100%);">
      <div class="bg-grid" style="opacity:.25"></div>
    </div>
    <div class="hf-safe-zone" style="position:absolute;top:220px;left:80px;right:80px;text-align:left;">
      <div class="hf-status-stamp hf-status-pass hf-animate-stamp" style="display:inline-flex;margin-bottom:12px;font-size:18px;padding:10px 22px;border-width:2px;">STEP 1/4 · {top_label}</div>
      <h2 class="hf-animate-title" style="margin:0;font-size:48px;font-weight:900;color:#FFFFFF;line-height:1.1;letter-spacing:-.02em;">{headline}</h2>
    </div>
    {connector}
    {''.join(rung_htmls)}
    <div class="scene-label" style="position:absolute;top:24px;left:24px;font-size:14px;color:{acc};opacity:0.7;">{sid} · {role}</div>
"""


def _css_step_ladder(sid: str, role: str, scene: dict[str, Any]) -> str:
    acc = _accent(role)
    return f"""
.{sid.lower()}-bg-grid {{ position:absolute; inset:0; pointer-events:none; background-image:linear-gradient({acc}06 1px,transparent 1px),linear-gradient(90deg,{acc}06 1px,transparent 1px); background-size:72px 72px; animation:grid-drift 18s linear infinite; }}
@keyframes grid-drift {{ 0%{{background-position:0 0;}} 100%{{background-position:72px 72px;}} }}
"""


def _gsap_step_ladder(sid: str, role: str, scene: dict[str, Any], start: float, duration: float) -> str:
    return f"""
const tl_{sid}=gsap.timeline({{paused:true}});
window.__timelines['{sid}']=tl_{sid};
tl_{sid}.fromTo('[data-scene-id="{sid}"] .ladder-rung',{{y:60,opacity:0}},{{y:0,opacity:1,duration:0.5,stagger:0.2,ease:'back.out(1.1)'}},0);
"""


def _template_concept_layers(sid: str, role: str, scene: dict[str, Any]) -> str:
    acc = _accent(role)
    headline = scene.get("headline", scene.get("narration", "三个层次递进")[:30] or "三个层次递进")
    layers = scene.get("layers", [
        {"level": "L1", "text": "收集：素材进库"},
        {"level": "L2", "text": "结构：双向链接"},
        {"level": "L3", "text": "调用：AI 提问"},
    ])
    widths = [920, 760, 600]
    colors = [acc, "#7C3AED", "#A855F7"]
    # V3-P3.9 — Knowledge Overlay grammar: 3 receding-width glass bars with
    # accent rail on the left + accent-color L# badge. Each layer is a
    # glass panel; uses a corner bracket "ribbon" effect.
    layer_htmls = []
    for idx, (layer, w, c) in enumerate(zip(layers, widths, colors)):
        y = 500 + idx * 200
        x = (1080 - w) // 2
        glass_class = "hf-glass-amber" if c.upper() in ("#FF6B35", "#FFB627") else (
            "hf-glass-purple" if c.upper() in ("#7C3AED", "#A855F7") else "hf-glass-cyan"
        )
        layer_htmls.append(f"""
        <div class="layer-bar hf-glass-panel {glass_class} hf-animate-card" style="position:absolute;top:{y}px;left:{x}px;width:{w}px;height:160px;padding:0 32px;display:flex;align-items:center;gap:28px;background:linear-gradient(90deg,{c}33,rgba(6,8,16,0.55) 60%);">
            <div style="position:absolute;left:0;top:0;bottom:0;width:6px;background:{c};box-shadow:0 0 18px {c}66;"></div>
            <div style="width:96px;height:96px;border-radius:18px;background:{c};display:flex;align-items:center;justify-content:center;font-size:42px;font-weight:900;color:#0A1628;flex-shrink:0;box-shadow:0 0 24px {c}66;">{layer.get('level', '')}</div>
            <div style="flex:1;">
                <div style="font-size:38px;font-weight:800;color:#fff;line-height:1.18;">{layer.get('text', '')}</div>
            </div>
        </div>
        """)
    return f"""
    <div data-motion-target="scene-bg" class="hf-bg-cinematic" style="position:absolute;inset:0;background:linear-gradient(180deg,#0A1628 0%,#0F0820 60%,#0A1628 100%);">
      <div class="bg-grid" style="opacity:.3"></div>
    </div>
    <div class="hf-safe-zone" style="position:absolute;top:220px;left:96px;right:96px;">
      <div class="hf-status-stamp hf-status-live hf-animate-stamp" style="display:inline-flex;margin-bottom:10px;font-size:16px;padding:8px 18px;">CONCEPT / LAYERS</div>
      <h2 class="hf-animate-title" style="margin:0;font-size:54px;font-weight:900;color:#fff;line-height:1.12;letter-spacing:-1.2px;">{headline}</h2>
    </div>
    {''.join(layer_htmls)}
    <!-- V3-P3.11D — bottom anchor -->
    <div style="position:absolute;bottom:320px;left:50%;transform:translateX(-50%);text-align:center;">
      <div style="width:100px;height:3px;margin:0 auto 14px;background:linear-gradient(90deg,{acc},transparent);border-radius:2px;"></div>
      <div style="font-size:22px;font-weight:600;color:rgba(255,255,255,0.38);letter-spacing:.06em;">三层递进 · 从底层到顶层</div>
    </div>
    <div class="scene-label" style="position:absolute;top:24px;left:24px;font-size:14px;color:{acc};opacity:0.7;">{sid} · {role}</div>
"""


def _css_concept_layers(sid: str, role: str, scene: dict[str, Any]) -> str:
    acc = _accent(role)
    return f"""
.{sid.lower()}-bg-grid {{ position:absolute; inset:0; pointer-events:none; background-image:linear-gradient({acc}06 1px,transparent 1px),linear-gradient(90deg,{acc}06 1px,transparent 1px); background-size:72px 72px; animation:grid-drift 18s linear infinite; }}
@keyframes grid-drift {{ 0%{{background-position:0 0;}} 100%{{background-position:72px 72px;}} }}
"""


def _gsap_concept_layers(sid: str, role: str, scene: dict[str, Any], start: float, duration: float) -> str:
    return f"""
const tl_{sid}=gsap.timeline({{paused:true}});
window.__timelines['{sid}']=tl_{sid};
tl_{sid}.fromTo('[data-scene-id="{sid}"] .layer-bar',{{y:80,opacity:0}},{{y:0,opacity:1,duration:0.55,stagger:0.18,ease:'power2.out'}},0);
"""


def _template_progress_tracker(sid: str, role: str, scene: dict[str, Any]) -> str:
    acc = _accent(role)
    headline = scene.get("headline", scene.get("narration", "8 周能力曲线")[:30] or "8 周能力曲线")
    tracks = scene.get("tracks", [
        {"label": "输入", "weeks": [20, 35, 50, 60, 70, 78, 85, 90]},
        {"label": "检索", "weeks": [10, 25, 45, 60, 72, 80, 88, 93]},
        {"label": "输出", "weeks": [5, 18, 35, 50, 62, 75, 85, 92]},
    ])
    caption = scene.get("caption", "8 周跑通最小闭环后，三条曲线同步进入加速段")
    # V3-P3.11E — 3 rating cards: left name, center bar, right score
    track_config = [
        {"color": "#38E1FF", "desc": "素材调用", "status": "READY", "glass": "hf-glass-cyan"},
        {"color": "#2EE874", "desc": "结构整理", "status": "STABLE", "glass": "hf-glass-green"},
        {"color": "#FFC83D", "desc": "持续输出", "status": "GROWING", "glass": "hf-glass-amber"},
    ]
    bar_max_w = 440
    week_labels = ["W1","W2","W3","W4","W5","W6","W7","W8"]
    track_htmls = []
    for idx, (track, tc) in enumerate(zip(tracks, track_config)):
        y = 430 + idx * 220
        weeks = track.get("weeks", [])
        final_val = weeks[-1] if weeks else 0
        bar_w = int(bar_max_w * final_val / 100)
        bar_w = max(40, bar_w)
        color = tc["color"]
        track_htmls.append(f"""
        <div class="progress-track hf-glass-panel {tc['glass']} hf-animate-card" style="position:absolute;top:{y}px;left:80px;width:920px;height:160px;padding:20px 28px;display:flex;align-items:center;gap:20px;background:rgba(2,4,12,0.5);">
            <div style="width:140px;flex-shrink:0;">
                <div style="font-size:30px;font-weight:800;color:#fff;line-height:1.2;">{track.get('label', '')}</div>
                <div style="font-size:18px;color:rgba(255,255,255,0.5);margin-top:4px;">{tc['desc']}</div>
            </div>
            <div style="flex:1;">
                <div style="width:100%;height:28px;background:rgba(255,255,255,0.06);border-radius:999px;overflow:hidden;position:relative;">
                    <div style="position:absolute;left:0;top:0;bottom:0;width:{bar_w}px;background:linear-gradient(90deg,{color},rgba(255,255,255,0.3));border-radius:999px;box-shadow:0 0 14px {color}66;"></div>
                    <div style="position:absolute;left:0;right:0;top:0;bottom:0;display:flex;justify-content:space-between;align-items:center;padding:0 10px;font-size:12px;color:rgba(255,255,255,0.35);font-family:monospace;">{''.join(f'<span>{w}</span>' for w in week_labels)}</div>
                </div>
                <div style="display:flex;justify-content:space-between;margin-top:4px;">
                    <span style="font-size:12px;color:rgba(255,255,255,0.3);">W1 → W8</span>
                    <span style="font-size:14px;color:{color};">+{final_val}%</span>
                </div>
            </div>
            <div style="text-align:center;width:80px;flex-shrink:0;">
                <div style="font-size:48px;font-weight:900;color:{color};line-height:1;text-shadow:0 0 20px {color}66;">{final_val}</div>
                <div class="hf-mini-badge" style="background:{color}22;color:{color};margin-top:4px;font-size:10px;">{tc['status']}</div>
            </div>
        </div>
        """)
    return f"""
    <div data-motion-target="scene-bg" class="hf-bg-cinematic" style="position:absolute;inset:0;background:{_bg(role)};">
      <div class="bg-grid" style="opacity:.25"></div>
    </div>
    <div class="hf-safe-zone" style="position:absolute;top:200px;left:80px;right:80px;">
      <div class="hf-status-stamp hf-status-live hf-animate-stamp" style="display:inline-flex;margin-bottom:12px;font-size:16px;padding:8px 18px;">PROGRESS / TRACKER</div>
      <div class="hf-animate-title" style="font-size:52px;font-weight:900;color:#fff;line-height:1.1;">{headline}</div>
    </div>
    {''.join(track_htmls)}
    <div class="hf-result-card hf-page-anchor" style="border-color:rgba(56,225,255,0.25);background:rgba(56,225,255,0.06);">
      <div class="hf-glow-divider"></div>
      <div style="font-size:24px;color:rgba(255,255,255,0.72);line-height:1.4;">{caption}</div>
    </div>
    <div class="scene-label" style="position:absolute;top:24px;left:24px;font-size:14px;color:{acc};opacity:0.7;">{sid} · {role}</div>
"""


def _css_progress_tracker(sid: str, role: str, scene: dict[str, Any]) -> str:
    acc = _accent(role)
    return f"""
.{sid.lower()}-bg-grid {{ position:absolute; inset:0; pointer-events:none; background-image:linear-gradient({acc}06 1px,transparent 1px),linear-gradient(90deg,{acc}06 1px,transparent 1px); background-size:72px 72px; animation:grid-drift 18s linear infinite; }}
@keyframes grid-drift {{ 0%{{background-position:0 0;}} 100%{{background-position:72px 72px;}} }}
"""


def _gsap_progress_tracker(sid: str, role: str, scene: dict[str, Any], start: float, duration: float) -> str:
    return f"""
const tl_{sid}=gsap.timeline({{paused:true}});
window.__timelines['{sid}']=tl_{sid};
tl_{sid}.fromTo('[data-scene-id="{sid}"] .progress-bar',{{scaleX:0,transformOrigin:'left center'}},{{scaleX:1,duration:1.0,stagger:0.2,ease:'power2.out'}},0);
"""


def _template_knowledge_graph(sid: str, role: str, scene: dict[str, Any]) -> str:
    acc = _accent(role)
    headline = scene.get("headline", scene.get("narration", "你的知识网络")[:30] or "你的知识网络")
    purple = "#C77DFF"
    # V3-P3.9R1 — Knowledge Overlay grammar: ONE big center HUB (2x larger
    # than before) + max 4 satellites. Connections are brighter, thicker
    # lines with glow. Center HUB carries a strong title.
    nodes = scene.get("nodes", [
        {"id": "N1", "label": "时间管理", "x": 540, "y": 800},
        {"id": "N2", "label": "GTD", "x": 240, "y": 540},
        {"id": "N3", "label": "Obsidian", "x": 540, "y": 400},
        {"id": "N4", "label": "AI 提问", "x": 240, "y": 1060},
        {"id": "N5", "label": "写作复盘", "x": 840, "y": 1060},
    ])
    edges = scene.get("edges", [("N1","N2"), ("N1","N3"), ("N1","N4"), ("N1","N5")])
    central_node = scene.get("central_node", "N1")
    nodes_by_id = {n["id"]: n for n in nodes}
    # V3-P3.9R1 — edges brighter, thicker, with purple glow
    edge_htmls = []
    for src_id, dst_id in edges:
        if src_id in nodes_by_id and dst_id in nodes_by_id:
            src = nodes_by_id[src_id]
            dst = nodes_by_id[dst_id]
            x1, y1 = src["x"] + 90, src["y"] + 60
            x2, y2 = dst["x"] + 90, dst["y"] + 40
            edge_htmls.append(f"""
            <div class="kg-edge" style="position:absolute;left:{x1}px;top:{y1}px;width:{max(abs(x2-x1), 1)}px;height:4px;background:linear-gradient(90deg,{purple}cc,rgba(56,225,255,0.4));transform-origin:0 0;transform:rotate({(y2-y1)/(x2-x1+0.0001) * 57.3 if x2 != x1 else 90}deg);box-shadow:0 0 18px {purple}aa;"></div>
            """)
    node_htmls = []
    for n in nodes:
        is_central = n["id"] == central_node
        if is_central:
            # Center HUB: 2x larger, big title, purple glass
            node_htmls.append(f"""
            <div class="kg-node hf-glass-panel hf-glass-purple hf-animate-card hf-pulse" style="position:absolute;left:{n['x']-40}px;top:{n['y']-30}px;width:280px;height:180px;border-radius:28px;display:flex;flex-direction:column;align-items:center;justify-content:center;padding:12px 20px;box-shadow:0 0 64px {purple}cc;background:linear-gradient(180deg,rgba(199,125,255,0.40),rgba(2,4,12,0.7));">
              <div class="hf-status-stamp hf-status-viral hf-animate-stamp" style="margin-bottom:10px;font-size:18px;padding:10px 20px;border-width:2px;">CORE HUB</div>
              <div style="font:900 40px/1.1 &quot;PingFang SC&quot;,sans-serif;color:#FFFFFF;line-height:1.1;text-align:center;letter-spacing:-.01em;text-shadow:0 0 20px {purple}66;">{n.get('label', '')}</div>
            </div>
            """)
        else:
            # V3-P3.11C — satellite nodes enlarged from 180×80 to 200×96
            node_htmls.append(f"""
            <div class="kg-node hf-glass-panel hf-animate-card" style="position:absolute;left:{n['x']}px;top:{n['y']}px;width:200px;height:96px;display:flex;align-items:center;justify-content:center;text-align:center;padding:10px 14px;background:rgba(2,4,12,0.7);border-color:rgba(199,125,255,0.4);">
              <div style="font:800 28px/1.15 &quot;PingFang SC&quot;,sans-serif;color:#FFFFFF;line-height:1.15;letter-spacing:-.005em;">{n.get('label', '')}</div>
            </div>
            """)
    return f"""
    <div data-motion-target="scene-bg" class="hf-bg-cinematic" style="position:absolute;inset:0;background:linear-gradient(160deg,#0A1628 0%,#0F0820 60%,#0A1628 100%);">
      <div class="bg-grid" style="opacity:.25"></div>
    </div>
    <div class="hf-safe-zone" style="position:absolute;top:170px;left:80px;right:80px;">
      <div class="hf-status-stamp hf-status-viral hf-animate-stamp" style="display:inline-flex;margin-bottom:12px;font-size:18px;padding:10px 22px;border-width:2px;">KNOWLEDGE GRAPH · 知识系统</div>
      <h2 class="hf-animate-title" style="margin:0;font-size:64px;font-weight:900;color:#FFFFFF;line-height:1.1;letter-spacing:-.02em;">{headline}</h2>
    </div>
    {''.join(edge_htmls)}
    {''.join(node_htmls)}
    <div class="scene-label" style="position:absolute;top:24px;left:24px;font-size:14px;color:{acc};opacity:0.7;">{sid} · {role}</div>
"""


def _css_knowledge_graph(sid: str, role: str, scene: dict[str, Any]) -> str:
    acc = _accent(role)
    return f"""
.{sid.lower()}-bg-grid {{ position:absolute; inset:0; pointer-events:none; background-image:linear-gradient({acc}06 1px,transparent 1px),linear-gradient(90deg,{acc}06 1px,transparent 1px); background-size:72px 72px; animation:grid-drift 18s linear infinite; }}
@keyframes grid-drift {{ 0%{{background-position:0 0;}} 100%{{background-position:72px 72px;}} }}
"""


def _gsap_knowledge_graph(sid: str, role: str, scene: dict[str, Any], start: float, duration: float) -> str:
    return f"""
const tl_{sid}=gsap.timeline({{paused:true}});
window.__timelines['{sid}']=tl_{sid};
tl_{sid}.fromTo('[data-scene-id="{sid}"] .kg-node',{{scale:0.4,opacity:0}},{{scale:1,opacity:1,duration:0.5,stagger:0.1,ease:'back.out(1.3)'}},0);
tl_{sid}.fromTo('[data-scene-id="{sid}"] .kg-edge',{{opacity:0}},{{opacity:1,duration:0.5,stagger:0.08}},0.3);
"""


def _template_quote_close(sid: str, role: str, scene: dict[str, Any]) -> str:
    acc = _accent(role)
    quote = scene.get("quote", scene.get("narration", "记住，是把素材变成自己的过程")[:30] or "记住，是把素材变成自己的过程")
    attribution = scene.get("attribution", "— 第二大脑实践 90 天")
    action = scene.get("action", "先跑通最小闭环，评论区告诉我你的第一步")
    return f"""
    <div data-motion-target="scene-bg" style="position:absolute;inset:0;background:linear-gradient(180deg,#0A1628 0%,#082016 50%,#0A1628 100%);">
      <div class="bg-grid"></div>
      <div class="bg-glow bg-glow-1" style="background:radial-gradient(circle,{acc}22 0%,transparent 68%);"></div>
    </div>
    <div style="position:absolute;top:140px;left:120px;right:120px;padding:54px 50px;border:2px solid {acc};border-radius:32px;background:linear-gradient(180deg,rgba(255,255,255,0.05),rgba(255,255,255,0.02));box-shadow:0 0 56px {acc}22;text-align:center;">
        <div style="font-size:18px;letter-spacing:0.32em;color:{acc};margin-bottom:24px;">QUOTE / CLOSE</div>
        <div style="font-size:64px;font-weight:900;color:#fff;line-height:1.18;letter-spacing:-1.4px;">“{quote}”</div>
        <div style="margin-top:24px;font-size:24px;color:rgba(255,255,255,0.55);letter-spacing:0.04em;">{attribution}</div>
    </div>
    <div style="position:absolute;top:1180px;left:0;right:0;text-align:center;">
        <div style="font-size:18px;letter-spacing:0.22em;color:rgba(255,255,255,0.5);margin-bottom:14px;">ACTION / 行动</div>
        <div style="display:inline-flex;padding:16px 36px;border-radius:18px;background:{acc}22;border:1px solid {acc}66;font-size:28px;color:#fff;font-weight:600;">{action}</div>
    </div>
    <div class="scene-label" style="position:absolute;top:24px;left:24px;font-size:14px;color:{acc};opacity:0.7;">{sid} · {role}</div>
"""


def _css_quote_close(sid: str, role: str, scene: dict[str, Any]) -> str:
    acc = _accent(role)
    return f"""
.{sid.lower()}-bg-grid {{ position:absolute; inset:0; pointer-events:none; background-image:linear-gradient({acc}06 1px,transparent 1px),linear-gradient(90deg,{acc}06 1px,transparent 1px); background-size:72px 72px; animation:grid-drift 18s linear infinite; }}
@keyframes grid-drift {{ 0%{{background-position:0 0;}} 100%{{background-position:72px 72px;}} }}
"""


def _gsap_quote_close(sid: str, role: str, scene: dict[str, Any], start: float, duration: float) -> str:
    return f"""
const tl_{sid}=gsap.timeline({{paused:true}});
window.__timelines['{sid}']=tl_{sid};
tl_{sid}.fromTo('[data-scene-id="{sid}"] [data-motion-target="scene-bg"] .bg-grid',{{opacity:0}},{{opacity:1,duration:0.8}},0);
"""


# ─────────────────────────────────────────────────────────────────
# P3.5 — 10 new seed renderers
# myth_bust / before_after_flash / timeline_pain / timeline_path /
# tool_stack / case_study / evidence_cards / score_panel /
# next_step_board / comment_invite
# All reuse existing HUD card / scanline / accent palette.
# ─────────────────────────────────────────────────────────────────

def _template_myth_bust(sid: str, role: str, scene: dict[str, Any]) -> str:
    acc = _accent(role)
    headline = scene.get("headline", scene.get("narration", "大部分人都搞错了")[:30] or "大部分人都搞错了")
    myth = scene.get("myth", "多装插件就能提高效率")
    truth = scene.get("truth", "先跑通最小闭环再说")
    # V3-P3.11C — alternate glass color so adjacent myth_bust scenes look different
    color_variant = scene.get("color_variant", "default")
    if color_variant == "alt":
        myth_color, x_color = "#FFC83D", "rgba(255,200,61,0.15)"
        truth_color, check_color = "#38E1FF", "rgba(56,225,255,0.15)"
    else:
        myth_color, x_color = "#FF5577", "rgba(255,85,119,0.15)"
        truth_color, check_color = "#2EE874", "rgba(46,232,116,0.15)"
    green = "#2EE874"
    return f"""
    <div data-motion-target="scene-bg" class="hf-bg-cinematic" style="position:absolute;inset:0;background:{_bg(role)};">
      <div class="bg-grid" style="opacity:.25"></div>
      <div class="bg-glow bg-glow-1" style="background:radial-gradient(circle,{acc}28 0%,transparent 70%);"></div>
    </div>
    <div class="hf-safe-zone" style="position:absolute;top:190px;left:72px;right:72px;">
      <div class="hf-status-stamp hf-status-risk hf-animate-stamp" style="display:inline-flex;margin-bottom:12px;font-size:16px;padding:8px 18px;">MYTH / BUST</div>
      <div class="hf-animate-title" style="font-size:52px;font-weight:900;color:#fff;line-height:1.1;">{headline}</div>
    </div>
    <!-- MYTH card -->
    <div class="hf-glass-panel hf-animate-card" style="position:absolute;top:430px;left:72px;width:936px;padding:28px 36px;text-align:left;border-color:{myth_color};background:{x_color};">
      <div style="display:flex;align-items:flex-start;gap:20px;">
        <div style="width:48px;height:48px;border-radius:50%;background:{myth_color}33;display:flex;align-items:center;justify-content:center;font-size:28px;flex-shrink:0;">✕</div>
        <div style="flex:1;">
          <div class="hf-mini-badge" style="background:{myth_color}33;color:{myth_color};margin-bottom:8px;">MYTH · 误区</div>
          <div style="font-size:40px;font-weight:800;color:rgba(255,255,255,0.5);text-decoration:line-through;line-height:1.2;">{myth}</div>
        </div>
      </div>
    </div>
    <!-- Transition block: MYTH → TRUTH -->
    <div style="position:absolute;top:680px;left:50%;transform:translateX(-50%);text-align:center;">
      <div class="hf-glow-divider" style="margin:0 auto 14px;"></div>
      <div style="display:inline-flex;align-items:center;gap:14px;padding:8px 24px;border-radius:999px;background:rgba(255,255,255,0.04);border:1px solid rgba(255,255,255,0.1);font-size:22px;color:rgba(255,255,255,0.55);letter-spacing:.04em;">
        <span style="color:{myth_color};">MYTH</span>
        <span style="font-size:18px;">→</span>
        <span style="color:{truth_color};">TRUTH</span>
      </div>
      <div style="font-size:24px;color:rgba(255,255,255,0.45);margin-top:4px;">真正的问题不是数量，而是结构</div>
    </div>
    <!-- TRUTH card -->
    <div class="hf-glass-panel hf-animate-card" style="position:absolute;top:820px;left:72px;width:936px;padding:28px 36px;text-align:left;border-color:{truth_color};background:{check_color};">
      <div style="display:flex;align-items:flex-start;gap:20px;">
        <div style="width:48px;height:48px;border-radius:50%;background:{truth_color}33;display:flex;align-items:center;justify-content:center;font-size:28px;flex-shrink:0;">✓</div>
        <div style="flex:1;">
          <div class="hf-mini-badge" style="background:{truth_color}33;color:{truth_color};margin-bottom:8px;">TRUTH · 真相</div>
          <div style="font-size:40px;font-weight:900;color:#fff;line-height:1.2;">{truth}</div>
        </div>
      </div>
    </div>
    <!-- Bottom conclusion -->
    <div class="hf-result-card hf-page-anchor" style="border-color:rgba(56,225,255,0.25);background:rgba(56,225,255,0.06);">
      <div class="hf-glow-divider"></div>
      <div style="font-size:26px;color:rgba(255,255,255,0.75);line-height:1.4;">真正要搭的是可调用的第二大脑</div>
    </div>
    <div class="scene-label" style="position:absolute;top:24px;left:24px;font-size:14px;color:{acc};opacity:0.7;">{sid} · {role}</div>
"""


def _css_myth_bust(sid: str, role: str, scene: dict[str, Any]) -> str:
    acc = _accent(role)
    return f"""
.{sid.lower()}-bg-grid {{ position:absolute; inset:0; pointer-events:none; background-image:linear-gradient({acc}06 1px,transparent 1px),linear-gradient(90deg,{acc}06 1px,transparent 1px); background-size:72px 72px; animation:grid-drift 18s linear infinite; }}
@keyframes grid-drift {{ 0%{{background-position:0 0;}} 100%{{background-position:72px 72px;}} }}
"""


def _gsap_myth_bust(sid: str, role: str, scene: dict[str, Any], start: float, duration: float) -> str:
    return f"""
const tl_{sid}=gsap.timeline({{paused:true}});
window.__timelines['{sid}']=tl_{sid};
tl_{sid}.fromTo('[data-scene-id="{sid}"] [data-motion-target="scene-bg"] .bg-grid',{{opacity:0}},{{opacity:1,duration:0.8}},0);
"""


def _template_before_after_flash(sid: str, role: str, scene: dict[str, Any]) -> str:
    acc = _accent(role)
    before_m = scene.get("before_metric", "5h")
    after_m = scene.get("after_metric", "40m")
    label = scene.get("metric_label", scene.get("narration", "找素材时间")[:30] or "找素材时间")
    return f"""
    <div data-motion-target="scene-bg" style="position:absolute;inset:0;background:linear-gradient(90deg,#1A0A0A 0%,#0A1628 50%,#082016 100%);">
      <div class="bg-grid"></div>
    </div>
    <div style="position:absolute;top:200px;left:0;right:0;text-align:center;">
      <div style="font-size:18px;letter-spacing:0.32em;color:rgba(255,255,255,0.55);margin-bottom:18px;">{label}</div>
      <div style="display:flex;align-items:center;justify-content:center;gap:40px;">
        <div style="text-align:center;">
            <div style="font-size:18px;letter-spacing:0.18em;color:#FF4757;margin-bottom:8px;">BEFORE</div>
            <div style="font-size:160px;font-weight:900;color:#FF4757;line-height:0.9;text-decoration:line-through;letter-spacing:-4px;text-shadow:0 0 32px rgba(255,71,87,0.5);">{before_m}</div>
        </div>
        <div style="font-size:120px;color:rgba(255,255,255,0.4);font-weight:900;">→</div>
        <div style="text-align:center;">
            <div style="font-size:18px;letter-spacing:0.18em;color:{acc};margin-bottom:8px;">AFTER</div>
            <div style="font-size:160px;font-weight:900;color:{acc};line-height:0.9;letter-spacing:-4px;text-shadow:0 0 48px {acc};">{after_m}</div>
        </div>
      </div>
    </div>
    <div style="position:absolute;top:1180px;left:0;right:0;text-align:center;">
      <div style="display:inline-flex;padding:18px 42px;border-radius:18px;background:{acc}22;border:2px solid {acc};font-size:32px;color:#fff;font-weight:700;letter-spacing:-0.4px;">同一个动作 · 完全不同的结果</div>
    </div>
    <div class="scene-label" style="position:absolute;top:24px;left:24px;font-size:14px;color:{acc};opacity:0.7;">{sid} · {role}</div>
"""


def _css_before_after_flash(sid: str, role: str, scene: dict[str, Any]) -> str:
    acc = _accent(role)
    return f"""
.{sid.lower()}-bg-grid {{ position:absolute; inset:0; pointer-events:none; background-image:linear-gradient({acc}06 1px,transparent 1px),linear-gradient(90deg,{acc}06 1px,transparent 1px); background-size:72px 72px; animation:grid-drift 18s linear infinite; }}
@keyframes grid-drift {{ 0%{{background-position:0 0;}} 100%{{background-position:72px 72px;}} }}
"""


def _gsap_before_after_flash(sid: str, role: str, scene: dict[str, Any], start: float, duration: float) -> str:
    return f"""
const tl_{sid}=gsap.timeline({{paused:true}});
window.__timelines['{sid}']=tl_{sid};
tl_{sid}.fromTo('[data-scene-id="{sid}"] [data-motion-target="scene-bg"] .bg-grid',{{opacity:0}},{{opacity:1,duration:0.8}},0);
"""


def _template_timeline_pain(sid: str, role: str, scene: dict[str, Any]) -> str:
    acc = _accent(role)
    headline = scene.get("headline", scene.get("narration", "三个月没整理的代价")[:30] or "三个月没整理的代价")
    events = scene.get("events", [
        {"week": "W1", "text": "笔记散 5 个 App", "severity": "LOW"},
        {"week": "W4", "text": "素材找不到", "severity": "MID"},
        {"week": "W8", "text": "怀疑记笔记的意义", "severity": "HIGH"},
        {"week": "W12", "text": "放弃，靠脑子", "severity": "CRIT"},
    ])
    severity_color = {"LOW": "#FBBF24", "MID": "#FF6B35", "HIGH": "#FF4757", "CRIT": "#FF0050"}
    event_htmls = []
    for idx, ev in enumerate(events):
        y = 480 + idx * 170
        sc = severity_color.get(ev.get("severity", "MID"), "#FF6B35")
        event_htmls.append(f"""
        <div class="tl-pain-event" style="position:absolute;top:{y}px;left:160px;width:760px;height:130px;background:rgba(255,255,255,0.05);border-left:6px solid {sc};border-radius:18px;padding:24px 28px;display:flex;align-items:center;gap:24px;box-shadow:0 0 24px {sc}22;">
            <div style="font-size:36px;font-weight:900;color:{sc};font-family:monospace;width:120px;flex-shrink:0;">{ev.get('week', '')}</div>
            <div style="flex:1;font-size:30px;font-weight:700;color:#fff;line-height:1.2;">{ev.get('text', '')}</div>
            <div style="padding:8px 18px;border-radius:10px;background:{sc}22;border:1px solid {sc}66;font-size:18px;color:{sc};font-weight:700;letter-spacing:0.1em;">{ev.get('severity', '')}</div>
        </div>
        """)
    conclusion = scene.get("conclusion", "信息过载不是记不住，是没结构")
    return f"""
    <div data-motion-target="scene-bg" style="position:absolute;inset:0;background:linear-gradient(180deg,#1A0A0A 0%,#0A1628 60%,#0A1628 100%);">
      <div class="bg-grid"></div>
    </div>
    <div style="position:absolute;top:200px;left:72px;right:72px;text-align:center;">
      <div style="display:inline-flex;padding:8px 20px;border-radius:999px;background:rgba(255,107,53,0.12);border:1px solid {acc}66;color:{acc};font-size:18px;letter-spacing:0.22em;margin-bottom:18px;">PAIN / TIMELINE</div>
      <div style="font-size:54px;font-weight:900;color:#fff;line-height:1.12;letter-spacing:-1.2px;">{headline}</div>
    </div>
    {''.join(event_htmls)}
    <div style="position:absolute;top:1200px;left:120px;right:120px;padding:18px 24px;border-top:1px solid rgba(255,255,255,0.18);text-align:center;font-size:26px;color:rgba(255,255,255,0.85);font-weight:700;">{conclusion}</div>
    <div class="scene-label" style="position:absolute;top:24px;left:24px;font-size:14px;color:{acc};opacity:0.7;">{sid} · {role}</div>
"""


def _css_timeline_pain(sid: str, role: str, scene: dict[str, Any]) -> str:
    acc = _accent(role)
    return f"""
.{sid.lower()}-bg-grid {{ position:absolute; inset:0; pointer-events:none; background-image:linear-gradient({acc}06 1px,transparent 1px),linear-gradient(90deg,{acc}06 1px,transparent 1px); background-size:72px 72px; animation:grid-drift 18s linear infinite; }}
@keyframes grid-drift {{ 0%{{background-position:0 0;}} 100%{{background-position:72px 72px;}} }}
"""


def _gsap_timeline_pain(sid: str, role: str, scene: dict[str, Any], start: float, duration: float) -> str:
    return f"""
const tl_{sid}=gsap.timeline({{paused:true}});
window.__timelines['{sid}']=tl_{sid};
tl_{sid}.fromTo('[data-scene-id="{sid}"] .tl-pain-event',{{x:60,opacity:0}},{{x:0,opacity:1,duration:0.5,stagger:0.15,ease:'power2.out'}},0);
"""


def _template_timeline_path(sid: str, role: str, scene: dict[str, Any]) -> str:
    acc = _accent(role)
    headline = scene.get("headline", scene.get("narration", "90 天建立第二大脑")[:30] or "90 天建立第二大脑")
    milestones = scene.get("milestones", [
        {"week": "W1-W2", "text": "统一入口"},
        {"week": "W3-W4", "text": "建结构"},
        {"week": "W5-W8", "text": "跑通检索"},
        {"week": "W9-W12", "text": "持续输出"},
    ])
    top_label = scene.get("top_label", "ROADMAP")
    milestone_htmls = []
    for idx, m in enumerate(milestones):
        x = 72 + idx * 248
        milestone_htmls.append(f"""
        <div class="tl-milestone" style="position:absolute;top:680px;left:{x}px;width:220px;height:300px;background:linear-gradient(180deg,rgba(77,159,255,0.12),rgba(255,255,255,0.04));border:2px solid {acc};border-radius:22px;padding:20px 18px;box-shadow:0 0 24px {acc}22;">
            <div style="font-size:18px;letter-spacing:0.18em;color:{acc};margin-bottom:10px;font-family:monospace;">{m.get('week', '')}</div>
            <div style="font-size:34px;font-weight:900;color:#fff;line-height:1.18;">{m.get('text', '')}</div>
        </div>
        """)
    return f"""
    <div data-motion-target="scene-bg" style="position:absolute;inset:0;background:linear-gradient(180deg,#0A1628 0%,#0A1A28 60%,#082016 100%);">
      <div class="bg-grid"></div>
    </div>
    <div style="position:absolute;top:220px;left:0;right:0;text-align:center;">
      <div style="font-size:18px;letter-spacing:0.32em;color:{acc};margin-bottom:14px;">{top_label}</div>
      <div style="font-size:54px;font-weight:900;color:#fff;line-height:1.12;letter-spacing:-1.2px;">{headline}</div>
    </div>
    <div style="position:absolute;top:560px;left:72px;right:72px;height:6px;background:linear-gradient(90deg,{acc},#2ED573);border-radius:999px;box-shadow:0 0 24px {acc};"></div>
    {''.join(milestone_htmls)}
    <div class="scene-label" style="position:absolute;top:24px;left:24px;font-size:14px;color:{acc};opacity:0.7;">{sid} · {role}</div>
"""


def _css_timeline_path(sid: str, role: str, scene: dict[str, Any]) -> str:
    acc = _accent(role)
    return f"""
.{sid.lower()}-bg-grid {{ position:absolute; inset:0; pointer-events:none; background-image:linear-gradient({acc}06 1px,transparent 1px),linear-gradient(90deg,{acc}06 1px,transparent 1px); background-size:72px 72px; animation:grid-drift 18s linear infinite; }}
@keyframes grid-drift {{ 0%{{background-position:0 0;}} 100%{{background-position:72px 72px;}} }}
"""


def _gsap_timeline_path(sid: str, role: str, scene: dict[str, Any], start: float, duration: float) -> str:
    return f"""
const tl_{sid}=gsap.timeline({{paused:true}});
window.__timelines['{sid}']=tl_{sid};
tl_{sid}.fromTo('[data-scene-id="{sid}"] .tl-milestone',{{y:60,opacity:0}},{{y:0,opacity:1,duration:0.5,stagger:0.2,ease:'back.out(1.1)'}},0);
"""


def _template_tool_stack(sid: str, role: str, scene: dict[str, Any]) -> str:
    acc = _accent(role)
    headline = scene.get("headline", scene.get("narration", "三件套搭起来")[:30] or "三件套搭起来")
    stack = scene.get("stack_layers", [
        {"name": "Obsidian", "role": "存储", "color": "#7C3AED"},
        {"name": "Codex", "role": "整理", "color": "#4D9FFF"},
        {"name": "Hermes", "role": "复盘", "color": "#2ED573"},
    ])
    # V3-P3.11E — 3-layer pipeline: L1 left, L2 center, L3 right with flow arrows
    layer_data_list = [
        {"pos": "left:60px;",  "tag": "采集 / INPUT",     "tag_color": "#38E1FF"},
        {"pos": "left:180px;", "tag": "整理 / STRUCTURE",  "tag_color": "#C77DFF"},
        {"pos": "left:300px;", "tag": "输出 / OUTPUT",     "tag_color": "#2EE874"},
    ]
    layer_htmls = []
    for idx, (s, ld) in enumerate(zip(stack, layer_data_list)):
        y = 420 + idx * 230
        c = s.get("color", ld["tag_color"])
        # Flow arrow between layers
        arrow = ""
        if idx < len(stack) - 1:
            arrow = f"""
            <div class="hf-flow-line" style="top:{y + 160}px;height:70px;"></div>
            <div style="position:absolute;top:{y + 220}px;left:50%;width:0;height:0;
                border-left:10px solid transparent;border-right:10px solid transparent;
                border-top:12px solid rgba(56,225,255,0.35);transform:translateX(-50%);"></div>
            """
        layer_htmls.append(f"""
        {arrow}
        <div class="stack-layer hf-glass-panel hf-animate-card" style="position:absolute;top:{y}px;{ld['pos']}width:720px;height:160px;padding:24px 32px;display:flex;align-items:center;gap:24px;
            background:linear-gradient(135deg,{c}33,rgba(2,4,12,0.62) 70%);
            border-left:4px solid {ld['tag_color']};box-shadow:0 0 30px {ld['tag_color']}22;">
            <div style="width:64px;height:64px;border-radius:14px;background:{c};display:flex;align-items:center;justify-content:center;font-size:28px;font-weight:900;color:#0A1428;flex-shrink:0;box-shadow:0 0 20px {c}66;">L{idx+1}</div>
            <div style="flex:1;">
                <div class="hf-mini-badge" style="background:{ld['tag_color']}22;color:{ld['tag_color']};margin-bottom:6px;">{ld['tag']}</div>
                <div style="font-size:36px;font-weight:800;color:#fff;line-height:1.15;">{s.get('name', '')}</div>
                <div style="font-size:22px;color:rgba(255,255,255,0.6);margin-top:4px;">{s.get('role', '')}</div>
            </div>
            <div style="font-size:16px;color:rgba(255,255,255,0.3);font-family:monospace;letter-spacing:0.1em;margin-top:auto;align-self:flex-end;">{idx+1}/3</div>
        </div>
        """)
    return f"""
    <div data-motion-target="scene-bg" class="hf-bg-cinematic" style="position:absolute;inset:0;background:{_bg(role)};">
      <div class="bg-grid" style="opacity:.25"></div>
      <div class="bg-glow bg-glow-1" style="background:radial-gradient(circle,{acc}28 0%,transparent 70%);"></div>
    </div>
    <div class="hf-safe-zone" style="position:absolute;top:220px;left:72px;right:72px;">
      <div class="hf-status-stamp hf-status-live hf-animate-stamp" style="display:inline-flex;margin-bottom:12px;font-size:16px;padding:8px 18px;">TOOL / STACK</div>
      <div class="hf-animate-title" style="font-size:52px;font-weight:900;color:#fff;line-height:1.12;">{headline}</div>
    </div>
    {''.join(layer_htmls)}
    <!-- V3-P3.11E — result anchor card -->
    <div class="hf-result-card hf-page-anchor" style="border-color:rgba(255,200,61,0.3);background:rgba(255,200,61,0.08);">
      <div class="hf-glow-divider"></div>
      <span class="hf-mini-badge" style="background:rgba(255,200,61,0.2);color:#FFC83D;margin-bottom:10px;">RESULT</span>
      <div style="font-size:24px;color:rgba(255,255,255,0.7);line-height:1.4;max-width:600px;margin:0 auto;">从分散工具变成可调用系统</div>
    </div>
    <div class="scene-label" style="position:absolute;top:24px;left:24px;font-size:14px;color:{acc};opacity:0.7;">{sid} · {role}</div>
"""


def _css_tool_stack(sid: str, role: str, scene: dict[str, Any]) -> str:
    acc = _accent(role)
    return f"""
.{sid.lower()}-bg-grid {{ position:absolute; inset:0; pointer-events:none; background-image:linear-gradient({acc}06 1px,transparent 1px),linear-gradient(90deg,{acc}06 1px,transparent 1px); background-size:72px 72px; animation:grid-drift 18s linear infinite; }}
@keyframes grid-drift {{ 0%{{background-position:0 0;}} 100%{{background-position:72px 72px;}} }}
"""


def _gsap_tool_stack(sid: str, role: str, scene: dict[str, Any], start: float, duration: float) -> str:
    return f"""
const tl_{sid}=gsap.timeline({{paused:true}});
window.__timelines['{sid}']=tl_{sid};
tl_{sid}.fromTo('[data-scene-id="{sid}"] .stack-layer',{{y:60,opacity:0}},{{y:0,opacity:1,duration:0.5,stagger:0.18,ease:'power2.out'}},0);
"""


def _template_case_study(sid: str, role: str, scene: dict[str, Any]) -> str:
    acc = _accent(role)
    headline = scene.get("headline", scene.get("narration", "真实案例")[:30] or "真实案例")
    case_label = scene.get("case_label", "李同学 / 设计师 / 自由职业")
    metrics = scene.get("metrics", [
        {"label": "整理耗时", "value": "-75%"},
        {"label": "素材复用", "value": "3.4×"},
        {"label": "完稿速度", "value": "+200%"},
    ])
    outcome = scene.get("outcome", "从 1 篇/周到 3 篇/周，质量反而更稳")
    metrics_html = "".join(
        f"""
        <div class="cs-metric" style="flex:1;background:rgba(77,159,255,0.10);border:2px solid {acc};border-radius:18px;padding:20px 16px;text-align:center;box-shadow:0 0 20px {acc}22;">
            <div style="font-size:18px;letter-spacing:0.14em;color:rgba(255,255,255,0.6);margin-bottom:8px;">{m.get('label', '')}</div>
            <div style="font-size:48px;font-weight:900;color:{acc};letter-spacing:-1px;line-height:1;">{m.get('value', '')}</div>
        </div>
        """
        for m in metrics
    )
    return f"""
    <div data-motion-target="scene-bg" style="position:absolute;inset:0;background:linear-gradient(180deg,#0A1628 0%,#0A1A28 60%,#101B32 100%);">
      <div class="bg-grid"></div>
    </div>
    <div style="position:absolute;top:220px;left:72px;right:72px;text-align:center;">
      <div style="display:inline-flex;padding:8px 20px;border-radius:999px;background:rgba(77,159,255,0.12);border:1px solid {acc}66;color:{acc};font-size:18px;letter-spacing:0.22em;margin-bottom:14px;">CASE / STUDY</div>
      <div style="font-size:54px;font-weight:900;color:#fff;line-height:1.12;letter-spacing:-1.2px;">{headline}</div>
      <div style="font-size:22px;color:rgba(255,255,255,0.7);margin-top:8px;">{case_label}</div>
    </div>
    <div style="position:absolute;top:540px;left:72px;right:72px;display:flex;gap:18px;">
        {metrics_html}
    </div>
    <div style="position:absolute;top:880px;left:120px;right:120px;padding:24px 28px;border:1px solid rgba(77,159,255,0.32);border-radius:22px;background:rgba(77,159,255,0.08);text-align:center;">
        <div style="font-size:18px;letter-spacing:0.18em;color:rgba(255,255,255,0.65);margin-bottom:8px;">OUTCOME / 结果</div>
        <div style="font-size:32px;font-weight:800;color:#fff;line-height:1.32;">{outcome}</div>
    </div>
    <div class="scene-label" style="position:absolute;top:24px;left:24px;font-size:14px;color:{acc};opacity:0.7;">{sid} · {role}</div>
"""


def _css_case_study(sid: str, role: str, scene: dict[str, Any]) -> str:
    acc = _accent(role)
    return f"""
.{sid.lower()}-bg-grid {{ position:absolute; inset:0; pointer-events:none; background-image:linear-gradient({acc}06 1px,transparent 1px),linear-gradient(90deg,{acc}06 1px,transparent 1px); background-size:72px 72px; animation:grid-drift 18s linear infinite; }}
@keyframes grid-drift {{ 0%{{background-position:0 0;}} 100%{{background-position:72px 72px;}} }}
"""


def _gsap_case_study(sid: str, role: str, scene: dict[str, Any], start: float, duration: float) -> str:
    return f"""
const tl_{sid}=gsap.timeline({{paused:true}});
window.__timelines['{sid}']=tl_{sid};
tl_{sid}.fromTo('[data-scene-id="{sid}"] .cs-metric',{{y:50,opacity:0}},{{y:0,opacity:1,duration:0.5,stagger:0.15,ease:'back.out(1.2)'}},0);
"""


def _template_evidence_cards(sid: str, role: str, scene: dict[str, Any]) -> str:
    acc = _accent(role)
    headline = scene.get("headline", scene.get("narration", "四项独立证据")[:30] or "四项独立证据")
    cards = scene.get("cards", [
        {"label": "测试 1", "text": "素材利用率 ↑ 78%"},
        {"label": "测试 2", "text": "完播率 ↑ 61%"},
        {"label": "测试 3", "text": "复盘耗时 ↓ 65%"},
        {"label": "测试 4", "text": "草稿接受率 80%"},
    ])
    caption = scene.get("caption", "三个独立测试都指向同一结论")
    positions = [(72, 480), (548, 480), (72, 880), (548, 880)]
    card_htmls = []
    for idx, (c, (x, y)) in enumerate(zip(cards, positions)):
        card_htmls.append(f"""
        <div class="ev-card" style="position:absolute;top:{y}px;left:{x}px;width:444px;height:330px;background:linear-gradient(180deg,rgba(46,213,115,0.10),rgba(255,255,255,0.04));border:2px solid {acc};border-radius:24px;padding:30px 28px;box-shadow:0 0 26px {acc}22;">
            <div style="font-size:18px;letter-spacing:0.18em;color:{acc};margin-bottom:14px;">{c.get('label', '')}</div>
            <div style="font-size:42px;font-weight:900;color:#fff;line-height:1.18;letter-spacing:-0.6px;">{c.get('text', '')}</div>
        </div>
        """)
    return f"""
    <div data-motion-target="scene-bg" style="position:absolute;inset:0;background:linear-gradient(180deg,#0A1628 0%,#0A1A28 60%,#082016 100%);">
      <div class="bg-grid"></div>
    </div>
    <div style="position:absolute;top:200px;left:72px;right:72px;text-align:center;">
      <div style="display:inline-flex;padding:8px 20px;border-radius:999px;background:rgba(46,213,115,0.12);border:1px solid {acc}66;color:{acc};font-size:18px;letter-spacing:0.22em;margin-bottom:18px;">EVIDENCE / CARDS</div>
      <div style="font-size:54px;font-weight:900;color:#fff;line-height:1.12;letter-spacing:-1.2px;">{headline}</div>
    </div>
    {''.join(card_htmls)}
    <div style="position:absolute;top:1280px;left:140px;right:140px;padding:18px 24px;border-top:1px solid rgba(255,255,255,0.18);text-align:center;font-size:24px;color:rgba(255,255,255,0.7);">{caption}</div>
    <div class="scene-label" style="position:absolute;top:24px;left:24px;font-size:14px;color:{acc};opacity:0.7;">{sid} · {role}</div>
"""


def _css_evidence_cards(sid: str, role: str, scene: dict[str, Any]) -> str:
    acc = _accent(role)
    return f"""
.{sid.lower()}-bg-grid {{ position:absolute; inset:0; pointer-events:none; background-image:linear-gradient({acc}06 1px,transparent 1px),linear-gradient(90deg,{acc}06 1px,transparent 1px); background-size:72px 72px; animation:grid-drift 18s linear infinite; }}
@keyframes grid-drift {{ 0%{{background-position:0 0;}} 100%{{background-position:72px 72px;}} }}
"""


def _gsap_evidence_cards(sid: str, role: str, scene: dict[str, Any], start: float, duration: float) -> str:
    return f"""
const tl_{sid}=gsap.timeline({{paused:true}});
window.__timelines['{sid}']=tl_{sid};
tl_{sid}.fromTo('[data-scene-id="{sid}"] .ev-card',{{scale:0.85,opacity:0}},{{scale:1,opacity:1,duration:0.5,stagger:0.15,ease:'back.out(1.15)'}},0);
"""


def _template_score_panel(sid: str, role: str, scene: dict[str, Any]) -> str:
    acc = _accent(role)
    headline = scene.get("headline", scene.get("narration", "这一轮的得分")[:30] or "这一轮的得分")
    criteria = scene.get("criteria", [
        {"name": "内容", "score": 9, "max": 10},
        {"name": "节奏", "score": 8, "max": 10},
        {"name": "结构", "score": 9, "max": 10},
        {"name": "互动", "score": 7, "max": 10},
    ])
    verdict = scene.get("verdict", "PASS / 已可发布")
    row_htmls = []
    for idx, c in enumerate(criteria):
        y = 500 + idx * 130
        pct = c.get("score", 0) / max(c.get("max", 1), 1)
        bar_w = int(700 * pct)
        row_htmls.append(f"""
        <div class="score-row" style="position:absolute;top:{y}px;left:160px;width:760px;height:90px;background:rgba(255,255,255,0.05);border-radius:16px;padding:16px 24px;display:flex;align-items:center;gap:24px;">
            <div style="font-size:28px;font-weight:700;color:#fff;width:100px;flex-shrink:0;">{c.get('name', '')}</div>
            <div style="flex:1;height:24px;background:rgba(255,255,255,0.08);border-radius:12px;overflow:hidden;position:relative;">
                <div class="score-bar" style="position:absolute;left:0;top:0;bottom:0;width:{bar_w}px;background:linear-gradient(90deg,{acc},#2ED573);border-radius:12px;box-shadow:0 0 12px {acc}66;"></div>
            </div>
            <div style="font-size:32px;font-weight:900;color:{acc};width:80px;text-align:right;flex-shrink:0;">{c.get('score', 0)}<span style="font-size:18px;color:rgba(255,255,255,0.4);">/{c.get('max', 10)}</span></div>
        </div>
        """)
    return f"""
    <div data-motion-target="scene-bg" style="position:absolute;inset:0;background:linear-gradient(180deg,#0A1628 0%,#082016 60%,#0A1628 100%);">
      <div class="bg-grid"></div>
    </div>
    <div style="position:absolute;top:220px;left:72px;right:72px;text-align:center;">
      <div style="display:inline-flex;padding:8px 20px;border-radius:999px;background:rgba(52,211,153,0.12);border:1px solid {acc}66;color:{acc};font-size:18px;letter-spacing:0.22em;margin-bottom:18px;">SCORE / PANEL</div>
      <div style="font-size:54px;font-weight:900;color:#fff;line-height:1.12;letter-spacing:-1.2px;">{headline}</div>
    </div>
    {''.join(row_htmls)}
    <div style="position:absolute;top:1100px;left:0;right:0;text-align:center;">
        <div style="display:inline-flex;padding:18px 42px;border-radius:18px;background:{acc};color:#082016;font-size:36px;font-weight:900;letter-spacing:-0.4px;box-shadow:0 0 40px {acc}66;">{verdict}</div>
    </div>
    <div class="scene-label" style="position:absolute;top:24px;left:24px;font-size:14px;color:{acc};opacity:0.7;">{sid} · {role}</div>
"""


def _css_score_panel(sid: str, role: str, scene: dict[str, Any]) -> str:
    acc = _accent(role)
    return f"""
.{sid.lower()}-bg-grid {{ position:absolute; inset:0; pointer-events:none; background-image:linear-gradient({acc}06 1px,transparent 1px),linear-gradient(90deg,{acc}06 1px,transparent 1px); background-size:72px 72px; animation:grid-drift 18s linear infinite; }}
@keyframes grid-drift {{ 0%{{background-position:0 0;}} 100%{{background-position:72px 72px;}} }}
"""


def _gsap_score_panel(sid: str, role: str, scene: dict[str, Any], start: float, duration: float) -> str:
    return f"""
const tl_{sid}=gsap.timeline({{paused:true}});
window.__timelines['{sid}']=tl_{sid};
tl_{sid}.fromTo('[data-scene-id="{sid}"] .score-bar',{{scaleX:0,transformOrigin:'left center'}},{{scaleX:1,duration:0.9,stagger:0.18,ease:'power2.out'}},0);
"""


def _template_next_step_board(sid: str, role: str, scene: dict[str, Any]) -> str:
    acc = _accent(role)
    headline = scene.get("headline", scene.get("narration", "下一步你做哪一步？")[:30] or "下一步你做哪一步？")
    next_steps = scene.get("next_steps", [
        {"label": "1", "text": "选一个入口 App"},
        {"label": "2", "text": "把 10 条素材搬进去"},
        {"label": "3", "text": "建立 3 个主题页"},
        {"label": "4", "text": "问 AI 一个真实问题"},
    ])
    step_htmls = []
    for idx, s in enumerate(next_steps):
        y = 500 + idx * 180
        step_htmls.append(f"""
        <div class="next-step-row" style="position:absolute;top:{y}px;left:160px;width:760px;height:140px;background:linear-gradient(90deg,rgba(255,107,53,0.10),rgba(255,255,255,0.04));border:2px solid {acc};border-radius:22px;padding:20px 28px;display:flex;align-items:center;gap:24px;box-shadow:0 0 22px {acc}22;">
            <div style="width:90px;height:90px;border-radius:50%;background:{acc};display:flex;align-items:center;justify-content:center;font-size:44px;font-weight:900;color:#0A1428;flex-shrink:0;">{s.get('label', '')}</div>
            <div style="flex:1;font-size:32px;font-weight:700;color:#fff;line-height:1.2;">{s.get('text', '')}</div>
        </div>
        """)
    return f"""
    <div data-motion-target="scene-bg" style="position:absolute;inset:0;background:linear-gradient(180deg,#0A1628 0%,#1A0A0A 60%,#0A1628 100%);">
      <div class="bg-grid"></div>
    </div>
    <div style="position:absolute;top:220px;left:72px;right:72px;text-align:center;">
      <div style="display:inline-flex;padding:8px 20px;border-radius:999px;background:rgba(255,107,53,0.12);border:1px solid {acc}66;color:{acc};font-size:18px;letter-spacing:0.22em;margin-bottom:18px;">NEXT / STEP</div>
      <div style="font-size:54px;font-weight:900;color:#fff;line-height:1.12;letter-spacing:-1.2px;">{headline}</div>
    </div>
    {''.join(step_htmls)}
    <div class="scene-label" style="position:absolute;top:24px;left:24px;font-size:14px;color:{acc};opacity:0.7;">{sid} · {role}</div>
"""


def _css_next_step_board(sid: str, role: str, scene: dict[str, Any]) -> str:
    acc = _accent(role)
    return f"""
.{sid.lower()}-bg-grid {{ position:absolute; inset:0; pointer-events:none; background-image:linear-gradient({acc}06 1px,transparent 1px),linear-gradient(90deg,{acc}06 1px,transparent 1px); background-size:72px 72px; animation:grid-drift 18s linear infinite; }}
@keyframes grid-drift {{ 0%{{background-position:0 0;}} 100%{{background-position:72px 72px;}} }}
"""


def _gsap_next_step_board(sid: str, role: str, scene: dict[str, Any], start: float, duration: float) -> str:
    return f"""
const tl_{sid}=gsap.timeline({{paused:true}});
window.__timelines['{sid}']=tl_{sid};
tl_{sid}.fromTo('[data-scene-id="{sid}"] .next-step-row',{{x:-60,opacity:0}},{{x:0,opacity:1,duration:0.5,stagger:0.2,ease:'back.out(1.2)'}},0);
"""


def _template_comment_invite(sid: str, role: str, scene: dict[str, Any]) -> str:
    acc = _accent(role)
    headline = scene.get("headline", scene.get("narration", "评论区告诉我")[:30] or "评论区告诉我")
    question = scene.get("question", "你愿意先只保留一个入口吗？")
    action = scene.get("action", "评论 / 点赞 / 收藏 / 转发")
    return f"""
    <div data-motion-target="scene-bg" style="position:absolute;inset:0;background:linear-gradient(180deg,#1A0A0A 0%,#0A1628 60%,#0A1628 100%);">
      <div class="bg-grid"></div>
      <div class="bg-glow bg-glow-1" style="background:radial-gradient(circle,{acc}22 0%,transparent 70%);"></div>
    </div>
    <div style="position:absolute;top:280px;left:0;right:0;text-align:center;">
      <div style="display:inline-flex;padding:8px 20px;border-radius:999px;background:rgba(255,71,87,0.12);border:1px solid {acc}66;color:{acc};font-size:18px;letter-spacing:0.22em;margin-bottom:18px;">COMMENT / INVITE</div>
      <div style="font-size:64px;font-weight:900;color:#fff;line-height:1.1;letter-spacing:-1.4px;">{headline}</div>
    </div>
    <div style="position:absolute;top:600px;left:120px;right:120px;background:linear-gradient(135deg,rgba(255,71,87,0.18),rgba(255,107,53,0.10));border:2px solid {acc};border-radius:28px;padding:50px 40px;text-align:center;box-shadow:0 0 48px {acc}22;">
        <div style="font-size:22px;letter-spacing:0.18em;color:rgba(255,255,255,0.6);margin-bottom:14px;">QUESTION / 引导</div>
        <div style="font-size:48px;font-weight:900;color:#fff;line-height:1.25;letter-spacing:-0.8px;">{question}</div>
    </div>
    <div style="position:absolute;top:1180px;left:0;right:0;text-align:center;">
        <div style="display:inline-flex;padding:18px 42px;border-radius:18px;background:rgba(255,255,255,0.06);border:1px solid rgba(255,255,255,0.16);font-size:28px;color:#fff;font-weight:600;letter-spacing:0.1em;">{action}</div>
    </div>
    <div class="scene-label" style="position:absolute;top:24px;left:24px;font-size:14px;color:{acc};opacity:0.7;">{sid} · {role}</div>
"""


def _css_comment_invite(sid: str, role: str, scene: dict[str, Any]) -> str:
    acc = _accent(role)
    return f"""
.{sid.lower()}-bg-grid {{ position:absolute; inset:0; pointer-events:none; background-image:linear-gradient({acc}06 1px,transparent 1px),linear-gradient(90deg,{acc}06 1px,transparent 1px); background-size:72px 72px; animation:grid-drift 18s linear infinite; }}
@keyframes grid-drift {{ 0%{{background-position:0 0;}} 100%{{background-position:72px 72px;}} }}
"""


def _gsap_comment_invite(sid: str, role: str, scene: dict[str, Any], start: float, duration: float) -> str:
    return f"""
const tl_{sid}=gsap.timeline({{paused:true}});
window.__timelines['{sid}']=tl_{sid};
tl_{sid}.fromTo('[data-scene-id="{sid}"] [data-motion-target="scene-bg"] .bg-grid',{{opacity:0}},{{opacity:1,duration:0.8}},0);
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
    "framework_quadrant": _template_framework_quadrant,
    "decision_tree": _template_decision_tree,
    "metric_dashboard": _template_metric_dashboard,
    "case_study_card": _template_case_study_card,
    "section_board": _template_section_board,
    "comment_question": _template_comment_question,
    "countdown_strike": _template_countdown_strike,
    "keyword_punchline": _template_keyword_punchline,
    "data_dense_table": _template_data_dense_table,
    "step_ladder": _template_step_ladder,
    "concept_layers": _template_concept_layers,
    "progress_tracker": _template_progress_tracker,
    "knowledge_graph": _template_knowledge_graph,
    "quote_close": _template_quote_close,
    "myth_bust": _template_myth_bust,
    "before_after_flash": _template_before_after_flash,
    "timeline_pain": _template_timeline_pain,
    "timeline_path": _template_timeline_path,
    "tool_stack": _template_tool_stack,
    "case_study": _template_case_study,
    "evidence_cards": _template_evidence_cards,
    "score_panel": _template_score_panel,
    "next_step_board": _template_next_step_board,
    "comment_invite": _template_comment_invite,
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
    "framework_quadrant": _css_framework_quadrant,
    "decision_tree": _css_decision_tree,
    "metric_dashboard": _css_metric_dashboard,
    "case_study_card": _css_case_study_card,
    "section_board": _css_section_board,
    "comment_question": _css_comment_question,
    "countdown_strike": _css_countdown_strike,
    "keyword_punchline": _css_keyword_punchline,
    "data_dense_table": _css_data_dense_table,
    "step_ladder": _css_step_ladder,
    "concept_layers": _css_concept_layers,
    "progress_tracker": _css_progress_tracker,
    "knowledge_graph": _css_knowledge_graph,
    "quote_close": _css_quote_close,
    "myth_bust": _css_myth_bust,
    "before_after_flash": _css_before_after_flash,
    "timeline_pain": _css_timeline_pain,
    "timeline_path": _css_timeline_path,
    "tool_stack": _css_tool_stack,
    "case_study": _css_case_study,
    "evidence_cards": _css_evidence_cards,
    "score_panel": _css_score_panel,
    "next_step_board": _css_next_step_board,
    "comment_invite": _css_comment_invite,
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
    "framework_quadrant": _gsap_framework_quadrant,
    "decision_tree": _gsap_decision_tree,
    "metric_dashboard": _gsap_metric_dashboard,
    "case_study_card": _gsap_case_study_card,
    "section_board": _gsap_section_board,
    "comment_question": _gsap_comment_question,
    "countdown_strike": _gsap_countdown_strike,
    "keyword_punchline": _gsap_keyword_punchline,
    "data_dense_table": _gsap_data_dense_table,
    "step_ladder": _gsap_step_ladder,
    "concept_layers": _gsap_concept_layers,
    "progress_tracker": _gsap_progress_tracker,
    "knowledge_graph": _gsap_knowledge_graph,
    "quote_close": _gsap_quote_close,
    "myth_bust": _gsap_myth_bust,
    "before_after_flash": _gsap_before_after_flash,
    "timeline_pain": _gsap_timeline_pain,
    "timeline_path": _gsap_timeline_path,
    "tool_stack": _gsap_tool_stack,
    "case_study": _gsap_case_study,
    "evidence_cards": _gsap_evidence_cards,
    "score_panel": _gsap_score_panel,
    "next_step_board": _gsap_next_step_board,
    "comment_invite": _gsap_comment_invite,
    "hook_centered": _gsap_fallback,
    "pain_centered": _gsap_fallback,
    "method_centered": _gsap_fallback,
    "evidence_centered": _gsap_fallback,
    "proof_centered": _gsap_fallback,
    "cta_centered": _gsap_fallback,
}
