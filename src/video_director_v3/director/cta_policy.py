"""CTA policy contract for the semantic director boundary."""
from __future__ import annotations

import json
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[3]
DEFAULT_CTA_POLICY_PATH = REPO_ROOT / "samples" / "cta" / "default_value_first.yaml"

FORBIDDEN_DEFAULT_PHRASES = (
    "评论区打关键词领取资料",
    "私信领取资料",
    "评论区回复领取",
    "评论区打字领取",
)


@dataclass(frozen=True)
class CtaPolicy:
    policy_id: str
    preferred_cta_text: str
    forbidden_phrases: tuple[str, ...]
    min_proof_scenes_before_final_cta: int
    max_cta_scenes: int
    early_cta_ratio: float
    strong_cta_ratio: float
    repeated_cta_soft_limit: int

    def as_dict(self) -> dict[str, Any]:
        return {
            "policy_id": self.policy_id,
            "preferred_cta_text": self.preferred_cta_text,
            "forbidden_phrases": list(self.forbidden_phrases),
            "min_proof_scenes_before_final_cta": self.min_proof_scenes_before_final_cta,
            "max_cta_scenes": self.max_cta_scenes,
            "early_cta_ratio": self.early_cta_ratio,
            "strong_cta_ratio": self.strong_cta_ratio,
            "repeated_cta_soft_limit": self.repeated_cta_soft_limit,
        }


def _coerce_cta_policy(data: dict[str, Any]) -> CtaPolicy:
    policy_id = str(data.get("policy_id") or "default_value_first").strip()
    preferred_cta_text = str(data.get("preferred_cta_text") or "先跑一版最小成交流程").strip()
    forbidden_phrases = tuple(
        str(item).strip()
        for item in data.get("forbidden_phrases", FORBIDDEN_DEFAULT_PHRASES)
        if str(item).strip()
    ) or FORBIDDEN_DEFAULT_PHRASES
    min_proof = int(data.get("min_proof_scenes_before_final_cta") or 1)
    max_cta = int(data.get("max_cta_scenes") or 4)
    early_ratio = float(data.get("early_cta_ratio") or 0.35)
    strong_ratio = float(data.get("strong_cta_ratio") or 0.8)
    repeated_soft_limit = int(data.get("repeated_cta_soft_limit") or 2)
    return CtaPolicy(
        policy_id=policy_id,
        preferred_cta_text=preferred_cta_text,
        forbidden_phrases=forbidden_phrases,
        min_proof_scenes_before_final_cta=min_proof,
        max_cta_scenes=max_cta,
        early_cta_ratio=early_ratio,
        strong_cta_ratio=strong_ratio,
        repeated_cta_soft_limit=repeated_soft_limit,
    )


def validate_cta_policy(data: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    required = (
        "policy_id",
        "preferred_cta_text",
        "forbidden_phrases",
        "min_proof_scenes_before_final_cta",
        "max_cta_scenes",
        "early_cta_ratio",
        "strong_cta_ratio",
        "repeated_cta_soft_limit",
    )
    for field in required:
        if field not in data:
            errors.append(f"missing field {field!r}")
    if not isinstance(data.get("forbidden_phrases"), list):
        errors.append("forbidden_phrases must be a list")
    return errors


@lru_cache(maxsize=1)
def load_default_cta_policy(path: str | Path = DEFAULT_CTA_POLICY_PATH) -> CtaPolicy:
    raw_path = Path(path)
    if raw_path.exists():
        data = json.loads(raw_path.read_text(encoding="utf-8"))
        return _coerce_cta_policy(data)
    return _coerce_cta_policy({})

