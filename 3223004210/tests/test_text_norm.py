# 覆盖 src/text_norm.py：normalize / char_ngrams / counts
# 函数名与测试用例ID一一对应
import pytest

from src.text_norm import char_ngrams, counts, normalize


def test_TEXTNORM_R001_001_normalize_bom_and_whitespace():
    # 目的：去除 BOM、裁剪首尾空白、压缩中间空白为单空格
    s = "\ufeff  A \nB\tC  "
    assert normalize(s) == "A B C"


def test_TEXTNORM_R001_002_normalize_preserve_punctuation():
    # 目的：规范化不应删除标点，仅压缩空白
    assert normalize(" A,B.C ") == "A,B.C"


def test_TEXTNORM_R001_003_char_ngrams_ok():
    # 目的：正常提取 2-gram
    assert char_ngrams("今天晴", n=2) == ["今天", "天晴"]


def test_TEXTNORM_R001_004_char_ngrams_too_short_returns_empty():
    # 目的：长度 < n 返回空列表
    assert char_ngrams("天", n=2) == []


def test_TEXTNORM_R001_005_char_ngrams_invalid_n_raises():
    # 目的：n<=0 应抛 ValueError
    with pytest.raises(ValueError):
        char_ngrams("abc", n=0)


def test_TEXTNORM_R001_006_counts_basic():
    # 目的：计数字典正确
    assert counts(["今", "今", "天"]) == {"今": 2, "天": 1}
