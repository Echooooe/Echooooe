# sim.py
import math
from typing import Dict, Set
from .text_norm import normalize, char_ngrams, counts

def _dot(a: Dict[str, int], b: Dict[str, int]) -> int:
    """
    稀疏向量点积： sum_i (a[i] * b[i])
    只遍历更短的那个字典，减少哈希查找次数，提高常数效率。
    """
    if len(a) > len(b):
        a, b = b, a  # 交换，确保遍历更小的那个
    return sum(v * b.get(k, 0) for k, v in a.items())

def _norm(a: Dict[str, int]) -> float:
    """
    向量 L2 范数：sqrt(sum_i (a[i]^2))
    """
    return math.sqrt(sum(v*v for v in a.values()))

def _jaccard_chars(a: str, b: str) -> float:
    """
    字符集合的 Jaccard 相似度：
    |set(a) ∩ set(b)| / |set(a) ∪ set(b)|
    适用于 n-gram 无法工作的极短文本场景。
    边界：
      - 两者皆空 => 定义为 1.0（皆无信息视为相同）
      - 一空一非空 => 0.0
    """
    sa: Set[str] = set(a)
    sb: Set[str] = set(b)
    if not sa and not sb:
        return 1.0
    if not sa or not sb:
        return 0.0
    inter = len(sa & sb)
    union = len(sa | sb)
    return inter / union if union else 0.0  # 正常不会出现 union=0

def similarity_ratio(orig: str, copy: str, n: int = 2) -> float:
    """
    计算两段文本的相似度（0.0 ~ 1.0）：
    1) 规范化文本（normalize）
    2) 若两者都为空 -> 1.0；若有一空 -> 0.0
    3) 提取 n-gram（默认 2）
    4) 若任一没有 n-gram（文本过短） -> 退化为字符集合 Jaccard
    5) 否则计算 n-gram 计数字典的余弦相似度： dot / (normA * normB)
    """
    # 先规范化，降低格式差异影响（空白/换行/前后空格）
    A = normalize(orig)
    B = normalize(copy)

    # 边界：两者都空 -> 1.0；有一边空 -> 0.0
    if not A and not B:
        return 1.0
    if not A or not B:
        return 0.0

    # 生成 n-gram 序列
    toksA = char_ngrams(A, n=n)
    toksB = char_ngrams(B, n=n)

    # 若任意一边由于过短导致没有 n-gram，则使用 Jaccard 退化方案
    if not toksA or not toksB:
        return _jaccard_chars(A, B)

    # 计数字典（稀疏向量）
    cA = counts(toksA)
    cB = counts(toksB)

    # 余弦相似度 = 点积 / (范数A * 范数B)
    num = _dot(cA, cB)
    den = _norm(cA) * _norm(cB)
    return (num / den) if den != 0 else 0.0  # 理论上 den 不会为 0，这里防御性返回 0.0
