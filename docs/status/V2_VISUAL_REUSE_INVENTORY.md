# V2 Visual Reuse Inventory

## Context

V2 (`video-director_CapCut2.0`) is a more mature project with substantial visual infrastructure. V3 (`video-director-v3`) is a simpler, restructured project. This inventory identifies what V2 has that V3 can reuse vs. what should be deprecated.

---

## Reusable Components

### ✅ Can be DIRECTLY REUSED

| Component | File | Notes |
|---|---|---|
| **ComponentRegistry** | `src/motion_design/component_registry.py` | Canonical names, motion targets, CSS selectors for all HUD/text/data components. V3 should import this and extend it. |
| **LayoutPresets** | `src/motion_design/layout_presets.py` | Zone-based layout system (top_progress, center_panel, bottom_caption). Well-documented and stable. |
| **MotionEventBindings** | `src/motion_design/motion_event_bindings.py` | GSAP animation bindings mapped to component types. V3's GSAP is much simpler — V3 could adopt V2's binding structure. |
| **MetricRail** | `src/motion_design/components/metric_rail.py` | Vertical scrolling metric display with KPI indicators. |
| **CardMatrix** | `src/motion_design/components/card_matrix.py` | 3-column card layout with icons and labels. |
| **ProcessTimeline** | `src/motion_design/components/process_timeline.py` | Horizontal step timeline with nodes and connectors. |
| **Checklist** | `src/motion_design/components/checklist.py` | Numbered action list with hover states. |
| **ScorePanel** | `src/motion_design/components/score_panel.py` | Multi-dimensional rating display. |
| **TablePanel** | `src/motion_design/components/table_panel.py` | Structured data table with rows and columns. |
| **CtaPanel** | `src/motion_design/components/cta_panel.py` | Call-to-action panel with button states. |
| **EvidenceComponents** | `src/motion_design/evidence_components.yaml` | Declarative component configurations. V3 could adopt the YAML format for visual spec. |

---

## Reusable Effects & Animations

### ✅ Can be REUSED (adapt to V3 GSAP structure)

| Effect | File | Notes |
|---|---|---|
| **Scene Transitions** | `src/renderers/hyperframes/transitions/` | S01→S02 cards-to-path, S02→S03 path-to-broken-flow, S03→S04 reconnect-flow, S04→S05 timeline-to-cards, S05→S06 cards-to-table, S06→S07 table-to-checklist, S07→S08 checklist-to-cta. These are GSAP transition objects. |
| **MotionStoryboardBuilder** | `src/renderers/hyperframes/visual_translator/motion_storyboard_builder.py` | Builds full motion storyboard from evidence plan. Could be ported to V3 as `storyboard_builder.py`. |
| **VisualBeatPlanner** | `src/renderers/hyperframes/visual_translator/visual_beat_planner.py` | Converts narrative beats to visual beats. |
| **SemanticTransitionPlanner** | V2 has this, V3 has it at `motion/semantic_transition_planner.py`. V2's version is more sophisticated. |
| **HyperFramesMotionJobBuilder** | `src/renderers/hyperframes/visual_translator/hyperframes_motion_job_builder.py` | Converts motion jobs to HyperFrames HTML. V2's HTML output is more complete than V3's. |

---

## Reusable Caption Styles

### ✅ V2 Caption System (more mature)

V2 `combined_html_builder.py` has better caption handling:
- `data-motion-target='caption'` for proper targeting
- Caption with timing metadata
- Caption GSAP animation tied to master timeline

**V3's captions** are in `#combined-captions` div with `.caption-beat` class — functional but lacks V2's motion-target conventions.

**Reuse recommendation:** V3 should adopt V2's `data-motion-target='caption'` convention and GSAP caption binding.

---

## Reusable HUD Styles

V2 has these HUD elements that V3 lacks:
1. **HudTitleBar** — top bar with label + title + subtitle (scene label in top-left corner)
2. **GridBackground** — grid overlay with animation
3. **ScanOverlay** — screen-edge scan effect
4. **ProgressBar** — bottom progress indicator (V3 has this as `#combined-progress` at bottom: 0 height)
5. **SidePanel** — right-side tag/label panel (V3 doesn't have this)
6. **MetricRail** — left-side vertical scrolling metrics

V3's HUD (in `_build_combined_html`) is: `#combined-hud`, `#combined-time`, `#combined-controls`, `#combined-progress` — all debug-style. **V3 should replace these with V2's more polished HUD components.**

---

## Deprecated or Do Not Use

| Item | Reason |
|---|---|
| **V2 combined_html_builder.py** | Very large (500+ lines), deeply coupled. Not worth migrating wholesale. V3's simpler builder is better as foundation. |
| **V2 hyperframes_job_builder.py** | V2-specific pipeline, not compatible with V3's storyboard structure. |
| **V2 VisualLayerBuilder** | Over-designed for V3's simpler use case. |
| **V2 evidence_planner.py** | Depends on V2's evidence gathering pipeline. |
| **V2 component_selector.py** | Depends on V2's evidence pipeline. |

---

## V3 Cannot Reuse (Structural Mismatch)

1. **CapCut integration** — V2 has CapCut-specific rendering. V3's goal is MP4 only.
2. **V2's scene_purpose + evidence_type system** — V3 uses role-based scenes (hook/pain/method/evidence/proof/cta). Different abstraction.
3. **V2's render stages** — V2 has more complex multi-pass rendering (Studio → HyperFrames → CapCut). V3 has simpler: HTML → frames → MP4.
4. **V2's smoke/quality/approval gates** — V3 has simpler versions of these.

---

## Summary

**V2 gives V3:**
1. Component naming conventions (ComponentRegistry)
2. Layout presets (Zone-based layout system)
3. Motion event binding patterns
4. Specific components: MetricRail, CardMatrix, ProcessTimeline, Checklist, ScorePanel
5. Transition objects (GSAP animations between scenes)
6. Caption style conventions

**V3 should NOT import wholesale:**
- V2's combined_html_builder (too complex, different architecture)
- V2's pipeline stages
- CapCut-specific code

**Recommendation:** Copy V2's `component_registry.py` and `layout_presets.py` into V3, then extend V3's simpler renderer with V2's component patterns.