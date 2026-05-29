# Design System

## Design Dials

V3 provides three design dials to control visual output:

| Dial | Range | Default | Description |
|------|-------|---------|-------------|
| DESIGN_VARIANCE | 1-10 | 7 | Controls layout variation |
| MOTION_INTENSITY | 1-10 | 6 | Controls animation intensity |
| VISUAL_DENSITY | 1-10 | 8 | Controls information density |

## Design Profile

The design profile builder combines:
- Script semantics
- Design dials
- Optional brandkit
- Optional DESIGN.md

Output: `visual_style_profile.json`

## Brandkit

Generates `brandkit.json` for:
- Colors
- Fonts
- Component styles
- Caption styles

## Stitch Design

Generates `DESIGN.md` for video visual design (not web design).

## ImageGen

Optional visual reference images - not a blocking step for preview or MP4 render.