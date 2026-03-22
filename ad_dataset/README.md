# 广告数据集处理模块

从文本中识别并清洗乱码广告内容。

## 快速开始

```python
from ad_dataset.data_manager import DataManager
from ad_dataset.data_processor import DataProcessor

# 1. 初始化数据管理器
dm = DataManager(dta_path="./data/")

# 2. 获取分块后的文本数据
chunks = dm.multi_cut_out("gpt2")

# 3. 初始化处理器（需要加载模型，首次较慢）
processor = DataProcessor("gpt2")

# 4. 处理每块数据
for chunk in chunks:
    results = processor.infer(chunk)
    print(f"发现 {len(results)} 条广告")

# 5. 保存结果
processor.save_result("output.jsonl")
```

## 模块说明

### DataManager

数据文件管理，负责扫描和分块。

| 方法 | 说明 |
|------|------|
| `__init__(dta_path)` | 初始化，扫描指定目录下的文本文件 |
| `_scanner()` | 递归扫描目录，返回文件路径列表 |
| `_is_text_file(path)` | 判断是否为文本文件 |
| `auto_sel()` | 取出最后一个文件路径 |
| `rescan()` | 重新扫描目录 |
| `read_to_slot()` | 读取文件内容到内存 |
| `cut_out(model_name)` | 按模型上下文大小分块返回文本 |
| `multi_cut_out(model_name)` | 返回所有分块的列表 |

**注意**：`cut_out` 返回 `"SIG_ENDED"` 表示已读取完毕。

### DataProcessor

调用 LLM 识别广告内容。

| 方法 | 说明 |
|------|------|
| `__init__(model)` | 加载预训练模型 |
| `infer(raw)` | 识别文本中的广告，返回 `DatSingle` 列表 |
| `main_loop(model_name)` | 遍历所有数据并处理 |
| `save_result(addr)` | 保存结果到 JSONL 文件 |

### DatSingle

结果数据类型：

```python
{
    "raw": "原始广告文本",
    "cleared": "清洗后的文本"
}
```

## 输出格式

调用 LLM 时使用的提示词：

```
你是一个数据清洗工具，负责从文本中识别并标记乱码广告内容。

识别标准：无法正常阅读、包含随机字符组合、看似乱码的推广信息。

输出格式要求：
1. 每条清洗结果占一行
2. 格式为：原文:::清洗后内容
3. 多个结果用;;;分隔

特殊规则：
- 若文本不包含乱码广告，输出：NOT_FOUND:::NOT_FOUND;;;
- 只输出结果，不要包含任何解释或额外文字

待处理文本：<用户文本>
```

## 依赖

- transformers
- torch
- jsonlines

详见 `pyproject.toml`。