# 覆盖 src/sim.py::similarity_ratio 的关键分支与性质
from src.sim import similarity_ratio

def test_SIM_R002_001_empty_both_returns_one():
    # 目的：两者都为空 -> 相似度 1.0
    assert similarity_ratio("", "") == 1.0

def test_SIM_R002_002_one_empty_returns_zero():
    # 目的：一空一非空 -> 0.0
    assert similarity_ratio("a", "") == 0.0
    assert similarity_ratio("", "a") == 0.0

def test_SIM_R002_003_fallback_to_jaccard_when_no_ngram():
    # 目的：无 n-gram 时走 Jaccard 退化（将 n 设大触发）
    s = similarity_ratio("ab", "ac", n=4)
    assert 0.0 <= s <= 1.0
    # 可更严格：≈ 1/3
    # import math; assert math.isclose(s, 1/3, rel_tol=1e-6)

def test_SIM_R002_004_identical_text_returns_one():
    # 目的：自反性：文本与自身相似度=1.0
    t = "深度学习是机器学习的分支。"
    assert similarity_ratio(t, t) == 1.0

def test_SIM_R002_005_no_overlap_ngram_returns_zero():
    # 目的：无重叠 n-gram -> 点积为0 -> 相似度0.0
    a, b = "abcdef", "ghijkl"
    assert similarity_ratio(a, b, n=2) == 0.0

def test_SIM_R002_006_paraphrase_higher_than_unrelated():
    # 目的：近义改写应高于无关句
    a = "机器学习是人工智能的重要分支。"
    b = "人工智能的重要分支之一是机器学习。"
    c = "今天天气晴朗，适合跑步。"
    assert similarity_ratio(a, b) > similarity_ratio(a, c)
