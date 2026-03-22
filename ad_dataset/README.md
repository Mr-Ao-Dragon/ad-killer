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

# 4. 处理每块数据（结果会累加）
for chunk in chunks:
    results = processor.infer(chunk)
    print(f"发现 {len(results)} 条广告")

# 5. 保存结果
processor.save_result("output.jsonl")
```

**注意**：
- 空目录不会崩溃，会返回空列表
- `infer()` 的结果会累加到 `processor.result`，多次调用后统一保存

## 模块说明

### DataManager

数据文件管理，负责扫描和分块。

| 方法 | 说明 | 返回值 |
|------|------|--------|
| `__init__(dta_path)` | 初始化，扫描指定目录下的文本文件 | DataManager 实例 |
| `_scanner()` | 递归扫描目录，返回文件路径列表 | `list[Path]` |
| `_is_text_file(path)` | 通过 MIME 类型判断是否为文本文件 | `bool` |
| `auto_sel()` | 取出并移除文件列表中的最后一个文件，无文件返回 `None` | `Path \| None` |
| `rescan()` | 重新扫描目录 | - |
| `read_to_slot()` | 读取文件内容到内存缓存，无文件返回空字符串 | `str` |
| `cut_out(model_name)` | 按模型上下文大小分块返回文本 | `str`（或 `"SIG_ENDED"`） |
| `multi_cut_out(model_name)` | 返回所有分块的列表 | `list[str]` |

**注意**：
- `cut_out` 返回 `"SIG_ENDED"` 表示已读取完毕
- 空目录处理：不会抛出异常，返回空列表
- **设计意图**：每个文件独立处理，避免数据间污染。如需处理多本书，请为每本书单独创建 DataManager 实例

### DataProcessor

调用 LLM 识别广告内容。

| 方法 | 说明 | 返回值 |
|------|------|--------|
| `__init__(model)` | 加载预训练模型 | DataProcessor 实例 |
| `infer(raw)` | 识别文本中的广告，结果累加到 `self.result` | `list[DatSingle]` |
| `main_loop(model_name)` | 遍历所有数据并处理 | - |
| `save_result(addr)` | 保存结果到 JSONL 文件 | - |

**注意**：
- `infer()` 每次调用的结果会**累加**到 `self.result`，不会清空
- 多次调用 `infer` 后，`self.result` 包含所有 chunk 的检测结果

### DatSingle

单条广告数据：

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