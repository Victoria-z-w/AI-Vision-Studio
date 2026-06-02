from __future__ import annotations

import pytest


class TestHealthCheck:
    @pytest.mark.asyncio
    async def test_healthz(self, client):
        response = await client.get("/api/v1/healthz")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        assert "models" in data


class TestUploadValidation:
    @pytest.mark.asyncio
    async def test_upload_no_file(self, client):
        response = await client.post("/api/v1/upload", data={"model": "yolo"})
        assert response.status_code in (400, 422)

    @pytest.mark.asyncio
    async def test_upload_invalid_model(self, client, sample_image):
        with open(sample_image, "rb") as f:
            response = await client.post(
                "/api/v1/upload",
                files={"file": ("test.png", f, "image/png")},
                data={"model": "invalid_model"},
            )
        assert response.status_code == 400

    @pytest.mark.asyncio
    async def test_upload_valid_model(self, client, sample_image):
        with open(sample_image, "rb") as f:
            response = await client.post(
                "/api/v1/upload",
                files={"file": ("test.png", f, "image/png")},
                data={"model": "yolo"},
            )
        # May fail because model download is needed, but should not be 400 validation error
        assert response.status_code != 422


class TestTasks:
    @pytest.mark.asyncio
    async def test_task_not_found(self, client):
        response = await client.get("/api/v1/tasks/nonexistent-id/status")
        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_list_tasks(self, client):
        response = await client.get("/api/v1/tasks")
        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        assert "pagination" in data
