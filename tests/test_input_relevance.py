"""Test that input relevance score meets threshold."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from video_director_v3.director.input_relevance_evaluator import evaluate_input


def test_input_relevance_score_pass():
    """Test that a reasonable Chinese script passes threshold."""
    script = """
    今天我要分享一个被100万知识工作者验证过的系统。

    你是不是也有这样的困惑？每天忙得不可开交，打开各种工具软件，
    切换来切换去，结果一天下来感觉什么都没完成。

    让我来教你如何用三个步骤，建立你的第二大脑。
    第一步：统一收集，把所有信息都放进Obsidian
    第二步：原子化笔记，把每一条信息变成原子化
    第三步：双向链接，在笔记之间建立连接

    使用这套系统三个月后，平均效率提升40%。
    不是理论，是实测数据。
    """

    result = evaluate_input(script)
    assert result["score"] >= 0.7, f"Expected score >= 0.7, got {result['score']}"
    assert result["suitable"] is True


def test_input_relevance_score_fail_short():
    """Test that a short script fails."""
    script = "短文本。"

    result = evaluate_input(script)
    assert result["score"] < 0.7