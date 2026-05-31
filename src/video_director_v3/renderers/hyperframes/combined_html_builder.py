#!/usr/bin/env python3
"""Combined HTML Builder — V3 migrated from V2."""
from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any


def build_combined_html(
    project_dir: Path,
    storyboard: dict[str, Any],
    tts_result: dict[str, Any] | None = None,
    caption_beats: dict[str, Any] | None = None,
    semantic_transitions: dict[str, Any] | None = None,
    duration_contract: Any | None = None,
) -> dict[str, Any]:
    """Build combined/index.html from storyboard."""
    # Import here to avoid circular dependency
    from video_director_v3.renderers.hyperframes.publish_templates import (
        get_scene_body, get_scene_css, get_scene_gsap,
    )
    project_id = storyboard.get("project", {}).get("project_id", "unknown")
    scenes = storyboard.get("scenes", [])

    # Calculate total duration
    total_duration = float(storyboard.get("project", {}).get("duration", 40.0))
    audio_tl_path = project_dir / "audio_timeline.json"
    if audio_tl_path.exists():
        audio_tl = json.loads(audio_tl_path.read_text(encoding="utf-8"))
        if audio_tl.get("total_duration"):
            total_duration = float(audio_tl["total_duration"])

    # Load scenes with layout info
    scene_parts = []
    for scene in scenes:
        sid = scene.get("scene_id", "S01")
        role = scene.get("role", "")
        start = float(scene.get("start", 0))
        duration = float(scene.get("duration", 5.0))
        layout = scene.get("layout_type", f"{role}_centered")

        # Generate scene body/CSS/GSAP using publish_templates
        body_content = get_scene_body(sid, role, scene)
        scene_css = get_scene_css(sid, role, scene)
        scene_gsap = get_scene_gsap(sid, role, scene, start, duration)

        scene_parts.append({
            "scene_id": sid,
            "role": role,
            "start": start,
            "duration": duration,
            "body": body_content,
            "layout": layout,
            "components": scene.get("components", []),
            "css": scene_css,
            "gsap": scene_gsap,
        })

    # Resolve audio
    audio_src = None
    audio_duration = None
    if tts_result and tts_result.get("audio_path"):
        audio_path = Path(tts_result["audio_path"])
        if audio_path.exists():
            assets_dir = project_dir / "combined" / "assets"
            assets_dir.mkdir(parents=True, exist_ok=True)
            dest = assets_dir / "voiceover.mp3"
            import shutil
            shutil.copyfile(audio_path, dest)
            audio_src = "./assets/voiceover.mp3"
            audio_duration = tts_result.get("real_duration")

    # Load semantic transitions
    st_data = semantic_transitions or {}
    if not st_data:
        st_path = project_dir / "semantic_transitions.json"
        if st_path.exists():
            st_data = json.loads(st_path.read_text(encoding="utf-8"))

    # Build HTML
    html = _build_combined_html(
        project_id=project_id,
        scenes=scene_parts,
        total_duration=total_duration,
        audio_src=audio_src,
        caption_beats=caption_beats,
        semantic_transitions=st_data,
    )

    # Write combined/index.html
    combined_dir = project_dir / "combined"
    combined_dir.mkdir(parents=True, exist_ok=True)
    index_path = combined_dir / "index.html"
    index_path.write_text(html, encoding="utf-8")

    # Copy audio to assets
    if audio_src and tts_result and tts_result.get("audio_path"):
        assets_dir = project_dir / "combined" / "assets"
        assets_dir.mkdir(parents=True, exist_ok=True)
        src_audio = Path(tts_result["audio_path"])
        if src_audio.exists():
            import shutil
            shutil.copyfile(src_audio, assets_dir / "voiceover.mp3")

    # Write manifest
    manifest = {
        "version": "V3",
        "project_id": project_id,
        "html_path": str(index_path),
        "total_duration": total_duration,
        "scene_count": len(scenes),
        "audio_duration": audio_duration,
        "audio_status": "ok" if audio_src else "no_audio",
        "scenes": [
            {
                "scene_id": s["scene_id"],
                "role": s.get("role", ""),
                "start": s["start"],
                "duration": s["duration"],
            }
            for s in scene_parts
        ],
    }
    (combined_dir / "combined_manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )

    # Write runtime report
    report = {
        "version": "V3",
        "total_duration": total_duration,
        "scene_count": len(scene_parts),
        "scene_body_inserted_count": sum(1 for s in scene_parts if s.get("body", "").strip()),
    }
    (combined_dir / "combined_runtime_report.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )

    return manifest


def _generate_scene_body(sid: str, role: str, scene: dict[str, Any]) -> str:
    """Generate scene body HTML based on role."""
    narration = scene.get("narration", "")
    headline = narration[:30] if narration else f"Scene {sid}"

    bg_colors = {
        "hook": "#0A1628",
        "pain": "#1A0A0A",
        "method": "#0A1A28",
        "evidence": "#0A1428",
        "proof": "#0A1A28",
        "cta": "#0A2818",
    }
    bg = bg_colors.get(role, "#050814")

    accent_colors = {
        "hook": "#FF4757",
        "pain": "#FF6B35",
        "method": "#2ED573",
        "evidence": "#4D9FFF",
        "proof": "#4D9FFF",
        "cta": "#2ED573",
    }
    accent = accent_colors.get(role, "#25D8FF")

    return f"""
    <div data-motion-target="scene-bg" style="position:absolute;inset:0;background:{bg};">
      <div class="bg-grid"></div>
      <div class="bg-glow bg-glow-1" style="background:radial-gradient(circle, {accent}22 0%, transparent 70%);"></div>
      <div class="bg-glow bg-glow-2" style="background:radial-gradient(circle, {accent}18 0%, transparent 70%);"></div>
    </div>
    <div data-motion-target="headline" class="headline-container" style="position:absolute;top:280px;left:72px;right:72px;">
      <div class="title" style="font-size:64px;font-weight:700;color:#fff;line-height:1.15;">{headline}</div>
    </div>
    <div data-motion-target="metric-panel" class="metric-panel" style="position:absolute;top:500px;left:72px;right:72px;display:flex;flex-direction:column;gap:16px;">
      <div class="metric-card" style="background:rgba(37,216,255,0.08);border:1px solid rgba(37,216,255,0.25);border-radius:16px;padding:20px 24px;">
        <b style="font-size:48px;font-weight:800;color:{accent};">40%</b>
        <span style="font-size:22px;color:rgba(255,255,255,0.75);display:block;margin-top:8px;">效率提升</span>
      </div>
    </div>
    <div class="scene-label" style="position:absolute;top:24px;left:24px;font-size:14px;color:{accent};opacity:0.7;">{sid} · {role}</div>
"""


def _generate_scene_css(sid: str, role: str) -> str:
    """Generate scoped CSS for a scene."""
    accent_colors = {
        "hook": "#FF4757",
        "pain": "#FF6B35",
        "method": "#2ED573",
        "evidence": "#4D9FFF",
        "proof": "#4D9FFF",
        "cta": "#2ED573",
    }
    accent = accent_colors.get(role, "#25D8FF")
    return f"""
.{sid.lower()}-hook-container {{
  position: absolute; top: 200px; left: 72px; right: 72px;
}}
.headline {{
  font-size: 74px; font-weight: 700; color: #fff; line-height: 1.1;
  text-shadow: 0 4px 20px rgba(0,0,0,0.5);
}}
.metric-card {{
  background: rgba({accent.replace('#', '')}, 0.08);
  border: 1px solid rgba({accent.replace('#', '')}, 0.25);
  border-radius: 16px; padding: 20px 24px;
}}
.metric-card b {{
  font-size: 48px; font-weight: 800; color: {accent}; line-height: 1;
}}
.bg-grid {{
  position: absolute; inset: 0; pointer-events: none;
  background-image:
    linear-gradient({accent}08 1px, transparent 1px),
    linear-gradient(90deg, {accent}08 1px, transparent 1px);
  background-size: 72px 72px;
  animation: grid-drift 18s linear infinite;
}}
@keyframes grid-drift {{
  0% {{ background-position: 0 0; }}
  100% {{ background-position: 72px 72px; }}
}}
.bg-glow {{
  position: absolute; width: 420px; height: 420px; border-radius: 50%;
  animation: glow-pulse 3.5s ease-in-out infinite; pointer-events: none;
}}
.bg-glow-1 {{ top: -120px; left: -80px; animation-delay: 0s; }}
.bg-glow-2 {{ bottom: -140px; right: -60px; animation-delay: 1.8s; }}
@keyframes glow-pulse {{
  0%, 100% {{ opacity: 0.5; transform: scale(1); }}
  50% {{ opacity: 0.8; transform: scale(1.15); }}
}}
"""


def _generate_scene_gsap(sid: str, role: str, start: float, duration: float) -> str:
    """Generate GSAP timeline for a scene."""
    # GSAP for entrance animations - animate FROM offscreen TO final position
    # Using scope prefix: [data-scene-id="S01"]
    return f"""
const tl_{sid} = gsap.timeline({{ paused: true }});
window.__timelines['{sid}'] = tl_{sid};
tl_{sid}.fromTo('[data-scene-id="{sid}"] .headline', {{y:60, opacity:0}}, {{y:0, opacity:1, duration:0.8, ease:'power3.out'}}, 0);
tl_{sid}.fromTo('[data-scene-id="{sid}"] .metric-card', {{y:40, opacity:0}}, {{y:0, opacity:1, duration:0.6, ease:'power2.out'}}, 0.3);
tl_{sid}.fromTo('[data-scene-id="{sid}"] .bg-grid', {{opacity:0}}, {{opacity:1, duration:1.0}}, 0);
"""


def _build_combined_html(
    project_id: str,
    scenes: list[dict[str, Any]],
    total_duration: float,
    audio_src: str | None = None,
    caption_beats: dict[str, Any] | None = None,
    semantic_transitions: dict[str, Any] | None = None,
) -> str:
    """Build the full combined HTML string."""
    # Per-scene CSS and GSAP
    scene_css_blocks = []
    scene_layer_htmls = []
    gsap_timeline_blocks = []

    for s in scenes:
        sid = s["scene_id"]
        scoped_css = _scope_css(s.get("css", ""), sid)
        scene_css_blocks.append(f"/* ===== {sid} ({s.get('role','')}) ===== */\n{scoped_css}\n")

        body_content = s.get("body", "").strip()
        scene_layer_htmls.append(
            f"  <!-- {sid} ({s.get('role','')}): {s.get('start',0):.2f}s – {s.get('start',0)+s.get('duration',0):.2f}s -->\n"
            f"  <div class='scene-layer' data-scene-id='{sid}' data-composition-id='{sid}' data-motion-target='scene-layer'>\n"
            f"    {body_content}\n"
            f"  </div>"
        )

        gsap = s.get("gsap", "")
        if gsap:
            gsap_timeline_blocks.append(f"  // === {sid} timeline ===\n{gsap}\n")

    # Master timeline
    master_js = _build_master_timeline(scenes, total_duration, semantic_transitions=semantic_transitions)

    # Caption layer
    caption_html = _build_caption_layer(caption_beats, scenes)
    caption_gsap = _build_caption_gsap(caption_beats, scenes)

    scene_css = "\n".join(scene_css_blocks)
    timeline_blocks_js = "\n".join(gsap_timeline_blocks)
    caption_gsap_js = caption_gsap
    master_js_out = master_js

    return f"""<!doctype html>
<html>
<head>
  <meta charset="utf-8" />
  <title>{project_id} — HyperFrames Combined</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <style>
    * {{ box-sizing: border-box; margin: 0; padding: 0; }}
    html, body {{
      width: 1080px; height: 1920px;
      overflow: hidden;
      background: #050814;
      font-family: -apple-system, BlinkMacSystemFont, "PingFang SC", "Microsoft YaHei", sans-serif;
    }}
    #stage {{
      position: relative; width: 1080px; height: 1920px; overflow: hidden; background: #050814;
    }}
    .scene-layer {{
      position: absolute; top: 0; left: 0; width: 1080px; height: 1920px; display: block; opacity: 1;
    }}
    /* ── Scene CSS ── */
{scene_css}
    /* ── Global HUD ── */
    #combined-progress {{
      position: fixed; bottom: 0; left: 0; height: 4px;
      background: linear-gradient(90deg, #25D8FF, #2ED573); width: 0%; z-index: 9999;
    }}
    #combined-hud {{
      position: fixed; top: 16px; right: 24px;
      background: rgba(0,0,0,.72); border: 1px solid rgba(37,216,255,.3);
      border-radius: 10px; padding: 8px 18px; font-size: 15px; color: #25D8FF; z-index: 9999;
    }}
    #combined-time {{
      position: fixed; top: 16px; left: 24px;
      background: rgba(0,0,0,.72); border: 1px solid rgba(37,216,255,.3);
      border-radius: 10px; padding: 8px 18px; font-size: 15px; color: #25D8FF; z-index: 9999;
    }}
    #combined-controls {{
      position: fixed; bottom: 20px; left: 50%; transform: translateX(-50%);
      display: flex; gap: 10px; z-index: 9999;
    }}
    #combined-controls button {{
      background: rgba(37,216,255,.12); border: 1px solid rgba(37,216,255,.38);
      color: #25D8FF; border-radius: 10px; padding: 9px 20px; font-size: 15px; cursor: pointer;
    }}
    #combined-controls button:hover {{ background: rgba(37,216,255,.28); }}
    /* ── V2.2.1: S01 Headline force-visible ── */
    [data-scene-id="S01"] [data-motion-target='headline'] {{
      font-size: 74px !important; font-weight: 700 !important; line-height: 1.1 !important;
      min-width: 860px !important; min-height: 90px !important;
      display: flex !important; opacity: 1 !important;
      transform: none !important; visibility: visible !important;
    }}
    [data-scene-id="S01"] .title {{
      font-size: 74px !important; font-weight: 700 !important; line-height: 1.1 !important;
      display: block !important; opacity: 1 !important;
    }}
    [data-scene-id="S01"] .scene-layer {{
      display: block !important; opacity: 1 !important;
    }}
    /* ── Caption styles ── */
    #combined-captions {{
      position: fixed; bottom: 76px; left: 50%; transform: translateX(-50%);
      z-index: 9998; pointer-events: none;
    }}
    .caption-beat {{
      position: absolute; left: 72px; right: 72px; bottom: 0; text-align: center;
      font-size: 42px; line-height: 1.28; color: #fff;
      text-shadow: 0 3px 12px rgba(0,0,0,.8);
      background: rgba(0,0,0,.72); border: 1px solid rgba(255,255,255,.12);
      border-radius: 16px; padding: 18px 28px; width: 860px; min-height: 80px;
      box-sizing: border-box; opacity: 0; transform: translateY(20px);
      display: block !important;
    }}
  </style>
</head>
<body>
  <div id="stage" data-composition-id="{project_id}" data-width="1080" data-height="1920" data-start="0">
{chr(10).join(scene_layer_htmls)}
  </div>
  {caption_html}
  <div id="combined-progress"></div>
  <div id="combined-hud">{scenes[0]['scene_id'] if scenes else '—'} · {scenes[0].get('role','') if scenes else ''}</div>
  <div id="combined-time">0.0s / {total_duration:.1f}s</div>
  <div id="combined-controls">
    <button id="btn-play">Play</button>
    <button id="btn-pause">Pause</button>
    <button id="btn-reset">Reset</button>
  </div>
  <audio id="voiceover-audio" preload="auto" src="{audio_src if audio_src else ''}"></audio>
  <script src="https://cdn.jsdelivr.net/npm/gsap@3.12.5/dist/gsap.min.js"></script>
  <script>
  window.__timelines = window.__timelines || {{}};
{timeline_blocks_js}
{caption_gsap_js}
{master_js_out}
  </script>
</body>
</html>"""


def _scope_css(css: str, scene_id: str) -> str:
    """Scope CSS selectors with data-scene-id."""
    lines = []
    for line in css.splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("/*") or stripped.startswith("@"):
            lines.append(line)
            continue
        if stripped.startswith("}"):
            lines.append(line)
            continue
        # Check if it's a selector line
        brace_idx = line.index("{") if "{" in line else -1
        if brace_idx > 0:
            selector = line[:brace_idx].strip()
            if selector and not selector.startswith("[data-scene-id"):
                scoped = f'[data-scene-id="{scene_id}"] {selector}'
                rest = line[brace_idx:]
                lines.append(scoped + rest)
            else:
                lines.append(line)
        else:
            lines.append(line)
    return "\n".join(lines)


def _build_caption_layer(caption_beats: dict[str, Any] | None, scenes: list) -> str:
    if not caption_beats:
        return "  <!-- caption_beats not available -->"
    beats = caption_beats.get("caption_beats", [])
    if not beats:
        return "  <!-- no caption beats -->"

    lines = ['  <div id="combined-captions">']
    for b in beats:
        safe_text = b.get("text", "").replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        lines.append(
            f"    <div class='caption-beat' id='{b['caption_id']}' "
            f"data-caption-id='{b['caption_id']}' "
            f"data-start='{b['start']:.2f}' "
            f"data-duration='{b['duration']:.2f}' "
            f"data-scene-id='{b['scene_id']}'>"
            f"{safe_text}</div>"
        )
    lines.append("  </div>")
    return "\n".join(lines)


def _build_caption_gsap(caption_beats: dict[str, Any] | None, scenes: list) -> str:
    if not caption_beats:
        return "// caption_beats not available"
    beats = caption_beats.get("caption_beats", [])
    if not beats:
        return "// no caption beats"

    lines = ["// ── Per-beat caption timeline ───────────────────────────────", "window.__captions = {};"]

    for b in beats:
        cid = b["caption_id"]
        duration = b["duration"]
        lines.append(
            f"window.__captions['{cid}'] = gsap.timeline({{paused:true}});"
            f"window.__captions['{cid}'].fromTo('#{cid}',"
            f"{{opacity:0, y:20}},{{opacity:1,y:0,duration:0.25,ease:'power2.out'}});"
            f"window.__captions['{cid}'].to('#{cid}',"
            f"{{opacity:0,y:-10,duration:0.25,ease:'power2.in'}},{duration:.2f});"
        )

    lines.append("")
    lines.append("// ── Master caption timeline ──────────────────────────────")
    lines.append("const masterCaptions = gsap.timeline({ paused: true });")
    for b in beats:
        cid = b["caption_id"]
        start = b["start"]
        lines.append(f"masterCaptions.add(window.__captions['{cid}'], {start:.2f});")
    lines.append("window.__timelines['captions'] = masterCaptions;")

    lines.append("")
    lines.append("const masterCaptionTimeline = gsap.timeline({ paused: true });")
    lines.append("masterCaptionTimeline.add(window.__timelines['captions'], 0);")

    return "\n".join(lines)


def _build_master_timeline(
    scenes: list[dict[str, Any]],
    total_duration: float,
    semantic_transitions: dict[str, Any] | None = None,
) -> str:
    """Build the master GSAP timeline JS."""
    fade = 0.18
    st_data = semantic_transitions or {}
    transitions_list = st_data.get("transitions", [])

    lines = [
        "// ── Master timeline ─────────────────────────────────────────────",
        "const master = gsap.timeline({ paused: true });",
        "",
    ]

    # Add scene timelines at their start offsets
    for s in scenes:
        sid = s["scene_id"]
        start = s["start"]
        lines.append(f"master.add(window.__timelines['{sid}'], {start:.2f});")

    lines.append("")

    # Scene visibility: fade in at start, fade out before next scene
    for i, s in enumerate(scenes):
        sid = s["scene_id"]
        start = s["start"]
        duration = s["duration"]
        end = start + duration

        lines.append(
            f"master.fromTo('[data-scene-id=\"{sid}\"]',"
            f"{{opacity:0}},{{opacity:1,duration:{fade},ease:'power2.out'}},"
            f"{start:.2f});"
        )

        if i < len(scenes) - 1:
            next_start = scenes[i + 1]["start"]
            # V2.2.1 Fix: overlap fade-out with next scene's fade-in to prevent gap
            fade_out_at = min(end - fade, next_start - fade)
            next_sid = scenes[i + 1]["scene_id"]
            next_fade_in_at = fade_out_at  # next scene fades in at same time as current fades out

            lines.append(
                f"master.to('[data-scene-id=\"{sid}\"]',"
                f"{{opacity:0,duration:{fade},ease:'power2.in'}},"
                f"{fade_out_at:.2f});"
            )
            lines.append(
                f"master.fromTo('[data-scene-id=\"{next_sid}\"]',"
                f"{{opacity:0}},{{opacity:1,duration:{fade},ease:'power2.out'}},"
                f"{next_fade_in_at:.2f});"
            )

    # Semantic transitions
    if transitions_list:
        lines.append("")
        lines.append("// ── Semantic transitions ────────────────────────────────")
        for idx, t in enumerate(transitions_list):
            from_sid = t.get("from_scene", "")
            to_sid = t.get("to_scene", "")
            start = t.get("start", 0.0)
            gsap_code = t.get("gsap_code", "")
            if gsap_code:
                lines.append(f"  // {from_sid} → {to_sid} at {start:.2f}s")
                lines.append(gsap_code)

    lines.append("")
    lines.append(f"master.to(master, {{}}, {total_duration:.2f});")
    lines.append(
        f"master.to('#combined-progress',"
        f"{{width:'100%',ease:'none',duration:{total_duration:.2f}}},0);"
    )
    lines.append(
        "master.eventCallback('onUpdate',function(){"
        f"var t=master.time();"
        f"document.getElementById('combined-time').textContent="
        f"t.toFixed(1)+'s / {total_duration:.1f}s';"
    )
    for s in scenes:
        sid = s["scene_id"]
        start = s["start"]
        end = start + s["duration"]
        role = s.get("role", "")
        lines.append(
            f"if(t>={start:.2f}&&t<{end:.2f})"
            f"document.getElementById('combined-hud').textContent='{sid} · {role}';"
        )
    lines.append("});")

    lines.append("window.__timelines['combined'] = master;")
    lines.append("")
    lines.append(
        "document.getElementById('btn-play').addEventListener('click',function(){master.play();});"
    )
    lines.append(
        "document.getElementById('btn-pause').addEventListener('click',function(){master.pause();});"
    )
    lines.append(
        "document.getElementById('btn-reset').addEventListener('click',function(){master.restart();});"
    )
    lines.append(f"console.log('HyperFrames V3 combined ready. Duration: {total_duration:.1f}s');")

    return "\n".join(lines)