from __future__ import annotations

import pytest
from pydantic import ValidationError

from app.schemas.task import TaskUploadRequest


class TestTaskUploadRequest:
    def test_valid_request(self):
        req = TaskUploadRequest(model="yolo", mode="sync")
        assert req.model == "yolo"
        assert req.mode == "sync"

    def test_invalid_model(self):
        with pytest.raises(ValidationError):
            TaskUploadRequest(model="invalid")

    def test_confidence_threshold_range(self):
        req = TaskUploadRequest(model="yolo", confidence_threshold=0.5)
        assert req.confidence_threshold == 0.5

    def test_confidence_out_of_range(self):
        with pytest.raises(ValidationError):
            TaskUploadRequest(model="yolo", confidence_threshold=1.5)

    def test_confidence_negative(self):
        with pytest.raises(ValidationError):
            TaskUploadRequest(model="yolo", confidence_threshold=-0.1)
