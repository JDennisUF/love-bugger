import argparse
import json
import math
import os
import sys
import time
from dataclasses import replace
from datetime import datetime, timezone
from pathlib import Path

import cv2

from .camera import VideoSource, inspect_camera
from .config import Config, load_config
from .detector import MotionDetector
from .recording import Recording
from .tracker import CentroidTracker


def run(config: Config, *, video=None, output=None, duration=None, headless=False, notes=""):
    if duration is not None and (not math.isfinite(duration) or duration <= 0):
        raise ValueError("Duration must be a positive finite number of seconds")
    if not headless and not (os.environ.get("DISPLAY") or os.environ.get("WAYLAND_DISPLAY")):
        raise ValueError("No desktop display found; use --headless")
    source = VideoSource(config.camera, video)
    recording = None
    frames_written = 0
    started = time.monotonic()
    metadata = {
        "started_utc": datetime.now(timezone.utc).isoformat(),
        "mode": "perception_only",
        "config": config.as_dict(),
        "source": source.settings,
        "notes": notes,
        "status": "running",
        "timestamp_basis": "monotonic_elapsed" if source.live else "media_time",
        "opencv_version": cv2.__version__,
    }
    try:
        detector = MotionDetector(config.detector)
        tracker = CentroidTracker(config.tracker)
        recording = Recording(Path(output or config.output.directory))
        recording.metadata(metadata)
        print("Source settings: " + json.dumps(source.settings), flush=True)
        print(f"Recording: {recording.directory}", flush=True)
        if source.live:
            requested = (config.camera.width, config.camera.height, config.camera.fps)
            actual = (source.settings["width"], source.settings["height"], source.fps)
            if requested != actual:
                print(f"Camera negotiated {actual}; requested {requested}", file=sys.stderr)
        while True:
            if source.live and duration is not None and time.monotonic() - started >= duration:
                break
            sample = source.read()
            if sample is None:
                break
            frame, timestamp = sample
            if not source.live and duration is not None and timestamp >= duration:
                break
            if frames_written == 0:
                recording.start(frame, source.fps)
                metadata["frame_size"] = [frame.shape[1], frame.shape[0]]
            tracks = tracker.update(detector.detect(frame))
            annotated = frame.copy()
            for track in tracks:
                detection = track.detection
                cv2.rectangle(
                    annotated,
                    (detection.x, detection.y),
                    (detection.x + detection.width, detection.y + detection.height),
                    (0, 255, 0),
                    1,
                )
                cv2.putText(
                    annotated,
                    f"Candidate {track.track_id}",
                    (detection.x, max(15, detection.y - 5)),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.45,
                    (0, 255, 0),
                    1,
                )
            processing_fps = (frames_written + 1) / max(time.monotonic() - started, 1e-9)
            warming = detector.frames_seen <= config.detector.warmup_frames
            label = "Background warm-up" if warming else f"Motion candidates: {len(tracks)}"
            cv2.putText(
                annotated,
                f"{label} | Processing {processing_fps:.1f} FPS",
                (10, 25),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.55,
                (0, 255, 255),
                1,
            )
            recording.write(frame, annotated, frames_written, timestamp, tracks)
            frames_written += 1
            if not headless:
                cv2.imshow("Love Bugger - motion candidates (q to stop)", annotated)
                delay = 1 if source.live else max(1, round(1000 / source.fps))
                key = cv2.waitKey(delay) & 0xFF
                if (
                    key in (ord("q"), 27)
                    or cv2.getWindowProperty(
                        "Love Bugger - motion candidates (q to stop)", cv2.WND_PROP_VISIBLE
                    )
                    < 1
                ):
                    break
        if frames_written == 0:
            raise ValueError("No frames recorded; increase duration or check the source")
        metadata["status"] = "completed"
    except KeyboardInterrupt:
        metadata["status"] = "interrupted"
    except Exception as error:
        metadata["status"] = "failed"
        metadata["error"] = str(error)
        raise
    finally:
        source.close()
        if not headless:
            cv2.destroyAllWindows()
        if recording:
            recording.close()
            metadata.update(
                {
                    "frames_written": frames_written,
                    "elapsed_seconds": time.monotonic() - started,
                    "measured_capture_fps"
                    if source.live
                    else "measured_read_fps": source.measured_fps,
                }
            )
            recording.metadata(metadata)
    return recording.directory


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="Love Bugger camera and motion-tracking prototype")
    subparsers = parser.add_subparsers(dest="command", required=True)
    for command in ("inspect", "live", "replay"):
        subparser = subparsers.add_parser(command)
        subparser.add_argument("--config", type=Path)
        if command != "replay":
            subparser.add_argument("--device", help="Override camera device path")
        if command == "replay":
            subparser.add_argument("video", type=Path)
        if command != "inspect":
            subparser.add_argument("--output", type=Path, help="Parent directory for a unique run")
            subparser.add_argument(
                "--duration", type=float, help="Wall seconds live; media seconds replay"
            )
            subparser.add_argument("--headless", action="store_true")
            subparser.add_argument("--notes", default="", help="Distance, lighting, target, etc.")
    args = parser.parse_args(argv)
    try:
        config = load_config(args.config)
        if getattr(args, "device", None):
            config = replace(config, camera=replace(config.camera, device=args.device))
        if args.command == "inspect":
            print(inspect_camera(config.camera.device))
        else:
            run(
                config,
                video=getattr(args, "video", None),
                output=args.output,
                duration=args.duration,
                headless=args.headless,
                notes=args.notes,
            )
        return 0
    except (ValueError, OSError, cv2.error) as error:
        print(f"love-bugger: {error}", file=sys.stderr)
        return 1
    except KeyboardInterrupt:
        return 130


if __name__ == "__main__":
    raise SystemExit(main())
