# README

# 论文查重设计-3223004210

## 一、项目介绍

本项目实现一个**轻量级文本相似度检测**工具，用于对“原文”与“疑似抄袭文本”进行相似度计算并输出结果。
 特点是**依赖少、运行简单**：评测只需一行命令即可完成；同时配备了**代码质量校验**与**单元测试+分支覆盖率**的可选工具链，便于复核。

## 二、功能特性

+ 基于 n-gram（默认 n=2）的文本相似度计算（Jaccard/重叠度等内部实现见 `src/`）
+ 文本清洗与规范化（大小写统一、空白/标点处理等，见 `src/text_norm.py`）
+ 清晰的输入/输出约定与**异常分类处理**（文件不存在、权限、编码错误等 → `stderr` + 退出码 2）
+ **单元测试**与分支覆盖率（branch coverage）报告
+ 代码质量检查（Pylint 10/10、Ruff/Black/isort 已通过）

## 三、运行环境

+ Python **3.10+**（开发与测试基于 **3.12**）
+ 操作系统：Windows 
+ 运行依赖：**无需第三方库**（详见 `requirements.txt`）

> 测试工具（pytest、pylint、ruff 等）不影响运行，放在 `requirements-dev.txt` 中，按需安装。

## 四、目录结构

```
3223004210/
├─ main.py                     # 命令行入口：读取原文/疑似文本，调用相似度函数，写入结果
├─ requirements.txt            # 运行依赖
├─ requirements-dev.txt        # 开发/测试/质量工具依赖（引用 requirements.txt）
├─ pytest.ini                  # pytest 配置（已启用 --cov-branch 分支覆盖率）
├─ .coveragerc                 # coverage 配置
├─ .pylintrc                   # Pylint 配置
├─ pyproject.toml              # Ruff/Black/isort 统一配置
├─ .gitignore                  # 项目级忽略（报告产物、缓存、.vs 等）
├─ data/
│  ├─ org.txt                  # 示例：原文
│  ├─ org_add.txt              # 示例：疑似文本
│  └─ ans.txt                  # 示例：输出结果
├─ src/
│  ├─ __init__.py
│  ├─ io_utils.py              # 读/写文本、路径/编码处理
│  ├─ text_norm.py             # 文本清洗/规范化（大小写、空白、标点等）
│  └─ sim.py                   # 相似度核心算法（n-gram 切片、集合/签名运算等）
├─ tests/                      #单元测试
│  ├─ test_io_utils.py
│  ├─ test_text_norm.py
│  ├─ test_sim.py
│  └─ test_main.py 
├─ reports/
│  ├─ tests/
│  │  └─ coverage_branch_*.png     #分支覆盖率截图
│  └─ perf/                        # 性能分析
│     ├─ before/                   # 优化前
│     │  ├─ baseline_top.txt       # cProfile Top（累计耗时）文本
│     │  └─ VS-baseline.png        # VS 性能分析器截图（CPU/热路径）
│     └─ after/                    # 优化后
│        ├─ optimized_top.txt
│        └─ VS-optimized.png         
└─ bench/
   └─ sample_profile.py        # 性能剖析脚本
               
```

## 五、使用方法

**命令：**

```bash
python main.py <orig_path> <copy_path> <ans_path> [-n N]
# 示例：
python main.py .\data\org.txt .\data\org_add.txt .\data\ans.txt
```

**参数说明**

+ `<orig_path>`：原文文件路径（UTF-8 文本）。
+ `<copy_path>`：疑似抄袭文件路径（UTF-8 文本）。
+ `<ans_path>`：结果输出文件路径。程序会写入一行相似度（四舍五入保留两位小数，末尾含换行）。
+ `-n N` / `--ngram N`（扩展功能）：n-gram 的 n 值，正整数；**默认 2**。
   n 越大匹配越严格，n 越小更敏感，**推荐 2–5**。

**输出：**
 `<答案输出文件>` 中写入**一行**，为相似度分值，**四舍五入保留两位小数**，末尾带换行。例如：

```
0.87
```

## 六、输入/输出与退出码约定

+ **输入**：纯文本文件，建议 UTF-8 编码。
+ **输出**：仅一行相似度，`{score:.2f}\n`。
+ **退出码**：
  + `0`：正常完成；
  + `2`：已知异常（文件不存在/权限问题/编码错误/内容解析错误等），错误信息写入 `stderr`；
  + 其他：非常规错误（不期望出现）。

## 七、单元测试与分支覆盖率

安装开发依赖：

```
pip install -r requirements-dev.txt
```

运行测试并生成分支覆盖率：

```
pytest
```
