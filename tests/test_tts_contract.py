"""Test the P3 audio-first contract."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from video_director_v3.config import DEFAULT_EDGE_TTS_RATE, MAX_NARRATION_SECONDS, MAX_SYNC_DRIFT_SECONDS
from video_director_v3.director.narration_planner import build_narration_plan, clean_text
from video_director_v3.director.storyboard_builder import build_motion_storyboard


def test_audio_first_defaults_to_natural_rate():
    assert DEFAULT_EDGE_TTS_RATE == "+0%"


def test_audio_first_sync_drift_gate():
    assert MAX_SYNC_DRIFT_SECONDS == 1.0
    assert MAX_NARRATION_SECONDS == 150.0


def test_narration_plan_distills_long_script_without_speeding_up_voice():
    sentence = "这是一个需要完整保留的知识点，不能为了固定时长被机械删除。"
    raw_script = "。".join([sentence] * 30) + "。"

    plan = build_narration_plan(raw_script, project_id="audio_first", target_duration=40)

    assert 0 < plan["sentence_count"] < 30
    assert plan["distillation"]["strategy"] == "extractive:high_value_beats"
    assert all(item["text"] == sentence.rstrip("。") for item in plan["sentence_list"])


def test_clean_text_removes_markdown_frontmatter():
    text = "---\ntitle: 不应进入口播\ndate: 2026-05-27\n---\n# 正文标题\n正文内容。"

    cleaned = clean_text(text)

    assert "title:" not in cleaned
    assert "date:" not in cleaned
    assert "正文标题" in cleaned


def test_dynamic_storyboard_uses_audio_timeline_and_changes_scene_count_by_script_length():
    short_sentence = "这是一个简短但完整的知识点。"
    long_script = "。".join(
        [
            "你有没有发现，很多人学了很多，却很难真正拿出来用",
            "真正的问题，不是你不努力，而是知识没有进入一个可检索的系统",
            "第一步，先把输入统一起来",
            "第二步，再把相关观点连成网络",
            "第三步，需要输出时直接从你的笔记里提取素材",
            "这样你写作、做视频、复盘时都不会再从零开始",
            "最后，先收藏这套最小闭环，照着跑一遍",
        ]
    ) + "。"

    short_plan = build_narration_plan(short_sentence * 3, project_id="short_case", target_duration=30)
    long_plan = build_narration_plan(long_script, project_id="long_case", target_duration=90)

    short_timeline = {
        "sentence_timings": [
            {"sentence_id": item["sentence_id"], "text": item["text"], "start": idx * 2.0, "end": (idx + 1) * 2.0, "duration": 2.0}
            for idx, item in enumerate(short_plan["sentence_list"])
        ]
    }
    long_timeline = {
        "sentence_timings": [
            {"sentence_id": item["sentence_id"], "text": item["text"], "start": idx * 3.0, "end": (idx + 1) * 3.0, "duration": 3.0}
            for idx, item in enumerate(long_plan["sentence_list"])
        ]
    }

    short_storyboard = build_motion_storyboard(
        short_plan.get("director_output", {}),
        target_duration=6.0,
        narration_plan=short_plan,
        audio_timeline=short_timeline,
    )
    long_storyboard = build_motion_storyboard(
        long_plan.get("director_output", {}),
        target_duration=21.0,
        narration_plan=long_plan,
        audio_timeline=long_timeline,
    )

    assert len(short_storyboard["scenes"]) >= 2
    assert len(long_storyboard["scenes"]) > len(short_storyboard["scenes"])
    assert short_storyboard["scenes"][-1]["end"] == short_timeline["sentence_timings"][-1]["end"]
    assert long_storyboard["scenes"][-1]["end"] == long_timeline["sentence_timings"][-1]["end"]
    assert all(scene.get("visual_template") for scene in long_storyboard["scenes"])


def test_narration_plan_roles_match_audio_first_obsidian_structure():
    raw_script = "\n".join(
        [
            "# 知识工作者效率倍增指南",
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
    )

    plan = build_narration_plan(raw_script, project_id="obsidian_roles", target_duration=40)
    roles = [item["role"] for item in plan["sentence_list"]]

    assert roles[0] == "hook"
    assert roles[1] == "pain"
    assert "method" in roles[2:7]
    assert roles[7] == "evidence"
    assert roles[10] == "proof"
    assert roles[-1] == "cta"
