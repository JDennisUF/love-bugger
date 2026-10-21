import csv
import json
from dataclasses import replace

import cv2
import numpy as np
import pytest

from lovebug_interceptor.camera import VideoSource
from lovebug_interceptor.config import Config, DetectorConfig
from lovebug_interceptor.main import main, run


@pytest.fixture
def video(tmp_path):
    path = tmp_path / "input.avi"
    writer = cv2.VideoWriter(str(path), cv2.VideoWriter_fourcc(*"MJPG"), 20, (160, 100))
    assert writer.isOpened(), "Test requires MJPEG support"
    try:
        for frame_number in range(40):
            frame = np.zeros((100, 160, 3), dtype=np.uint8)
            if frame_number >= 10:
                left = 10 + (frame_number - 10) * 3
                frame[40:46, left : left + 6] = 255
            writer.write(frame)
    finally:
        writer.release()
    return path


def test_replay_creates_readable_outputs_and_tracks(video, tmp_path):
    config = replace(Config(), detector=DetectorConfig(warmup_frames=10))
    directory = run(config, video=video, output=tmp_path / "runs", headless=True, notes="test")
    metadata = json.loads((directory / "metadata.json").read_text())
    assert metadata["status"] == "completed"
    assert metadata["mode"] == "perception_only"
    assert metadata["frames_written"] == 40
    assert metadata["notes"] == "test"
    assert metadata["timestamp_basis"] == "media_time"
    with (directory / "tracks.csv").open() as stream:
        rows = list(csv.DictReader(stream))
    assert rows
    assert all(int(row["frame_number"]) >= 10 for row in rows)
    timestamps = [float(row["timestamp"]) for row in rows]
    assert timestamps == sorted(timestamps)
    assert len({row["track_id"] for row in rows}) == 1
    for filename in ("raw.avi", "annotated.avi"):
        capture = cv2.VideoCapture(str(directory / filename))
        try:
            count = 0
            while capture.read()[0]:
                count += 1
            assert count == 40
        finally:
            capture.release()


def test_replay_duration_is_media_time(video, tmp_path):
    directory = run(Config(), video=video, output=tmp_path / "runs", headless=True, duration=0.5)
    metadata = json.loads((directory / "metadata.json").read_text())
    assert metadata["frames_written"] == 10


def test_unusable_media_timestamps_fall_back_to_frame_rate(video):
    source = VideoSource(Config().camera, video)
    original = source.capture

    class MissingTimestamps:
        def read(self):
            return original.read()

        def get(self, _):
            return 0

        def release(self):
            original.release()

    source.capture = MissingTimestamps()
    try:
        assert [source.read()[1] for _ in range(4)] == pytest.approx([0, 0.05, 0.1, 0.15])
    finally:
        source.close()


def test_invalid_source_and_duration(tmp_path, capsys):
    assert main(["replay", str(tmp_path / "missing.avi"), "--headless"]) == 1
    assert "does not exist" in capsys.readouterr().err
    assert main(["live", "--duration", "nan", "--headless"]) == 1
    assert "positive finite" in capsys.readouterr().err


def test_unwritable_output(video, tmp_path):
    destination = tmp_path / "file"
    destination.write_text("not a directory")
    with pytest.raises(OSError):
        run(Config(), video=video, output=destination, headless=True)


def test_encoder_failure_is_reported_and_finalized(video, tmp_path, monkeypatch):
    from lovebug_interceptor import recording

    class FailedWriter:
        released = False

        def __init__(self, *args):
            pass

        def isOpened(self):
            return False

        def release(self):
            self.released = True

    monkeypatch.setattr(recording.cv2, "VideoWriter", FailedWriter)
    with pytest.raises(ValueError, match="MJPEG encoder"):
        run(Config(), video=video, output=tmp_path / "runs", headless=True)
    metadata_path = next((tmp_path / "runs").glob("*/metadata.json"))
    assert json.loads(metadata_path.read_text())["status"] == "failed"


@pytest.mark.parametrize("failure", [KeyboardInterrupt(), ValueError("Camera feed lost")])
def test_interruption_and_feed_loss_close_source(video, tmp_path, monkeypatch, failure):
    from lovebug_interceptor import main as application

    original_read = VideoSource.read
    original_close = VideoSource.close
    closed = []

    def interrupted_read(self):
        if self.frames_read >= 5:
            raise failure
        return original_read(self)

    def close(self):
        closed.append(True)
        original_close(self)

    monkeypatch.setattr(application.VideoSource, "read", interrupted_read)
    monkeypatch.setattr(application.VideoSource, "close", close)
    if isinstance(failure, KeyboardInterrupt):
        directory = run(Config(), video=video, output=tmp_path / "runs", headless=True)
        expected = "interrupted"
    else:
        with pytest.raises(ValueError, match="Camera feed lost"):
            run(Config(), video=video, output=tmp_path / "runs", headless=True)
        directory = next((tmp_path / "runs").iterdir())
        expected = "failed"
    assert closed == [True]
    metadata = json.loads((directory / "metadata.json").read_text())
    assert metadata["status"] == expected
    assert metadata["frames_written"] == 5
