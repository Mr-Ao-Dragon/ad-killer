import mimetypes
import pathlib
import typing

import transformers


class DataManager:
    def __init__(self, dta_path: str = "./data/"):
        self.dta_path = dta_path
        self.data_file_map = self._scanner()
        self.read_slot = ""
        self.slot_read_pointer = 0
        self.model_name = ""
        self.model_ctx_size = 0
        self._current_file_content = ""

    def _scanner(self):
        result = []
        for path in pathlib.Path(self.dta_path).rglob("*"):
            if path.is_file() and (path.suffix == ".txt" or self._is_text_file(path)):
                result.append(path)
        return result

    def _is_text_file(self, path: pathlib.Path) -> bool:
        mime = mimetypes.guess_type(path)[0]
        return mime is not None and (mime.startswith('text/') or mime == 'application/octet-stream')

    def auto_sel(self):
        selected = self.data_file_map[-1]
        self.data_file_map.pop()
        return selected

    def rescan(self):
        self.data_file_map = self._scanner()

    def read_to_slot(self):
        if self._current_file_content:
            return self._current_file_content
        file_path = self.auto_sel()
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            self._current_file_content = f.read()
        return self._current_file_content

    def cut_out(self, model_name: str):
        if self.model_name != model_name:
            self.model_name = model_name or 'zai-org/chatglm3-6b'
        if self.model_ctx_size <= 0:
            self.model_ctx_size = transformers.AutoConfig.from_pretrained(self.model_name).max_position_embeddings

        content = self.read_to_slot()
        if self.slot_read_pointer >= len(content):
            return "SIG_ENDED"

        chunk_size = self.model_ctx_size // 45 * 100
        result = content[self.slot_read_pointer:self.slot_read_pointer + chunk_size]
        self.slot_read_pointer += chunk_size
        return result

    def multi_cut_out(self, model_name: str) -> typing.List[str]:
        results = []
        result = self.cut_out(model_name)
        while result != "SIG_ENDED":
            results.append(result)
            result = self.cut_out(model_name)
        return results