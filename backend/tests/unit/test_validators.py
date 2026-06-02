from __future__ import annotations

from io import BytesIO

import pytest
from fastapi import UploadFile

from app.utils.validators import ValidationError, validate_upload


class TestValidateUpload:
    def test_valid_png(self):
        content = b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01"
        file = UploadFile(filename="test.png", file=BytesIO(content))
        data, fmt = validate_upload(file)
        assert fmt == "PNG"
        assert data == content

    def test_rejects_exe_masquerading_as_png(self):
        content = b"MZ\x90\x00\x03\x00"  # EXE magic
        file = UploadFile(filename="test.png", file=BytesIO(content))
        with pytest.raises(ValidationError) as exc:
            validate_upload(file)
        assert "UNSUPPORTED_FORMAT" in str(exc.value.error_code)

    def test_rejects_file_too_large(self):
        # Use a valid PNG header + lots of data
        content = b"\x89PNG\r\n\x1a\n" + b"X" * (21 * 1024 * 1024)  # 21MB
        file = UploadFile(filename="big.png", file=BytesIO(content))
        with pytest.raises(ValidationError) as exc:
            validate_upload(file)
        assert exc.value.error_code == "FILE_TOO_LARGE"

    def test_rejects_unsupported_mime(self):
        content = b"GIF89a\x00\x01\x00\x01"
        file = UploadFile(
            filename="test.gif",
            file=BytesIO(content),
            headers={"content-type": "image/gif"},
        )
        with pytest.raises(ValidationError):
            validate_upload(file)


class TestPreprocessing:
    def test_exif_orientation(self, sample_image):
        from app.preprocessing.pipeline import run_preprocessing
        output_dir = sample_image.parent / "preproc"
        result = run_preprocessing(sample_image, output_dir)
        assert result.exists()
        assert result.suffix == ".png"

    def test_sha256_short(self, sample_image):
        from app.preprocessing.pipeline import compute_sha256_short
        sha = compute_sha256_short(sample_image)
        assert len(sha) == 12
        assert all(c in "0123456789abcdef" for c in sha)
