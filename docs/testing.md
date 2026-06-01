# Testing

## Running Tests

```bash
cd <PROJECT_ROOT>
pytest tests/ -v
```

## Test Suite

| Test | Purpose |
|------|---------|
| test_paths.py | Verify outputs go to outputs/ or test_outputs/, never src/outputs |
| test_input_relevance.py | Verify sample script input_relevance_score >= 0.7 |
| test_tts_contract.py | Verify audio-first defaults, long-script distillation, and dynamic storyboard timing |
| test_preview_pipeline.py | Verify preview structure, fail-closed approval, dynamic transitions, visual beats, and caption splitting |
| test_render_gate.py | Verify render_mp4 without --approved fails |

## Smoke Test

To run a minimal smoke test:

```bash
python3 -m video_director_v3.cli \
  --script samples/scripts/minimal_obsidian_codex_hermes.md \
  --platform douyin \
  --target-duration 40 \
  --project-id smoke_test \
  --output-mode hyperframes_preview \
  --tts-mode edge_tts \
  --tts-fallback system_say \
  --design-variance 7 \
  --motion-intensity 6 \
  --visual-density 8 \
  --no-allow-mock-audio
```

Then verify smoke render:

```bash
python3 -m video_director_v3.cli \
  --project-id smoke_test \
  --output-mode render_mp4 \
  --approved \
  --render-smoke-seconds 5 \
  --fps 25
```
