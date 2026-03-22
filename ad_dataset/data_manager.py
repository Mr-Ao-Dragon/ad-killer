"""数据文件管理模块，负责扫描和分块文本数据"""

import mimetypes
import pathlib

import transformers


class DataManager:
    """数据文件管理器，负责扫描和分块文本数据"""

    def __init__(self, dta_path: str = "./data/"):
        """
        初始化数据管理器

        Args:
            dta_path: 数据目录路径，默认为 "./data/"
        """
        self.dta_path = dta_path
        self.data_file_map = self._scanner()
        self.read_slot = ""
        self.slot_read_pointer = 0
        self.model_name = ""
        self.model_ctx_size = 0
        self._current_file_content = ""

    def _scanner(self) -> list[pathlib.Path]:
        """递归扫描目录，返回文本文件路径列表"""
        result = []
        for path in pathlib.Path(self.dta_path).rglob("*"):
            if path.is_file() and (path.suffix == ".txt" or self._is_text_file(path)):
                result.append(path)
        return result

    def _is_text_file(self, path: pathlib.Path) -> bool:
        """通过 MIME 类型判断是否为文本文件"""
        mime = mimetypes.guess_type(path)[0]
        return mime is not None and (mime.startswith('text/') or mime == 'application/octet-stream')

    def auto_sel(self) -> pathlib.Path | None:
        """
        取出并移除文件列表中的最后一个文件

        Returns:
            文件路径，无文件时返回 None
        """
        if not self.data_file_map:
            return None
        selected = self.data_file_map[-1]
        self.data_file_map.pop()
        return selected

    def rescan(self):
        """重新扫描数据目录"""
        self.data_file_map = self._scanner()

    def read_to_slot(self) -> str:
        """
        读取文件内容到内存缓存

        Returns:
            文件内容，无文件时返回空字符串
        """
        if self._current_file_content:
            return self._current_file_content
        file_path = self.auto_sel()
        if file_path is None:
            return ""
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            self._current_file_content = f.read()
        return self._current_file_content

    def cut_out(self, model_name: str) -> str:
        """
        按模型上下文大小分块返回文本

        Args:
            model_name: 模型名称

        Returns:
            文本块，读取完毕后返回 "SIG_ENDED"
        """
        if self.model_name != model_name:
            self.model_name = model_name or 'zai-org/chatglm3-6b'
        if self.model_ctx_size <= 0:
            self.model_ctx_size = (transformers.
                                   AutoConfig.
                                   from_pretrained(self.model_name).
                                   max_position_embeddings)

        content = self.read_to_slot()
        if self.slot_read_pointer >= len(content):
            return "SIG_ENDED"

        chunk_size = self.model_ctx_size // 45 * 100
        result = content[self.slot_read_pointer:self.slot_read_pointer + chunk_size]
        self.slot_read_pointer += chunk_size
        return result

    def multi_cut_out(self, model_name: str) -> list[str]:
        """
        返回所有分块的列表

        Args:
            model_name: 模型名称

        Returns:
            文本块列表
        """
        results = []
        result = self.cut_out(model_name)

        while result != "SIG_ENDED":
            results.append(result)
            result = self.cut_out(model_name)
        return results
