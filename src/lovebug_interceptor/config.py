import math
import tomllib
from dataclasses import asdict, dataclass, field, fields
from pathlib import Path


@dataclass(frozen=True)
class CameraConfig:
    device: str = "/dev/v4l/by-id/usb-046d_C270_HD_WEBCAM_11319900-video-index0"
    width: int = 1280
    height: int = 720
    fps: float = 30.0
    fourcc: str = "MJPG"


@dataclass(frozen=True)
class DetectorConfig:
    history: int = 300
    variance_threshold: float = 16.0
    warmup_frames: int = 30
    min_area: int = 4
    max_area: int = 2500


@dataclass(frozen=True)
class TrackerConfig:
    max_distance_px: float = 60.0
    max_missed_frames: int = 10


@dataclass(frozen=True)
class OutputConfig:
    directory: str = "data/runs"


@dataclass(frozen=True)
class Config:
    camera: CameraConfig = field(default_factory=CameraConfig)
    detector: DetectorConfig = field(default_factory=DetectorConfig)
    tracker: TrackerConfig = field(default_factory=TrackerConfig)
    output: OutputConfig = field(default_factory=OutputConfig)

    def as_dict(self):
        return asdict(self)


def load_config(path: Path | None = None) -> Config:
    content = tomllib.loads(path.read_text()) if path else {}
    sections = {
        "camera": CameraConfig,
        "detector": DetectorConfig,
        "tracker": TrackerConfig,
        "output": OutputConfig,
    }
    if content.keys() - sections.keys():
        raise ValueError("Unknown configuration section")
    values = {}
    for section, constructor in sections.items():
        supplied = content.get(section, {})
        if not isinstance(supplied, dict):
            raise ValueError(f"{section} must be a table")
        defaults = constructor()
        allowed = {item.name for item in fields(defaults)}
        if supplied.keys() - allowed:
            raise ValueError(f"Unknown setting in {section}")
        for name, value in supplied.items():
            expected = type(getattr(defaults, name))
            if expected is float:
                valid = type(value) in (int, float) and math.isfinite(value)
            else:
                valid = type(value) is expected
            if not valid:
                raise ValueError(f"Invalid type or value for {section}.{name}")
        values[section] = constructor(**supplied)
    config = Config(**values)
    for name in ("width", "height", "fps"):
        if getattr(config.camera, name) <= 0:
            raise ValueError(f"camera.{name} must be positive")
    if not config.camera.device or len(config.camera.fourcc) != 4:
        raise ValueError("Camera requires a device and a four-character codec")
    detector = config.detector
    if detector.history <= 0 or detector.variance_threshold <= 0:
        raise ValueError("Detector history and variance threshold must be positive")
    if detector.warmup_frames < 0 or not 0 < detector.min_area <= detector.max_area:
        raise ValueError("Invalid detector warmup or area limits")
    if config.tracker.max_distance_px <= 0 or config.tracker.max_missed_frames < 0:
        raise ValueError("Invalid tracker distance or expiry")
    if not config.output.directory.strip():
        raise ValueError("Output directory cannot be empty")
    return config
