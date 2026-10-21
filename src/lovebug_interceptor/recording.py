import csv
import json
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

import cv2


class Recording:
    def __init__(self, root: Path):
        name = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ") + "-" + uuid4().hex[:8]
        self.directory = root / name
        self.directory.mkdir(parents=True)
        self.writers = []
        self.csv_file = None
        self.csv_writer = None

    def start(self, frame, fps: float):
        height, width = frame.shape[:2]
        for filename in ("raw.avi", "annotated.avi"):
            writer = cv2.VideoWriter(
                str(self.directory / filename),
                cv2.VideoWriter_fourcc(*"MJPG"),
                fps,
                (width, height),
            )
            self.writers.append(writer)
            if not writer.isOpened():
                raise ValueError(
                    f"Cannot create {filename}; MJPEG encoder or output is unavailable"
                )
        self.csv_file = (self.directory / "tracks.csv").open("w", newline="")
        self.csv_writer = csv.writer(self.csv_file)
        self.csv_writer.writerow(
            [
                "frame_number",
                "timestamp",
                "track_id",
                "x_px",
                "y_px",
                "bbox_x",
                "bbox_y",
                "width_px",
                "height_px",
            ]
        )

    def write(self, raw, annotated, frame_number: int, timestamp: float, tracks):
        self.writers[0].write(raw)
        self.writers[1].write(annotated)
        for track in tracks:
            detection = track.detection
            self.csv_writer.writerow(
                [
                    frame_number,
                    f"{timestamp:.6f}",
                    track.track_id,
                    *detection.centroid,
                    detection.x,
                    detection.y,
                    detection.width,
                    detection.height,
                ]
            )

    def metadata(self, values):
        (self.directory / "metadata.json").write_text(json.dumps(values, indent=2) + "\n")

    def close(self):
        for writer in self.writers:
            writer.release()
        if self.csv_file:
            self.csv_file.close()
