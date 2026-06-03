"""Proof asset contract for the semantic director boundary."""
from __future__ import annotations

import json
import re
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[3]
DEFAULT_PROOF_ASSET_PATH = REPO_ROOT / "samples" / "proofs" / "default_ai_content_system.yaml"

GENERIC_PROOF_PHRASES = {
    "真实案例",
    "已验证",
    "可复用",
    "经验",
    "已经跑通",
    "已经跑通过",
    "案例",
    "实例",
}
FAKE_METRIC_MARKERS = {
    "1000%",
    "999%",
    "暴涨",
    "保证",
    "绝对",
    "秒杀",
    "永久",
}


@dataclass(frozen=True)
class ProofAsset:
    asset_id: str
    claim_supported: str
    evidence_items: tuple[str, ...]
    metric_source: str
    credibility_note: str
    factual_boundaries: tuple[str, ...]

    def as_dict(self) -> dict[str, Any]:
        return {
            "asset_id": self.asset_id,
            "claim_supported": self.claim_supported,
            "evidence_items": list(self.evidence_items),
            "metric_source": self.metric_source,
            "credibility_note": self.credibility_note,
            "factual_boundaries": list(self.factual_boundaries),
        }


def _coerce_proof_asset(data: dict[str, Any]) -> ProofAsset:
    asset_id = str(data.get("asset_id") or "default_ai_content_system_proof").strip()
    claim_supported = str(data.get("claim_supported") or "系统先跑通，再谈扩展").strip()
    evidence_items = tuple(
        str(item).strip()
        for item in data.get("evidence_items", [])
        if str(item).strip()
    )
    metric_source = str(data.get("metric_source") or "preview_report / sync_report / scene_pack").strip()
    credibility_note = str(data.get("credibility_note") or "有执行记录，非空话").strip()
    factual_boundaries = tuple(
        str(item).strip()
        for item in data.get("factual_boundaries", [])
        if str(item).strip()
    )
    return ProofAsset(
        asset_id=asset_id,
        claim_supported=claim_supported,
        evidence_items=evidence_items,
        metric_source=metric_source,
        credibility_note=credibility_note,
        factual_boundaries=factual_boundaries,
    )


def validate_proof_asset(data: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    required = ("asset_id", "claim_supported", "evidence_items", "metric_source", "credibility_note", "factual_boundaries")
    for field in required:
        if field not in data:
            errors.append(f"missing field {field!r}")
    if not isinstance(data.get("evidence_items"), list):
        errors.append("evidence_items must be a list")
    if not isinstance(data.get("factual_boundaries"), list):
        errors.append("factual_boundaries must be a list")
    return errors


@lru_cache(maxsize=1)
def load_default_proof_asset(path: str | Path = DEFAULT_PROOF_ASSET_PATH) -> ProofAsset:
    raw_path = Path(path)
    if raw_path.exists():
        data = json.loads(raw_path.read_text(encoding="utf-8"))
        return _coerce_proof_asset(data)
    return _coerce_proof_asset({})


def proof_metric_is_suspicious(text: str) -> bool:
    normalized = text.strip()
    if not normalized:
        return False
    if any(marker in normalized for marker in FAKE_METRIC_MARKERS):
        return True
    if re.search(r"\b\d{3,}\s*[%倍次]\b", normalized):
        return True
    if re.search(r"\b\d{2,}\s*(?:天|周|小时|分钟)\b", normalized) and any(term in normalized for term in ("保证", "绝对", "必定")):
        return True
    return False

