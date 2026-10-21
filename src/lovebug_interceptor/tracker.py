from dataclasses import dataclass
from math import dist

from .config import TrackerConfig
from .detector import Detection


@dataclass
class Track:
    track_id: int
    detection: Detection
    missed_frames: int = 0


class CentroidTracker:
    def __init__(self, config: TrackerConfig):
        self.config = config
        self.tracks: dict[int, Track] = {}
        self.next_id = 1

    def update(self, detections: list[Detection]) -> list[Track]:
        matches = sorted(
            (dist(track.detection.centroid, detection.centroid), track_id, detection_index)
            for track_id, track in self.tracks.items()
            for detection_index, detection in enumerate(detections)
        )
        matched_tracks = set()
        matched_detections = set()
        for distance, track_id, detection_index in matches:
            if distance > self.config.max_distance_px:
                break
            if track_id in matched_tracks or detection_index in matched_detections:
                continue
            track = self.tracks[track_id]
            track.detection = detections[detection_index]
            track.missed_frames = 0
            matched_tracks.add(track_id)
            matched_detections.add(detection_index)
        for track_id in list(self.tracks):
            if track_id not in matched_tracks:
                self.tracks[track_id].missed_frames += 1
                if self.tracks[track_id].missed_frames > self.config.max_missed_frames:
                    del self.tracks[track_id]
        for detection_index, detection in enumerate(detections):
            if detection_index not in matched_detections:
                self.tracks[self.next_id] = Track(self.next_id, detection)
                self.next_id += 1
        return [track for track in self.tracks.values() if track.missed_frames == 0]
