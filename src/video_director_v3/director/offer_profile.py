"""Offer profile contract for the semantic director boundary."""
from __future__ import annotations

import json
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[3]
DEFAULT_OFFER_PROFILE_PATH = REPO_ROOT / "samples" / "offers" / "default_ai_content_system.yaml"


@dataclass(frozen=True)
class OfferProfile:
    profile_id: str
    target_user: str
    core_promise: str
    delivery_shape: str
    risk_reversal: str
    next_step: str
    prohibited_cta: tuple[str, ...]

    def as_dict(self) -> dict[str, Any]:
        return {
            "profile_id": self.profile_id,
            "target_user": self.target_user,
            "core_promise": self.core_promise,
            "delivery_shape": self.delivery_shape,
            "risk_reversal": self.risk_reversal,
            "next_step": self.next_step,
            "prohibited_cta": list(self.prohibited_cta),
        }


def _coerce_offer_profile(data: dict[str, Any]) -> OfferProfile:
    profile_id = str(data.get("profile_id") or "default_ai_content_system").strip()
    target_user = str(data.get("target_user") or "需要把内容流程接成闭环的创作者").strip()
    core_promise = str(data.get("core_promise") or "先跑通一个最小成交流程，再继续优化").strip()
    delivery_shape = str(data.get("delivery_shape") or "文案 -> TTS -> 预览 -> 确认 -> 发布").strip()
    risk_reversal = str(data.get("risk_reversal") or "先用最小闭环验证，再逐步扩展").strip()
    next_step = str(data.get("next_step") or "先做一版最小成交流程").strip()
    prohibited = tuple(
        str(item).strip()
        for item in data.get("prohibited_cta", [])
        if str(item).strip()
    )
    return OfferProfile(
        profile_id=profile_id,
        target_user=target_user,
        core_promise=core_promise,
        delivery_shape=delivery_shape,
        risk_reversal=risk_reversal,
        next_step=next_step,
        prohibited_cta=prohibited,
    )


def validate_offer_profile(data: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    required = ("profile_id", "target_user", "core_promise", "delivery_shape", "risk_reversal", "next_step", "prohibited_cta")
    for field in required:
        if field not in data:
            errors.append(f"missing field {field!r}")
    if not isinstance(data.get("prohibited_cta"), list):
        errors.append("prohibited_cta must be a list")
    return errors


@lru_cache(maxsize=1)
def load_default_offer_profile(path: str | Path = DEFAULT_OFFER_PROFILE_PATH) -> OfferProfile:
    raw_path = Path(path)
    if raw_path.exists():
        data = json.loads(raw_path.read_text(encoding="utf-8"))
        return _coerce_offer_profile(data)
    return _coerce_offer_profile({})

