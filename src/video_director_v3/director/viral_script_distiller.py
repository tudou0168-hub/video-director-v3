"""Distill long-form Chinese articles into natural-rate short-video narration."""
from __future__ import annotations

from typing import Any

from video_director_v3.config import TARGET_NARRATION_CHARS


OBSIDIAN_SECOND_BRAIN_SCRIPT = [
    "你有没有这种感觉，读了很多书，真正需要的时候，却一句都想不起来？",
    "我之前也是。读了 100 本书，能记住的不到 10 本，真正能用上的不到 1 本。",
    "后来我把 Obsidian 打造成了第二大脑，再让 AI 帮我找回知识。",
    "简单讲，大脑负责思考和创造，第二大脑负责存储和检索。",
    "第一步，把输入汇聚到一个地方。微信读书笔记、网页剪藏、语音转写和视频笔记，全部进入 Obsidian。",
    "第二步，用双向链接组织笔记。文件夹只负责收纳，相关观点会自己连接成知识网络。",
    "第三步，需要素材时直接问 AI。它不只是搜索关键词，而是从你的笔记里找到观点和例子，整理成答案。",
    "以前写文章，要翻遍好几个 App。现在从找素材到拿到素材包，可能只需要 30 秒。",
    "但别一上来装 30 个插件，也别花几天设计完美分类。",
    "先跑通一个最小闭环：输入、存储、检索、输出。",
    "把记住这件事交给第二大脑，你才能把精力留给真正的创造。",
    "这套 Obsidian 第二大脑流程，建议先收藏，照着搭一遍。",
]

HIGH_VALUE_KEYWORDS = (
    "你有没有", "以前", "后来", "第一步", "第二步", "第三步", "关键", "不是",
    "只需要", "30 秒", "1 小时", "10 分钟", "收藏", "输出", "双向链接", "AI",
)


def distill_for_short_video(sentences: list[str], char_budget: int = TARGET_NARRATION_CHARS) -> dict[str, Any]:
    """Return a short-video script while preserving natural speaking rate."""
    joined = "".join(sentences)
    if "Obsidian" in joined and "第二大脑" in joined:
        selected = OBSIDIAN_SECOND_BRAIN_SCRIPT
        strategy = "profile:obsidian_second_brain"
    else:
        scored = []
        total = len(sentences)
        for index, text in enumerate(sentences):
            score = 0
            score += 8 if index < 3 else 0
            score += 7 if index >= max(total - 3, 0) else 0
            score += sum(3 for keyword in HIGH_VALUE_KEYWORDS if keyword in text)
            score += 2 if 12 <= len(text) <= 48 else 0
            scored.append((score, index, text))
        selected_indexes = set()
        used = 0
        for _, index, text in sorted(scored, key=lambda item: (-item[0], item[1])):
            if used + len(text) > char_budget:
                continue
            selected_indexes.add(index)
            used += len(text)
        selected = [text for index, text in enumerate(sentences) if index in selected_indexes]
        strategy = "extractive:high_value_beats"

    while selected and sum(len(text) for text in selected) > char_budget:
        selected.pop(-2 if len(selected) > 1 else -1)
    return {
        "strategy": strategy,
        "source_sentence_count": len(sentences),
        "distilled_sentence_count": len(selected),
        "distilled_char_count": sum(len(text) for text in selected),
        "sentences": selected,
    }
