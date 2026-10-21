from dataclasses import dataclass

import cv2
import numpy as np

from .config import DetectorConfig


@dataclass(frozen=True)
class Detection:
    x: int
    y: int
    width: int
    height: int

    @property
    def centroid(self) -> tuple[float, float]:
        return self.x + self.width / 2, self.y + self.height / 2


class MotionDetector:
    def __init__(self, config: DetectorConfig):
        self.config = config
        self.frames_seen = 0
        self.background = cv2.createBackgroundSubtractorMOG2(
            history=config.history,
            varThreshold=config.variance_threshold,
            detectShadows=False,
        )

    def detect(self, frame: np.ndarray) -> list[Detection]:
        mask = self.background.apply(cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY))
        self.frames_seen += 1
        if self.frames_seen <= self.config.warmup_frames:
            return []
        count, _, stats, _ = cv2.connectedComponentsWithStats(mask)
        detections = []
        for index in range(1, count):
            left, top, width, height, area = stats[index]
            if self.config.min_area <= area <= self.config.max_area:
                detections.append(Detection(int(left), int(top), int(width), int(height)))
        return detections
