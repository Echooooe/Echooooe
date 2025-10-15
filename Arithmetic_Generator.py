#!/usr/bin/env python3
"""
四则运算题目生成与批改程序
用法示例：
  生成题目： python Arithmetic_Generator.py -n 10 -r 10
  批改题目： python Arithmetic_Generator.py -e Exercises.txt -a Answers.txt

输出：
  - 生成模式：Exercises.txt, Answers.txt
  - 批改模式：Grade.txt

说明：
 - 支持自然数与真分数（输出格式：3/5 或 2'3/8 表示带分数）
 - 保证运算中不出现负数，除法结果不为整数
 - 每题运算符不超过3个，题目不重复（+ 和 * 支持交换/结合去重）
 - 最多支持生成 10000 道题目
"""

import argparse
import random
from fractions import Fraction
import sys
import math
import re

MAX_TRIES = 20000  # 最大尝试次数，防止死循环

# ============================================================
# 基础表达式类与其子类：Number, Binary
# ============================================================

class Expr:
    """表达式抽象基类"""
    def eval(self) -> Fraction:
        """计算表达式的结果（以 Fraction 表示）"""
        raise NotImplementedError

    def to_str(self) -> str:
        """将表达式转换为可显示的字符串"""
        raise NotImplementedError

    def canonical(self) -> str:
        """生成用于去重的标准化字符串（对 + 和 * 进行交换、结合归一化）"""
        raise NotImplementedError


class Number(Expr):
    """表示一个数值节点（自然数或分数）"""
    def __init__(self, frac: Fraction):
        self.frac = frac

    def eval(self):
        return self.frac

    def to_str(self):
        """数字节点转字符串"""
        return format_fraction_output(self.frac)

    def canonical(self):
        return self.to_str()


class Binary(Expr):
    """表示二元运算节点（+ - * /）"""
    def __init__(self, op, left: Expr, right: Expr):
        self.op = op
        self.left = left
        self.right = right

    def eval(self):
        """递归计算表达式结果"""
        a = self.left.eval()
        b = self.right.eval()
        if self.op == '+': return a + b
        if self.op == '-': return a - b
        if self.op == '*': return a * b
        if self.op == '/': return a / b
        raise ValueError('unknown op')

    # ---------------- 括号处理辅助函数 ----------------
    def _prec(self, op):
        """运算符优先级"""
        if op in ('+', '-'):
            return 1
        return 2

    def needs_paren_left(self):
        """判断左子表达式是否需要加括号"""
        return isinstance(self.left, Binary) and self._prec(self.left.op) < self._prec(self.op)

    def needs_paren_right(self):
        """判断右子表达式是否需要加括号"""
        return isinstance(self.right, Binary) and self._prec(self.right.op) <= self._prec(self.op)

    def to_str(self):
        """生成表达式字符串，必要时添加括号"""
        l = self.left.to_str()
        r = self.right.to_str()

        # 根据优先级加括号
        if self.needs_paren_left():
            l = f"({l})"
        if self.needs_paren_right():
            r = f"({r})"

        # 新增：当生成形如 a / b/c 时自动加括号 → a / (b/c)
        if self.op == '/' and '/' in r and not r.startswith('('):
            r = f"({r})"

        return f"{l} {self.op} {r}"

    def _flatten(self, op):
        """将同类型运算符的树展开（如 a+(b+c)→[a,b,c]）"""
        res = []
        def collect(node):
            if isinstance(node, Binary) and node.op == op:
                collect(node.left)
                collect(node.right)
            else:
                res.append(node)
        collect(self)
        return res

    def canonical(self):
        """生成用于去重的标准形式字符串"""
        if self.op in ('+', '*'):
            items = self._flatten(self.op)
            can_items = [it.canonical() for it in items]
            can_items_sorted = sorted(can_items)
            return f"({self.op.join(can_items_sorted)})"
        else:
            return f"({self.left.canonical()}{self.op}{self.right.canonical()})"


# ============================================================
# 表达式生成与约束校验
# ============================================================

def gen_number(rng):
    """生成随机数字（自然数或真分数）"""
    if rng <= 1:
        return Number(Fraction(0))
    if random.random() < 0.5:
        # 生成整数 0..rng-1
        return Number(Fraction(random.randint(0, rng - 1), 1))
    else:
        # 生成分数或带分数
        denom = random.randint(2, max(2, rng - 1))
        numer = random.randint(1, denom - 1)
        if random.random() < 0.2:
            # 以一定概率生成带分数
            whole = random.randint(0, max(0, (rng - 1) // denom))
            val = Fraction(whole * denom + numer, denom)
            return Number(val)
        return Number(Fraction(numer, denom))


def validate_tree(node: Expr) -> bool:
    """递归校验表达式是否合法：
       - 不产生负数
       - 除法不为整数且不除以 0"""
    try:
        def dfs(n):
            if isinstance(n, Number):
                return n.eval()
            a = dfs(n.left)
            b = dfs(n.right)
            if n.op == '-':
                if a < b: raise ValueError('negative')
                return a - b
            if n.op == '/':
                if b == 0: raise ValueError('divzero')
                res = a / b
                if res.denominator == 1:  # 排除整除
                    raise ValueError('div_integer')
                return res
            if n.op == '+': return a + b
            if n.op == '*': return a * b
            raise ValueError('op')
        dfs(node)
        return True
    except Exception:
        return False


def gen_expr_with_ops(k, rng):
    """生成包含 k 个运算符的随机表达式"""
    leaves = [gen_number(rng) for _ in range(k + 1)]
    nodes = leaves[:]
    tries = 0

    while len(nodes) > 1 and tries < MAX_TRIES:
        tries += 1
        i, j = random.sample(range(len(nodes)), 2)
        left, right = nodes[i], nodes[j]
        op = random.choice(['+', '-', '*', '/'])
        node = Binary(op, left, right)

        # 处理减法与除法的合法性
        if op == '-':
            if left.eval() < right.eval():
                node = Binary(op, right, left)
                if node.left.eval() < node.right.eval():
                    continue
        if op == '/':
            if right.eval() == 0:
                if left.eval() == 0:
                    continue
                node = Binary(op, right, left)
            a, b = node.left.eval(), node.right.eval()
            if b == 0 or (a / b).denominator == 1:
                continue

        # 删除已合并节点
        for idx in sorted([i, j], reverse=True):
            del nodes[idx]
        nodes.append(node)

    if len(nodes) != 1:
        return None
    root = nodes[0]
    if not validate_tree(root):
        return None
    return root


def generate_exercises(n, rng):
    """生成 n 道符合约束的题目与答案"""
    if n <= 0 or n > 10000:
        raise ValueError('n must be 1..10000')
    exercises, answers, seen = [], [], set()
    tries = 0

    while len(exercises) < n and tries < MAX_TRIES:
        tries += 1
        k = random.randint(1, 3)
        root = gen_expr_with_ops(k, rng)
        if root is None:
            continue
        can = root.canonical()
        if can in seen:
            continue
        seen.add(can)
        exercises.append(root.to_str() + ' =')
        val = root.eval()
        answers.append(format_fraction_output(val))

    if len(exercises) < n:
        raise RuntimeError(f'只生成到 {len(exercises)} 道题（尝试 {tries} 次），请增大范围或放宽约束')
    return exercises, answers


# ============================================================
# 输出格式化与批改逻辑
# ============================================================

def format_fraction_output(fr: Fraction) -> str:
    """将 Fraction 格式化为输出形式（整数 / 真分数 / 带分数）"""
    if fr.denominator == 1:
        return str(fr.numerator)
    n, d = abs(fr.numerator), fr.denominator
    if n > d:
        whole, rem = n // d, n % d
        sign = '-' if fr < 0 else ''
        return f"{sign}{whole}'{rem}/{d}"
    sign = '-' if fr < 0 else ''
    return f"{sign}{n}/{d}"


def grade(exfile, ansfile):
    """批改模式：读取题目与答案文件，逐题比对，输出 Grade.txt"""
    with open(exfile, 'r', encoding='utf-8') as f:
        exercises = [line.strip() for line in f if line.strip()]
    with open(ansfile, 'r', encoding='utf-8') as f:
        answers = [line.strip() for line in f if line.strip()]
    m = min(len(exercises), len(answers))
    correct_idx, wrong_idx = [], []

    for i in range(m):
        line = exercises[i]
        expr_text = line[:-1].strip() if line.endswith('=') else line
        try:
            got = parse_and_eval(expr_text)
            got_str = format_fraction_output(got)
        except Exception:
            got_str = 'ERROR'
        if i < len(answers) and answers[i].strip() == got_str:
            correct_idx.append(i + 1)
        else:
            wrong_idx.append(i + 1)

    for j in range(m, len(answers)):
        wrong_idx.append(j + 1)

    with open('Grade.txt', 'w', encoding='utf-8') as f:
        f.write(f"Correct: {len(correct_idx)} ({', '.join(map(str, correct_idx))})\n\n")
        f.write(f"Wrong: {len(wrong_idx)} ({', '.join(map(str, wrong_idx))})\n")
    print('Grade.txt 已生成')


# ============================================================
# 表达式解析与执行（用于批改）
# ============================================================

TOKEN_REGEX = re.compile(r"(\d+'\d+/\d+|\d+/\d+|\d+|[()+\-*/])")

def parse_and_eval(s: str) -> Fraction:
    """解析题目字符串并计算结果"""
    tokens = TOKEN_REGEX.findall(s.replace(' ', ''))

    # 将带分数转为括号形式 (a + b/c)
    t2 = []
    for tok in tokens:
        if "'" in tok:
            whole, frac = tok.split("'")
            t2.extend(['(', whole, '+'] + [frac] + [')'])
        else:
            t2.append(tok)

    # 将分数字符转换为 Fraction(...) 表达式
    out_tokens = []
    for tok in t2:
        if '/' in tok and tok[0].isdigit():
            n, d = tok.split('/')
            out_tokens.append(f'Fraction({int(n)},{int(d)})')
        elif tok.isdigit():
            out_tokens.append(f'Fraction({int(tok)},1)')
        else:
            out_tokens.append(tok)
    expr = ''.join(out_tokens)

    # 安全求值，仅允许 Fraction 类型
    val = eval(expr, {'Fraction': Fraction})
    return val


# ============================================================
# 主程序入口
# ============================================================

def main():
    """命令行参数解析与模式分发"""
    parser = argparse.ArgumentParser(description='四则运算题目生成与批改')
    parser.add_argument('-n', type=int, help='生成题目个数')
    parser.add_argument('-r', type=int, help='数值范围（自然数和分母上限）')
    parser.add_argument('-e', help='题目文件（批改模式）')
    parser.add_argument('-a', help='答案文件（批改模式）')
    args = parser.parse_args()

    if args.e or args.a:
        if not (args.e and args.a):
            parser.error('使用 -e 批改时必须同时给出 -a')
        grade(args.e, args.a)
        return

    if args.r is None:
        parser.error('生成题目时必须指定 -r 参数')
    if args.n is None:
        parser.error('生成题目时必须指定 -n 参数')

    exercises, answers = generate_exercises(args.n, args.r)
    with open('Exercises.txt', 'w', encoding='utf-8') as f:
        f.writelines(line + '\n' for line in exercises)
    with open('Answers.txt', 'w', encoding='utf-8') as f:
        f.writelines(line + '\n' for line in answers)
    print('Exercises.txt, Answers.txt 已生成')


if __name__ == '__main__':
    main()
