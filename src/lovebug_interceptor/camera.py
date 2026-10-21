import math
import subprocess
import time
from pathlib import Path

import cv2

from .config import CameraConfig


def inspect_camera(device: str) -> str:
    try:
        result = subprocess.run(
            ["v4l2-ctl", "--device", device, "--all", "--list-formats-ext"],
            capture_output=True,
            text=True,
            check=True,
            timeout=15,
        )
    except FileNotFoundError as error:
        raise ValueError("Install v4l-utils to inspect camera capabilities") from error
    except subprocess.CalledProcessError as error:
        raise ValueError(error.stderr.strip() or "Camera inspection failed") from error
    except subprocess.TimeoutExpired as error:
        raise ValueError("Camera inspection timed out") from error
    return result.stdout


class VideoSource:
    def __init__(self, config: CameraConfig, video: Path | None = None):
        self.live = video is None
        self.frames_read = 0
        self.previous_timestamp = -1.0
        self.first_arrival: float | None = None
        self.last_arrival: float | None = None
        if video is not None and not video.is_file():
            raise ValueError(f"Video does not exist: {video}")
        self.capture = cv2.VideoCapture(
            config.device if self.live else str(video),
            cv2.CAP_V4L2 if self.live else cv2.CAP_ANY,
        )
        try:
            if not self.capture.isOpened():
                raise ValueError(f"Cannot open {'camera ' + config.device if self.live else video}")
            if self.live:
                self.capture.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*config.fourcc))
                self.capture.set(cv2.CAP_PROP_FRAME_WIDTH, config.width)
                self.capture.set(cv2.CAP_PROP_FRAME_HEIGHT, config.height)
                self.capture.set(cv2.CAP_PROP_FPS, config.fps)
            reported_fps = self.capture.get(cv2.CAP_PROP_FPS)
            self.fps = (
                reported_fps if math.isfinite(reported_fps) and reported_fps > 0 else config.fps
            )
            self.settings = {
                "source": config.device if self.live else str(video.resolve()),
                "live": self.live,
                "width": self.capture.get(cv2.CAP_PROP_FRAME_WIDTH),
                "height": self.capture.get(cv2.CAP_PROP_FRAME_HEIGHT),
                "reported_fps": reported_fps if math.isfinite(reported_fps) else None,
                "recording_fps": self.fps,
                "fourcc": int(self.capture.get(cv2.CAP_PROP_FOURCC)),
                "backend": self.capture.getBackendName(),
            }
        except Exception:
            self.capture.release()
            raise

    def read(self):
        success, frame = self.capture.read()
        arrival = time.monotonic()
        if not success:
            if self.live or self.frames_read == 0:
                raise ValueError(
                    "Camera feed lost" if self.live else "Video contains no readable frames"
                )
            return None
        if self.first_arrival is None:
            self.first_arrival = arrival
        self.last_arrival = arrival
        if self.live:
            timestamp = arrival - self.first_arrival
        else:
            timestamp = self.capture.get(cv2.CAP_PROP_POS_MSEC) / 1000
            if not math.isfinite(timestamp) or timestamp <= self.previous_timestamp:
                timestamp = max(self.frames_read / self.fps, self.previous_timestamp + 1 / self.fps)
        self.previous_timestamp = timestamp
        self.frames_read += 1
        return frame, timestamp

    @property
    def measured_fps(self) -> float | None:
        if self.frames_read < 2 or self.last_arrival == self.first_arrival:
            return None
        return (self.frames_read - 1) / (self.last_arrival - self.first_arrival)

    def close(self):
        self.capture.release()
