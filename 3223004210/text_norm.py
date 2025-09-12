# text_norm.py
import re
from typing import List, Dict

# 用一个预编译的正则来把多个空白（空格、换行、制表符等）压缩成单个空格
_SPACE_RE = re.compile(r"\s+")

def normalize(text: str) -> str:
    """
    文本规范化：
    1) 去除 BOM（\ufeff）
    2) 去首尾空白
    3) 将任何连续空白压缩为一个空格
    不过度删标点，保留语义特征。
    """
    # 有些 UTF-8 带 BOM 的文件，开头会出现 \ufeff
    t = text.replace("\ufeff", "")
    # 去首尾空白，避免两端多余换行/空格
    t = t.strip()
    # 将中间任何空白（空格、换行、制表）压缩为一个空格
    t = _SPACE_RE.sub(" ", t)
    return t

def char_ngrams(text: str, n: int = 2) -> List[str]:
    """
    基于字符的 n-gram 提取：
    给定字符串 text，提取长度为 n 的所有连续子串。
    例如：text="今天晴"、n=2 -> ["今天", "天晴"]
    返回:
        n-gram 列表；若文本长度 < n，则返回空列表（由上层决定如何退化处理）
    """
    if n <= 0:
        # 约束 n 必须为正；防止错误参数导致逻辑异常或死循环
        raise ValueError("n must be positive")
    if len(text) < n:
        return []
    # 经典滑窗：从 0 到 len(text)-n，逐字符取长度 n 的片段
    return [text[i:i+n] for i in range(len(text) - n + 1)]

def counts(tokens: List[str]) -> Dict[str, int]:
    """
    将 n-gram 列表转成“计数字典”（稀疏向量的表现形式）
    例如：["今天","今天","天晴"] -> {"今天":2, "天晴":1}
    """
    d: Dict[str, int] = {}
    for tk in tokens:
        d[tk] = d.get(tk, 0) + 1  # d.get(tk,0) 取不存在时的默认 0
    return d
