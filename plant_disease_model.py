"""Lightweight local inference for AgroAI Pro plant disease image classification.

Model: MobileNetV2 fine-tuned on PlantVillage, exported to quantized ONNX.
The weights are downloaded from Hugging Face on first use and inference then runs
on the Streamlit server using ONNX Runtime CPU. No inference API is called.
"""
from __future__ import annotations

import os
import tempfile
from pathlib import Path

import numpy as np
import requests
import streamlit as st
from PIL import Image, ImageOps

MODEL_URL = (
    "https://huggingface.co/onnx-community/"
    "mobilenet_v2_1.0_224-plant-disease-identification-ONNX/resolve/main/onnx/model_int8.onnx"
)
MODEL_PATH = Path(tempfile.gettempdir()) / "agroai_plant_disease_model_int8.onnx"

MODEL_CLASSES = [
    "Apple Scab",
    "Apple with Black Rot",
    "Cedar Apple Rust",
    "Healthy Apple",
    "Healthy Blueberry Plant",
    "Cherry with Powdery Mildew",
    "Healthy Cherry Plant",
    "Corn (Maize) with Cercospora and Gray Leaf Spot",
    "Corn (Maize) with Common Rust",
    "Corn (Maize) with Northern Leaf Blight",
    "Healthy Corn (Maize) Plant",
    "Grape with Black Rot",
    "Grape with Esca (Black Measles)",
    "Grape with Isariopsis Leaf Spot",
    "Healthy Grape Plant",
    "Orange with Citrus Greening",
    "Peach with Bacterial Spot",
    "Healthy Peach Plant",
    "Bell Pepper with Bacterial Spot",
    "Healthy Bell Pepper Plant",
    "Potato with Early Blight",
    "Potato with Late Blight",
    "Healthy Potato Plant",
    "Healthy Raspberry Plant",
    "Healthy Soybean Plant",
    "Squash with Powdery Mildew",
    "Strawberry with Leaf Scorch",
    "Healthy Strawberry Plant",
    "Tomato with Bacterial Spot",
    "Tomato with Early Blight",
    "Tomato with Late Blight",
    "Tomato with Leaf Mold",
    "Tomato with Septoria Leaf Spot",
    "Tomato with Spider Mites or Two-spotted Spider Mite",
    "Tomato with Target Spot",
    "Tomato Yellow Leaf Curl Virus",
    "Tomato Mosaic Virus",
    "Healthy Tomato Plant",
]


def _ensure_model_file() -> str:
    """Download a small quantized model file once and reuse it on this server."""
    if MODEL_PATH.exists() and MODEL_PATH.stat().st_size > 1_000_000:
        return str(MODEL_PATH)

    temp_path = MODEL_PATH.with_suffix(".download")
    try:
        with requests.get(MODEL_URL, stream=True, timeout=(15, 180)) as response:
            response.raise_for_status()
            total = 0
            with open(temp_path, "wb") as output:
                for chunk in response.iter_content(chunk_size=1024 * 1024):
                    if chunk:
                        output.write(chunk)
                        total += len(chunk)
        if total < 1_000_000:
            raise RuntimeError("Downloaded model file is unexpectedly small; download may have failed.")
        os.replace(temp_path, MODEL_PATH)
    finally:
        if temp_path.exists():
            try:
                temp_path.unlink()
            except OSError:
                pass
    return str(MODEL_PATH)


@st.cache_resource(show_spinner=False)
def _load_session():
    import onnxruntime as ort

    model_path = _ensure_model_file()
    options = ort.SessionOptions()
    options.intra_op_num_threads = 2
    options.inter_op_num_threads = 1
    return ort.InferenceSession(model_path, sess_options=options, providers=["CPUExecutionProvider"])


def _preprocess(image: Image.Image) -> np.ndarray:
    """Resize and normalize to match the model's documented 224x224 preprocessing."""
    image = ImageOps.exif_transpose(image).convert("RGB")
    width, height = image.size
    scale = 256 / min(width, height)
    resized = image.resize((max(224, round(width * scale)), max(224, round(height * scale)),), Image.Resampling.BILINEAR)
    left = (resized.width - 224) // 2
    top = (resized.height - 224) // 2
    resized = resized.crop((left, top, left + 224, top + 224))

    pixels = np.asarray(resized, dtype=np.float32) / 255.0
    pixels = (pixels - 0.5) / 0.5
    return np.transpose(pixels, (2, 0, 1))[None, ...].astype(np.float32)


def predict_plant_disease(image: Image.Image, top_k: int = 3) -> list[dict[str, float | str]]:
    """Return the highest-scoring PlantVillage classes for a PIL image."""
    session = _load_session()
    input_name = session.get_inputs()[0].name
    outputs = session.run(None, {input_name: _preprocess(image)})
    scores = np.asarray(outputs[0]).reshape(-1).astype(np.float64)

    if len(scores) != len(MODEL_CLASSES):
        raise RuntimeError(
            f"Model returned {len(scores)} scores, but {len(MODEL_CLASSES)} class labels are configured."
        )

    # Some exports return logits and others return probabilities. Handle both.
    if np.all(scores >= 0) and np.isfinite(scores).all() and 0.98 <= scores.sum() <= 1.02:
        probabilities = scores / scores.sum()
    else:
        scores -= np.max(scores)
        exp_scores = np.exp(scores)
        probabilities = exp_scores / exp_scores.sum()

    indices = np.argsort(probabilities)[::-1][:max(1, min(int(top_k), len(MODEL_CLASSES)))]
    return [
        {"label": MODEL_CLASSES[int(index)], "score": float(probabilities[index])}
        for index in indices
    ]
