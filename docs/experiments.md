# Camera experiments

## Household-target procedure

1. Mount the C270 so it stays still. Use a plain background and diffuse visible light.
2. Record the target's approximate size and distance. A small paper dot on a thread
   is a convenient first target; keep hands outside the scene when possible.
3. Start a 20–30 second recording. Leave the scene still for at least two seconds so
   the background model settles, then move the target across the image.
4. Try horizontal, vertical, and diagonal motion, a brief disappearance, and a stationary
   pause. Candidate detection is based on motion, so stationary targets can disappear.
5. Replay the raw video to compare settings. Watch the annotated video for missed
   targets, unrelated boxes, and ID changes. Count visible target frames manually when
   estimating recall; count correct versus unrelated detections when estimating precision.
6. Repeat at another distance and with different visible lighting. Keep the camera
   position and settings fixed within each run. Record settings and retain run IDs.

Start with automatic exposure. The C270 currently exposes automatic exposure and
dynamic frame-rate controls; dim light may lower delivered FPS or increase blur.
Use `love-bugger inspect` to review supported controls. Record any manual changes,
then compare delivered FPS and target sharpness; the application does not alter exposure.

Tune `detector.min_area` and `max_area` for the observed foreground size in pixels.
Avoid increasing the minimum so much that small insect-sized targets are filtered out.
`tracker.max_distance_px` gates movement per frame; a large value can increase identity
swaps. `max_missed_frames` controls how long an unseen track can retain its ID.
MOG2 background subtraction and greedy centroid matching are an initial baseline.

## Result template

Copy this section for each experiment (or keep private notes alongside ignored run data).

| Field | Observation |
| --- | --- |
| Date / run directory | |
| Target and approximate dimensions | |
| Approximate camera-to-target distance | |
| Lighting and background | |
| Requested / negotiated resolution and FPS | |
| Measured capture FPS | |
| Exposure changes, if any | |
| Target bounding-box size in pixels | |
| Motion blur / contrast | |
| Visible target frames / detected target frames | |
| Correct / unrelated candidate observations | |
| Track dropouts / identity changes | |
| Configuration / next adjustment | |

For lovebug trials, retain 2–3 representative clips and visually confirm species and
target location before scoring. Distances are experiment notes, not calibrated 3D output.
