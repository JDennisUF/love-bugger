from dataclasses import replace

import numpy as np
import pytest

from lovebug_interceptor.config import DetectorConfig, TrackerConfig, load_config
from lovebug_interceptor.detector import Detection, MotionDetector
from lovebug_interceptor.tracker import CentroidTracker


@pytest.mark.parametrize(
    "content",
    [
        "[camera]\nfps = -1",
        "[camera]\nwidth = true",
        "[camera]\nfps = nan",
        "[camera]\nunknown = 1",
        "[detector]\nmin_area = 20\nmax_area = 10",
        "[tracker]\nmax_missed_frames = -1",
        "[output]\ndirectory = ''",
        "[unknown]",
    ],
)
def test_invalid_configuration(tmp_path, content):
    path = tmp_path / "invalid.toml"
    path.write_text(content)
    with pytest.raises(ValueError):
        load_config(path)


def test_example_configuration_loads():
    from pathlib import Path

    config = load_config(Path(__file__).resolve().parents[1] / "config/example.toml")
    assert config.camera.width == 1280
    assert config.camera.fps == 30


def test_motion_detection_warmup_and_size_filter():
    detector = MotionDetector(DetectorConfig(warmup_frames=5, min_area=4, max_area=100))
    background = np.zeros((80, 120, 3), dtype=np.uint8)
    for _ in range(5):
        assert detector.detect(background) == []
    assert detector.detect(background) == []
    frame = background.copy()
    frame[20:26, 30:36] = 255
    frame[0, 0] = 255
    frame[40:60, 70:90] = 255
    assert detector.detect(frame) == [Detection(30, 20, 6, 6)]


def test_tracker_assigns_each_detection_once_and_preserves_ids():
    tracker = CentroidTracker(TrackerConfig(max_distance_px=20))
    first = tracker.update([Detection(0, 0, 4, 4), Detection(15, 0, 4, 4)])
    assert [track.track_id for track in first] == [1, 2]
    moved = tracker.update([Detection(2, 0, 4, 4), Detection(13, 0, 4, 4)])
    assert [(track.track_id, track.detection.x) for track in moved] == [(1, 2), (2, 13)]
    single = tracker.update([Detection(7, 0, 4, 4)])
    assert len(single) == 1
    assert len(tracker.tracks) == 2


def test_tracker_dropout_expiry_and_distance_gate():
    tracker = CentroidTracker(TrackerConfig(max_distance_px=10, max_missed_frames=1))
    detection = Detection(10, 10, 5, 5)
    assert tracker.update([detection])[0].track_id == 1
    assert tracker.update([]) == []
    assert tracker.update([replace(detection, x=12)])[0].track_id == 1
    assert tracker.update([replace(detection, x=90)])[0].track_id == 2
    tracker.update([])
    assert 1 not in tracker.tracks
    tracker.update([])
    assert tracker.tracks == {}
