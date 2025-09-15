# bench/sample_profile.py
from src.sim import similarity_ratio


def main():
    a = "人工智能的重要分支是机器学习。" * 200
    b = "机器学习是人工智能的重要分支。" * 200
    s = 0.0
    for _ in range(300):
        s += similarity_ratio(a, b, n=2)
    print(s)  # 防止被优化掉


if __name__ == "__main__":
    main()
