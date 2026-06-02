from __future__ import annotations

import importlib
import logging

logger = logging.getLogger(__name__)

_OPTIONAL_MODELS: dict[str, dict] = {
    "rembg": {
        "packages": ["rembg"],
        "install_cmd": "pip install 'rembg[gpu]'",
        "description": "Background removal (rembg + onnxruntime)",
        "gpu_install_cmd": "pip install 'rembg[gpu]' onnxruntime-gpu",
    },
    "ocr": {
        "packages": ["paddleocr"],
        "install_cmd": "pip install paddlepaddle-gpu paddleocr",
        "description": "Text recognition (PaddleOCR + PaddlePaddle)",
        "cpu_install_cmd": "pip install paddlepaddle paddleocr",
    },
}


def check_optional_dependencies() -> dict[str, bool]:
    """Check which optional model dependencies are installed.

    Returns a dict mapping model_type -> available (True/False).
    Never raises — missing packages only produce warnings.
    """
    availability: dict[str, bool] = {"yolo": True}

    for model_type, info in _OPTIONAL_MODELS.items():
        all_found = True
        for pkg_name in info["packages"]:
            try:
                importlib.import_module(pkg_name)
            except ImportError:
                all_found = False
                break

        if all_found:
            logger.info(f"Optional model '{model_type}' is available ({info['description']}).")
        else:
            logger.warning(
                f"Optional model '{model_type}' ({info['description']}) is NOT available. "
                f"Install with: {info['install_cmd']}"
            )
            logger.warning(
                f"After installing, restart the server to enable '{model_type}' inference."
            )

        availability[model_type] = all_found

    return availability


def get_install_command(model_type: str) -> str | None:
    """Return the install command for a missing model, or None if it should always be available."""
    info = _OPTIONAL_MODELS.get(model_type)
    if info is None:
        return None
    return info["install_cmd"]


def get_model_description(model_type: str) -> str:
    """Return a human-readable description of the model."""
    info = _OPTIONAL_MODELS.get(model_type)
    if info is None:
        return model_type
    return info["description"]
