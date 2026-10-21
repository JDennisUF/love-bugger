# Lovebug Interceptor — Project Plan

**Status:** Camera prototype implemented; lovebug feasibility testing pending
**Last updated:** 2026-10-21  
**Development environment:** Linux desktop, Zed, local Git repository  
**Implementation progress:** See [first milestone checklist](docs/checklist.md) and [camera experiments](docs/experiments.md).
**First objective:** Detect, track, and physically intercept **one** flying lovebug in a controlled test area.

## 1. Vision

Develop a single, camera-guided flying device that actively approaches lovebugs in outdoor gathering spaces (patios, yards, and similar areas). Unlike passive traps, the system should seek and intercept individual insects. Start with a supervised prototype; scale only after proving the fundamentals.

**Success is not measured by number of features.** The first meaningful demonstration is a repeatable, recorded intercept of one lovebug under controlled conditions.

## 2. Decisions and working assumptions

| Topic | Current direction | Confidence |
| --- | --- | --- |
| Development | Local repository, Zed, incremental coding and testing | Decided |
| Operator station | Linux desktop | Decided |
| Number of drones | One initially | Decided |
| Target | Florida lovebugs | Decided |
| Engagement | Active physical interception, not passive trapping | Decided |
| Tracking | Stationary external camera tracks insect and drone | Preferred architecture; unproven |
| Navigation | Ground station estimates intercept vector and sends guidance | Proposed |
| Drone processing | Minimize onboard compute/weight | Preferred |
| Interception mechanism | Lightweight spinning circular wire with three thin spokes | Concept only; safety and effectiveness untested |
| Lighting | Test visible backlighting, UV-A, and IR for contrast | Open experiment |
| Deployment | Outdoor spaces where people gather | Long-term goal, **not** initial test environment |

## 3. Key constraints and risks

- **Safety:** A high-speed exposed wire rotor could injure people, pets, or wildlife. Do not test it exposed. Begin with non-contact interception simulations and a fully enclosed, guarded test rig; choose a guarded capture or contact mechanism before any flight test.
- **Flying near people:** No autonomous pursuit near people, animals, windows, vehicles, or other obstacles during early development. Use a contained test volume and manual emergency stop.
- **Target visibility:** Lovebugs are small; camera resolution, contrast, motion blur, and range will determine feasibility.
- **Depth ambiguity:** One stationary camera provides image coordinates, not reliable 3D target position without additional assumptions. Evaluate stereo cameras, multiple viewpoints, or depth constraints.
- **Drone tracking:** Distinguish the drone from the insect in the same camera stream. Fiducial markers or separate tracking cues may help.
- **Latency:** Exposure, detection, tracking, network transmission, and drone response all consume time; interception needs prediction rather than pursuit of stale positions.
- **Airflow:** Prop wash can deflect an insect before contact; the proposed spinning wire may also create airflow. Measure rather than assume.
- **Environmental conditions:** Sunlight, wind, foliage, moving shadows, and other insects can produce false detections.
- **Battery/endurance:** Payload and aggressive maneuvers reduce flight time.
- **Rules and nuisance:** Check applicable drone rules, local restrictions, and effects on non-target insects before outdoor deployment.

## 4. Proposed architecture

```text
 Stationary camera(s)
         |
         v
 Linux ground station (Python + OpenCV)
   - frame acquisition
   - insect detection
   - drone detection
   - multi-object tracking
   - coordinate calibration
   - motion prediction
   - intercept planning
   - safety supervisor
         |
         v
 Command link / flight controller
         |
         v
 Single guarded test drone
         |
         v
 Telemetry + video logs -> analysis and tuning
```

Keep perception, tracking, planning, and drone-control interfaces separate so recorded video and a simulated drone can be used before flying hardware.

## 5. Development phases

### Phase 0 — Repository and safety foundation

- [x] Initialize Python project, virtual environment, formatter/linter, and basic tests.
- [ ] Create configuration for cameras, calibration, detection thresholds, and safety limits.
- [x] Define a no-flight simulation mode as the default (current application is perception-only).
- [ ] Define kill-switch behavior, loss-of-tracking behavior, and allowed test boundaries.
- [ ] Document a contained test area and an observer/operator procedure.

**Exit criterion:** Application runs locally, reads a configuration, and processes a sample video without any hardware commands.

### Phase 1 — Prove lovebug detection

- [ ] Collect short daytime and dusk recordings with lovebugs in view.
- [ ] Record approximate target distance, lighting, camera resolution, FPS, and lens field of view.
- [ ] Test visible diffuse backlighting, 365 nm UV-A, and 850 nm IR **only with compatible cameras and appropriate eye protection**.
- [ ] Determine whether lovebugs fluoresce or merely reflect under UV; do not assume UV makes them brighter.
- [x] Implement simple background subtraction / motion detection.
- [x] Overlay bounding boxes and track IDs on recorded footage (verified with synthetic footage).
- [ ] Measure detection rate, false positives, and apparent target size in pixels.

**Exit criterion:** Reliably identify and track individual lovebugs in representative recorded video, with documented results.

### Phase 2 — Tracking and trajectory estimation

- [ ] Estimate 2D positions and velocities over time.
- [ ] Test Kalman filtering or another simple motion estimator.
- [ ] Evaluate camera frame rate and shutter speed to limit motion blur.
- [ ] Measure tracking dropouts and prediction error.
- [ ] Decide how to obtain depth: stereo, second camera, constrained plane, or another method.
- [ ] Establish camera-to-test-volume calibration.

**Exit criterion:** Predict a target's short-term position and quantify prediction error in physical units.

### Phase 3 — Drone tracking and simulated intercepts

- [ ] Choose a small drone with a documented, controllable interface and telemetry.
- [ ] Establish its position estimate relative to the camera system.
- [ ] Build a simulation or replay mode that takes insect tracks and models drone motion.
- [ ] Implement intercept-point estimation and velocity/acceleration limits.
- [ ] Include confidence thresholds, obstacle exclusion zones, geofencing, and fail-safe hover/land behavior.
- [ ] Compare simple pursuit with predictive interception in simulation.

**Exit criterion:** Simulated drone consistently reaches predicted intercept points without violating test-volume limits.

### Phase 4 — Controlled flight, no insect contact

- [ ] Fly the drone manually in a contained, unoccupied test area.
- [ ] Validate external drone tracking against flight telemetry.
- [ ] Test limited autonomous movements to static waypoints.
- [ ] Test moving-target tracking using a harmless visual target.
- [ ] Measure end-to-end command latency and position error.
- [ ] Confirm safe behavior on lost camera feed, lost target, and lost communications.

**Exit criterion:** The drone can safely follow a moving virtual/visual target and stop on command, without any exposed interception device.

### Phase 5 — Interception mechanism research

**Original concept:** A circular, rapidly rotating, three-spoke thin-wire device intended to contact a slow-moving lovebug. This is an **unvalidated concept**, not an approved flight component.

- [ ] Sketch mass, diameter, mounting location, power, and shielding constraints.
- [ ] Analyze exposed-wire hazards and reject configurations that cannot be fully guarded.
- [ ] Evaluate safer enclosed alternatives, such as a guarded capture inlet or soft-contact mechanism.
- [ ] Test airflow and target deflection on a stationary enclosed bench rig.
- [ ] Assess fouling, cleaning, weight, vibration, and drone stability.
- [ ] Select a mechanism only after demonstrating safe containment.

**Exit criterion:** Bench-tested, guarded mechanism with measured effectiveness and no exposed moving contact parts.

### Phase 6 — First live intercept

- [ ] Integrate perception, prediction, control, and guarded interception hardware.
- [ ] Operate in a contained test enclosure, away from bystanders and non-target animals.
- [ ] Start with a supervised single-target trial and a manual abort control.
- [ ] Record camera video, track history, commands, telemetry, and outcome.
- [ ] Repeat trials and classify misses (detection, depth, prediction, control, airflow, contact).

**Exit criterion:** Repeatable successful interception of a single lovebug under controlled conditions.

### Phase 7 — Only after proof of concept

Investigate larger coverage areas, multiple camera views, outdoor lighting, wind tolerance, target classification, flight endurance, docking/charging, and responsible deployment around people and non-target insects.

## 6. First technical spike: camera feasibility

Before buying drone parts, answer:

1. At what distance can the camera resolve a lovebug as a useful target (not just a pixel)?
2. What FPS and shutter speed keep it trackable?
3. Which illumination/background combination provides the highest contrast?
4. How many simultaneous flying objects can be tracked without identity swaps?
5. Can a second camera provide useful 3D coordinates at the intended range?

**Suggested first deliverable:** A Python script that loads a video or live webcam feed, highlights candidate moving insects, assigns track IDs, and saves an annotated video plus CSV of `(timestamp, track_id, x_px, y_px, confidence)`.

## 7. Initial software stack (provisional)

- **Language:** Python 3.11+.
- **Video and image processing:** OpenCV.
- **Numerics:** NumPy.
- **Tracking:** Begin with a simple centroid tracker; add a Kalman filter as needed.
- **Testing:** pytest.
- **Configuration:** TOML or YAML.
- **Data:** MP4 recordings, CSV/JSONL event logs.
- **Drone integration:** Defer selection until camera/tracking feasibility is established; prefer a documented SDK or standard telemetry/control protocol.

Avoid ML model training, complex infrastructure, or a web UI until basic computer vision demonstrates value.

## 8. Suggested repository layout

```text
lovebug-interceptor/
├── README.md
├── PROJECT_PLAN.md
├── pyproject.toml
├── config/
│   └── example.toml
├── src/
│   └── lovebug_interceptor/
│       ├── camera.py
│       ├── detector.py
│       ├── tracker.py
│       ├── calibration.py
│       ├── prediction.py
│       ├── simulator.py
│       ├── safety.py
│       └── main.py
├── tests/
├── scripts/
├── docs/
│   ├── experiments.md
│   └── safety.md
└── data/
    └── .gitkeep
```

Add raw video recordings and local configuration files to `.gitignore` unless intentionally publishing small, licensed test clips.

## 9. Measurements to record

| Metric | Why it matters |
| --- | --- |
| Detection precision / recall | Is the insect actually found? |
| Target pixels across | Is camera resolution sufficient? |
| Track continuity | Can the same insect be followed? |
| 3D localization error | Is its physical position known? |
| Prediction error at 100–500 ms | Can we aim ahead of the insect? |
| Camera-to-command latency | How stale is the guidance? |
| Drone position error | Can the aircraft reach the target location? |
| Airflow-induced target displacement | Does the drone push the insect away? |
| Successful intercepts / attempts | Does the integrated system work? |
| False engagements / non-target detections | Is operation selective and safe? |

## 10. Current status and immediate next actions

**Completed conceptually:** Defined the problem, chose one-drone scope, preferred a stationary camera with Linux-based tracking, discussed an active interception concept, and identified lighting as an early experiment.

**Implemented and verified:** Python 3.11 CLI, TOML configuration, live camera capture,
video replay, motion candidates, centroid track IDs, raw/annotated recordings, CSV logs,
and metadata. Automated tests pass. The Logitech C270 recorded 144 readable 1280×720
frames in a five-second capture at approximately 30 FPS. This was a capture smoke test,
not a target-detection experiment. See the milestone checklist for remaining operator trials.

**Not yet demonstrated:** Lovebug detection, UV/IR response, 3D tracking, flight control, interception mechanism, and successful contact.

**Next work session:**

1. Follow the household-target procedure in `docs/experiments.md`.
2. Inspect annotated recordings and tune candidate-size and tracking limits.
3. Compare target visibility at two distances and lighting conditions.
4. Obtain 2–3 short lovebug video clips recorded with the C270.
5. Measure baseline lovebug detection performance before selecting drone hardware.

## 11. Open decisions

- Camera model, lens, frame rate, and placement.
- Indoor test volume dimensions and target range.
- Single vs stereo camera configuration.
- Drone platform and its control API.
- Safe guarded interception mechanism.
- Lighting requirements for daylight vs dusk.
- Target/non-target classification and deployment restrictions.

---

**Guiding principle:** Prove perception first, then localization, then predictive control, then safe physical interception. Keep each phase independently testable.
