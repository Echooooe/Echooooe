#!/usr/bin/env python3
"""
四则运算题目生成与批改程序
用法举例：
  生成题目： python Arithmetic_Generator.py -n 10 -r 10
  批改题目： python Arithmetic_Generator.py -e Exercises.txt -a Answers.txt

输出：Exercises.txt, Answers.txt（生成时）或 Grade.txt（批改时）

说明：
 - 支持自然数和真分数（输出格式：3/5 或 2'3/8 表示带分数）
 - 保证运算过程中不出现负数，保证除法结果非整数（有小数/分数部分）
 - 每题运算符个数不超过3
 - 生成题目不重复（对+和*做交换/结合规范化后去重）
 - 支持生成最多10000题

"""
import argparse
import random
from fractions import Fraction
import sys
import math

MAX_TRIES = 20000

# 表示表达式的结点
class Expr:
    def eval(self) -> Fraction:
        raise NotImplementedError
    def to_str(self) -> str:
        raise NotImplementedError
    def canonical(self) -> str:
        """用于去重：对 + 和 * 做交换与结合的归一化"""
        raise NotImplementedError

class Number(Expr):
    def __init__(self, frac: Fraction):
        self.frac = frac
    def eval(self):
        return self.frac
    def to_str(self):
        # 输出要求：真分数用 3/5，带分数用 2'3/8
        if self.frac.denominator == 1:
            return str(self.frac.numerator)
        n = abs(self.frac.numerator)
        d = self.frac.denominator
        if abs(self.frac) > 1 and n > d:
            # 带分数
            whole = n // d
            rem = n % d
            sign = "-" if self.frac < 0 else ""
            return f"{sign}{whole}'{rem}/{d}"
        else:
            sign = "-" if self.frac < 0 else ""
            return f"{sign}{n}/{d}"
    def canonical(self):
        return self.to_str()

class Binary(Expr):
    def __init__(self, op, left: Expr, right: Expr):
        self.op = op  # '+','-','*','/'
        self.left = left
        self.right = right
    def eval(self):
        a = self.left.eval()
        b = self.right.eval()
        if self.op == '+':
            return a + b
        if self.op == '-':
            return a - b
        if self.op == '*':
            return a * b
        if self.op == '/':
            # assume b != 0
            return a / b
        raise ValueError('unknown op')
    def needs_paren_left(self):
        return isinstance(self.left, Binary) and self._prec(self.left.op) < self._prec(self.op)
    def needs_paren_right(self):
        return isinstance(self.right, Binary) and self._prec(self.right.op) <= self._prec(self.op)
    def _prec(self, op):
        if op in ('+', '-'):
            return 1
        return 2
    def to_str(self):
        l = self.left.to_str()
        r = self.right.to_str()
        if self.needs_paren_left():
            l = f"({l})"
        if self.needs_paren_right():
            r = f"({r})"
        return f"{l} {self.op} {r}"
    def canonical(self):
        # 对于 + 和 *：进行结合（flatten）并对子项排序（按字符串）以消除因为交换或结合造成的重复
        if self.op in ('+', '*'):
            items = self._flatten(self.op)
            # 递归canonical化每一项
            can_items = [it.canonical() for it in items]
            can_items_sorted = sorted(can_items)
            return f"({self.op.join(can_items_sorted)})"
        else:
            return f"({self.left.canonical()}{self.op}{self.right.canonical()})"
    def _flatten(self, op):
        res = []
        def collect(node):
            if isinstance(node, Binary) and node.op == op:
                collect(node.left)
                collect(node.right)
            else:
                res.append(node)
        collect(self)
        return res

# 生成随机数字：自然数或真分数（分母范围 2..range）
def gen_number(rng):
    # 决定是否为整数
    if rng <= 1:
        return Number(Fraction(0))
    if random.random() < 0.5:
        # 整数 0..rng-1
        return Number(Fraction(random.randint(0, rng-1), 1))
    else:
        # 生成分数或带分数
        denom = random.randint(2, max(2, rng-1))
        numer = random.randint(1, denom-1)
        # 有一定概率生成带分数
        if random.random() < 0.2:
            whole = random.randint(0, max(0, (rng-1)//denom ))
            val = Fraction(whole * denom + numer, denom)
            return Number(val)
        return Number(Fraction(numer, denom))

# 检查二叉表达式约束：无负、中间除法结果为分数（非整数）
# 对整棵树进行检验，确保每个子表达式满足约束

def validate_tree(node: Expr) -> bool:
    try:
        # 评估每个子表达式并检查条件
        def dfs(n):
            if isinstance(n, Number):
                return n.eval()
            a = dfs(n.left)
            b = dfs(n.right)
            if n.op == '-':
                if a < b:
                    raise ValueError('negative')
                return a - b
            if n.op == '/':
                if b == 0:
                    raise ValueError('divzero')
                res = a / b
                # 保证结果为分数（非整数）
                if res.denominator == 1:
                    raise ValueError('div_integer')
                return res
            if n.op == '+':
                return a + b
            if n.op == '*':
                return a * b
            raise ValueError('op')
        dfs(node)
        return True
    except Exception:
        return False

# 生成表达式，运算符数量为 k (1..3)

def gen_expr_with_ops(k, rng):
    # 递归构建：随机选择二叉构造直到达到运算符数量
    # 一个简单方法：先生成 k+1 个叶子数字，然后随机把它们两两组合成二叉树，直到剩1个节点
    leaves = [gen_number(rng) for _ in range(k+1)]
    ops = []
    nodes = leaves[:]
    tries = 0
    while len(nodes) > 1 and tries < MAX_TRIES:
        tries += 1
        i = random.randrange(len(nodes))
        j = random.randrange(len(nodes))
        if i == j:
            continue
        left = nodes[i]
        right = nodes[j]
        op = random.choice(['+', '-', '*', '/'])
        # 构造并立即验证局部约束: 若是减法确保 left >= right by value; 若是除法 ensure result non-integer and b !=0
        # 如果不满足，尝试交换 operands for - and / (可能成功)
        node = Binary(op, left, right)
        if op == '-':
            if left.eval() < right.eval():
                # try swap
                node = Binary(op, right, left)
                if node.left.eval() < node.right.eval():
                    continue
        if op == '/':
            # avoid zero
            if right.eval() == 0:
                # try swap
                if left.eval() == 0:
                    continue
                node = Binary(op, right, left)
            # ensure non-integer
            a = node.left.eval()
            b = node.right.eval()
            if b == 0:
                continue
            res = a / b
            if res.denominator == 1:
                # try swap once
                node = Binary(op, node.right, node.left)
                a = node.left.eval(); b = node.right.eval()
                if b == 0 or (a/b).denominator == 1:
                    continue
        # 合法，移除 i,j 并加入节点
        # 删除两个索引，注意顺序
        i2, j2 = sorted([i, j], reverse=True)
        del nodes[i2]
        del nodes[j2]
        nodes.append(node)
    if len(nodes) != 1:
        return None
    root = nodes[0]
    # 最后全树校验（防止中间某处出现负或整除问题）
    if not validate_tree(root):
        return None
    return root

# 生成指定数量的题目，确保不重复

def generate_exercises(n, rng):
    if n <= 0 or n > 10000:
        raise ValueError('n must be 1..10000')
    exercises = []
    answers = []
    seen = set()
    tries = 0
    while len(exercises) < n and tries < MAX_TRIES:
        tries += 1
        k = random.randint(1, 3)  # 运算符个数
        root = gen_expr_with_ops(k, rng)
        if root is None:
            continue
        can = root.canonical()
        if can in seen:
            continue
        seen.add(can)
        exercises.append(root.to_str() + ' =')
        # 答案格式：要把Fraction化为带分数或整数形式
        val = root.eval()
        answers.append(format_fraction_output(val))
    if len(exercises) < n:
        raise RuntimeError(f'只生成到 {len(exercises)} 道题（尝试 {tries} 次），请增大范围或放宽约束')
    return exercises, answers

# 格式化答案：整数 或 带分数 2'3/8 或 真分数 3/5

def format_fraction_output(fr: Fraction) -> str:
    if fr.denominator == 1:
        return str(fr.numerator)
    n = abs(fr.numerator)
    d = fr.denominator
    if n > d:
        whole = n // d
        rem = n % d
        sign = '-' if fr < 0 else ''
        return f"{sign}{whole}'{rem}/{d}"
    sign = '-' if fr < 0 else ''
    return f"{sign}{n}/{d}"

# 批改函数：读取题目文件和答案文件，逐题比较

def grade(exfile, ansfile):
    with open(exfile, 'r', encoding='utf-8') as f:
        exercises = [line.strip() for line in f if line.strip()]
    with open(ansfile, 'r', encoding='utf-8') as f:
        answers = [line.strip() for line in f if line.strip()]
    m = min(len(exercises), len(answers))
    correct_idx = []
    wrong_idx = []
    for i in range(m):
        # 解析题目（去掉末尾的 =）并计算正确答案
        line = exercises[i]
        if line.endswith('='):
            expr_text = line[:-1].strip()
        else:
            expr_text = line
        try:
            got = parse_and_eval(expr_text)
            got_str = format_fraction_output(got)
        except Exception as e:
            got_str = 'ERROR'
        if i < len(answers) and answers[i].strip() == got_str:
            correct_idx.append(i+1)
        else:
            wrong_idx.append(i+1)
    # 若有多余的答案，也标为错误
    for j in range(m, len(answers)):
        wrong_idx.append(j+1)
    # 若题目比答案多，后续题目视为错误（或未作答）
    # 输出 Grade.txt
    with open('Grade.txt', 'w', encoding='utf-8') as f:
        f.write(f"Correct: {len(correct_idx)} ({', '.join(map(str, correct_idx))})\n\n")
        f.write(f"Wrong: {len(wrong_idx)} ({', '.join(map(str, wrong_idx))})\n")
    print('Grade.txt 已生成')

# 一个简单的表达式解析器（只为本题限定格式支持自然数、分数、带分数，四则运算及括号）
import re
TOKEN_REGEX = re.compile(r"(\d+'\d+/\d+|\d+/\d+|\d+|[()+\-*/])")

def parse_and_eval(s: str) -> Fraction:
    tokens = TOKEN_REGEX.findall(s.replace(' ', ''))
    # 将带分数转换为 parenthesized (a + b/c)
    # 简单方法：在遇到带分数 token 2'3/8 将其替换为 (2+3/8)
    t2 = []
    for tok in tokens:
        if "'" in tok:
            whole, frac = tok.split("'")
            t2.extend(['(', whole, '+'] + [frac] + [')'])
        else:
            t2.append(tok)
    # 现在只是实现一个安全的计算：将分数文本转换为 Fraction
    # 我们把所有分数字面量替换为 an eval-friendly form Fraction(n,m) and then evaluate
    out_tokens = []
    for tok in t2:
        if '/' in tok and tok[0].isdigit():
            n,d = tok.split('/')
            out_tokens.append(f'Fraction({int(n)},{int(d)})')
        elif tok.isdigit():
            out_tokens.append(f'Fraction({int(tok)},1)')
        else:
            out_tokens.append(tok)
    expr = ''.join(out_tokens)
    # 为安全，允许运行时仅有 Fraction 在全局命名空间
    val = eval(expr, {'Fraction': Fraction})
    return val


def main():
    parser = argparse.ArgumentParser(description='四则运算题目生成与批改')
    parser.add_argument('-n', type=int, help='生成题目个数')
    parser.add_argument('-r', type=int, help='数值范围（生成的自然数、分母等使用该上限，不包含该值）')
    parser.add_argument('-e', help='现有题目文件，用于批改')
    parser.add_argument('-a', help='答案文件，用于批改')
    args = parser.parse_args()

    if args.e or args.a:
        if not (args.e and args.a):
            parser.error('使用 -e 批改时必须同时给出 -a')
        grade(args.e, args.a)
        return

    # 生成模式
    if args.r is None:
        parser.error('生成题目时必须指定 -r 参数（数值范围）')
    if args.n is None:
        parser.error('生成题目时必须指定 -n 参数（题目数量）')
    n = args.n
    r = args.r
    exercises, answers = generate_exercises(n, r)
    with open('Exercises.txt', 'w', encoding='utf-8') as f:
        for line in exercises:
            f.write(line + '\n')
    with open('Answers.txt', 'w', encoding='utf-8') as f:
        for line in answers:
            f.write(line + '\n')
    print('Exercises.txt, Answers.txt 已生成')

if __name__ == '__main__':
    main()
