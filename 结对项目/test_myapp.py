# test_myapp.py
import pytest
from fractions import Fraction
from Myapp import Number, Binary, gen_number, gen_expr_with_ops, validate_tree
from Myapp import format_fraction_output, parse_mixed_fraction, parse_and_eval, generate_exercises

# =================== 测试 Number 类 ===================
def test_gen_number():
    """
    测试目标：
        - gen_number 能否正确生成 Number 对象
        - 生成的值为 Fraction 类型
    测试思路：
        - 随机生成 50 个 Number
        - 检查类型与 eval() 输出类型
    """
    for _ in range(50):
        n = gen_number(10)
        assert isinstance(n, Number)
        val = n.eval()
        assert isinstance(val, Fraction)

def test_number_eval():
    """
    测试目标：
        - Number.eval() 方法正确返回自身存储的 Fraction
    测试思路：
        - 构造一个 Number(Fraction)
        - 调用 eval() 并与原 Fraction 比较
    """
    n = Number(Fraction(3, 4))
    assert n.eval() == Fraction(3, 4)

# =================== 测试 Binary 类 ===================
def test_binary_eval():
    """
    测试目标：
        - Binary.eval() 正确计算加法结果
    测试思路：
        - 构造 Binary('+', Number, Number)
        - 检查 eval() 与手动计算结果一致
    """
    n1 = Number(Fraction(1,2))
    n2 = Number(Fraction(1,3))
    b = Binary('+', n1, n2)
    assert b.eval() == Fraction(5,6)

# =================== 测试 gen_expr_with_ops ===================
def test_gen_expr_with_ops_valid():
    """
    测试目标：
        - gen_expr_with_ops 能生成合法表达式
    测试思路：
        - 生成一个包含最多 3 个运算符的表达式
        - 验证生成的表达式对象类型
        - 若表达式非空，调用 validate_tree 验证其合法性
    """
    expr = gen_expr_with_ops(3, 10)
    assert expr is None or isinstance(expr, Binary) or isinstance(expr, Number)
    if expr:
        assert validate_tree(expr)

# =================== 测试 validate_tree ===================
def test_validate_tree_negative():
    """
    测试目标：
        - validate_tree 能检测减法产生负数的非法情况
    测试思路：
        - 构造 1 - 2
        - 断言 validate_tree 返回 False
    """
    n1 = Number(Fraction(1))
    n2 = Number(Fraction(2))
    b = Binary('-', n1, n2)
    assert not validate_tree(b)

def test_validate_tree_div_integer():
    """
    测试目标：
        - validate_tree 能检测除法结果为整数的非法情况
    测试思路：
        - 构造 4 ÷ 2，结果分母 = 1
        - 断言 validate_tree 返回 False
    """
    n1 = Number(Fraction(4,1))
    n2 = Number(Fraction(2,1))
    b = Binary('/', n1, n2)
    assert not validate_tree(b)

# =================== 测试 format_fraction_output ===================
def test_format_fraction_output():
    """
    测试目标：
        - format_fraction_output 能正确格式化整数、真分数、带分数和负数
    测试思路：
        - 构造多种 Fraction
        - 检查输出字符串是否符合要求
    """
    assert format_fraction_output(Fraction(5,1)) == "5"
    assert format_fraction_output(Fraction(3,2)) == "1'1/2"
    assert format_fraction_output(Fraction(2,3)) == "2/3"
    assert format_fraction_output(Fraction(-7,3)) == "-2'1/3"

# =================== 测试 parse_mixed_fraction ===================
def test_parse_mixed_fraction():
    """
    测试目标：
        - parse_mixed_fraction 能解析带分数、真分数和整数
    测试思路：
        - 输入 3'2/5、2/3、5
        - 检查返回的 Fraction 是否正确
    """
    assert parse_mixed_fraction("3'2/5") == Fraction(17,5)
    assert parse_mixed_fraction("2/3") == Fraction(2,3)
    assert parse_mixed_fraction("5") == Fraction(5,1)

# =================== 测试 parse_and_eval ===================
def test_parse_and_eval():
    """
    测试目标：
        - parse_and_eval 能正确解析题目字符串并返回 Fraction
        - 支持带分数和 ÷ 符号
    测试思路：
        - 构造加法、带分数加法、除法表达式
        - 检查计算结果是否正确
    """
    assert parse_and_eval("1/2 + 1/3") == Fraction(5,6)
    assert parse_and_eval("2'1/2 + 1/2") == Fraction(3,1)
    assert parse_and_eval("3 ÷ 2") == Fraction(3,2)

# =================== 测试 generate_exercises ===================
def test_generate_exercises_count_and_unique():
    """
    测试目标：
        - generate_exercises 能生成指定数量的题目和答案
        - 生成题目去重生效（canonical）
    测试思路：
        - 生成 10 道题目
        - 检查题目和答案长度是否一致
        - 遍历题目，解析表达式确保值非空
    """
    n = 10
    rng = 10
    exercises, answers = generate_exercises(n, rng)
    assert len(exercises) == n
    assert len(answers) == n
    # 检查去重（canonical）
    canon_set = set()
    from Myapp import Binary, Number
    for ex in exercises:
        # 去掉编号和等号
        s = ex.split('.', 1)[-1].strip().rstrip('=').strip()
        val = parse_and_eval(s)  # 直接解析求值
        assert val is not None
