# Love Bugger

Camera feasibility tools for a camera-guided lovebug interceptor. This first milestone
detects moving **candidates**, assigns track IDs, and records evidence for analysis.
It does not identify insect species. See [PROJECT_PLAN.md](PROJECT_PLAN.md) for the roadmap
and [the milestone checklist](docs/checklist.md) for current progress.

## Install

Use Python 3.11+ and run commands from the repository root:

```bash
python3.11 -m venv .venv
source .venv/bin/activate
python -m pip install -e '.[dev]'
```

On Debian/Ubuntu, a missing `ensurepip` usually requires `python3.11-venv`.
Camera inspection requires `v4l-utils`. Preview requires a graphical desktop and OpenCV's
system GUI libraries (commonly `libgl1` and `libxcb-cursor0`). Use `--headless` over SSH.
The installed OpenCV package includes preview support; do not also install
`opencv-python-headless` in this environment.

## Inspect and capture

The default device is the Logitech C270 discovered on this desktop. It advertises
1280×720 at 30 FPS using MJPEG; actual delivery depends on exposure and lighting.

```bash
love-bugger inspect
love-bugger live --duration 30 --notes "Small paper target; plain background; distance 0.5 m"
love-bugger live --headless --duration 5
```

Preview opens by default. Press `q`, Escape, or Ctrl-C to finish; closing the window also
stops the run. All capture runs record automatically. Mount the camera firmly and keep
the scene still during the initial 30-frame background warm-up.

To change devices, use `--device /dev/video0` or copy `config/example.toml` to
`config/local.toml`, edit it, and supply `--config config/local.toml`. Local config is
ignored by Git. Config and output paths are relative to the current working directory.
Keep the `video-index0` capture device; the C270's second node is not another camera view.
Inspection reports controls without changing exposure settings.

## Replay and outputs

```bash
love-bugger replay data/runs/RUN/raw.avi
love-bugger replay data/runs/RUN/raw.avi --headless --duration 10
```

Each run has a unique directory under `data/runs/` (override with `--output DIRECTORY`):

- `raw.avi`: unannotated frames re-encoded as MJPEG, without audio.
- `annotated.avi`: bounding boxes, track IDs, warm-up indicator, and processing FPS.
- `tracks.csv`: zero-based frame number, timestamp in seconds, track ID, centroid in
  pixels, bounding-box origin, width, and height. Only observed candidates have rows.
- `metadata.json`: configuration, requested and negotiated settings, actual frame size,
  notes, frame count, processing elapsed time, measured read/capture FPS, and completion status.

Live timestamps measure elapsed monotonic time from the first received frame; they are
host arrival times, not hardware exposure times. Replay uses media timestamps, falling
back to frame number/FPS when timestamps are unavailable or fail to increase.
`--duration` means wall time for live capture and media time for replay.
Videos use a constant reported FPS (configured FPS if unavailable), so irregular arrival
times can differ from video playback timing. Use CSV timestamps for track timing.
Replay read FPS measures processing throughput, not the original camera's delivery rate.
Interrupted runs retain their outputs and metadata; failed runs are marked with the error.

## First experiment

Follow [docs/experiments.md](docs/experiments.md) with a small moving household target.
Tune candidate area and association distance in TOML as needed. Background motion,
lighting changes, and camera shake can all produce candidates. Small targets may merge,
disappear when stationary, or swap IDs when crossing. There is no species confidence score.

## Development

```bash
python -m pytest
ruff check .
ruff format --check .
```

Capture, detection, tracking, and recording are separate components under
`src/lovebug_interceptor/`. Automated tests generate a small video fixture; a real camera
is not required. Drone guidance and interception hardware are later project phases.
