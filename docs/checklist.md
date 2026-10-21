# First milestone checklist

This checklist tracks implementation and evidence separately. The broader phase exits
remain in [PROJECT_PLAN.md](../PROJECT_PLAN.md).

## Software

- [x] Install the Python 3.11 environment and CLI.
- [x] Validate configuration and report camera capabilities.
- [x] Capture live video and replay recordings through the same pipeline.
- [x] Detect moving candidates and assign centroid track IDs.
- [x] Save raw/annotated videos, track CSV, and run metadata.
- [x] Verify failures, interruption, and resource cleanup with automated tests.
- [x] Pass automated tests, lint, and format checks.
- [x] Complete a brief headless C270 recording and verify saved frames.

Verification on 2026-10-21: 20 tests passed; Ruff lint and formatting passed. C270 run
`data/runs/20261021T200319Z-fa8a3247` saved 144 frames at 1280×720 with measured capture
rate 30.0 FPS. Both videos decode fully. Recordings are local and ignored by Git.
Interactive preview and household-target accuracy still require operator observation.

## Household-target experiments (operator)

- [ ] Fix the camera in place with a plain, stationary background.
- [ ] Record a small target moving horizontally, vertically, and diagonally.
- [ ] Check bounding boxes and ID continuity by watching annotated replay.
- [ ] Compare at least two distances and lighting conditions.
- [ ] Record apparent target size, motion blur, false detections, and dropouts.
- [ ] Select a useful baseline configuration and retain the run IDs.

## Lovebug feasibility (later evidence)

- [ ] Collect 2–3 short clips with recognizable lovebugs and experiment notes.
- [ ] Manually mark target visibility and compare it with candidate tracks.
- [ ] Measure detection precision/recall and track continuity on those clips.
- [ ] Document useful camera range and limitations before selecting flight hardware.

Household and synthetic targets validate software behavior, not lovebug recognition.
