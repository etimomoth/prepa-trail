from __future__ import annotations

import threading
from functools import lru_cache
from typing import Any

import torch

from app.core.config import settings
from app.core.logging import get_logger

log = get_logger(__name__)

_clip_lock = threading.Lock()
_clip_state: dict[str, Any] = {}


def select_device() -> torch.device:
    if torch.cuda.is_available():
        return torch.device("cuda")
    if getattr(torch.backends, "mps", None) and torch.backends.mps.is_available():
        return torch.device("mps")
    return torch.device("cpu")


@lru_cache(maxsize=1)
def device() -> torch.device:
    d = select_device()
    log.info("ML device selected: %s", d)
    return d


def load_clip() -> dict[str, Any]:
    """Return cached dict with {model, preprocess, tokenizer, device}. Lazy import."""
    import open_clip

    with _clip_lock:
        if _clip_state:
            return _clip_state
        dev = device()
        log.info("loading CLIP %s/%s", settings.clip_model, settings.clip_pretrained)
        model, _, preprocess = open_clip.create_model_and_transforms(
            settings.clip_model, pretrained=settings.clip_pretrained
        )
        tokenizer = open_clip.get_tokenizer(settings.clip_model)
        model = model.to(dev).eval()
        if settings.clip_fp16 and dev.type == "cuda":
            model = model.half()
        _clip_state.update(
            {"model": model, "preprocess": preprocess, "tokenizer": tokenizer, "device": dev}
        )
        return _clip_state
