import mimetypes
import pathlib

import transformers


class DataManager:
    @classmethod
    def __scanner(cls):
        result = []
        for path in pathlib.Path(cls.dta_path).rglob("*"):
            if path.is_file() and (mimetypes.guess_type(path)[0] == 'text/' or mimetypes.guess_type(path)[
                0] == 'application/octet-stream' or path.suffix == ".txt"):
                result.append(path)
        return result

    data_file_map = []
    dta_path = ""
    read_slot = ""
    slot_read_pointer = 0
    model_name = ""
    model_ctx_size = 0

    @classmethod
    def __init__(cls):
        cls.dta_path = "./data/"
        cls.data_file_map = cls.__scanner()

    @classmethod
    def auto_sel(cls):
        selected = cls.data_file_map[-1]
        del cls.data_file_map[-1]
        return selected

    @classmethod
    def rescan(cls):
        cls.data_file_map = cls.__scanner()

    @classmethod
    def read_2_slot(cls):
        if len(cls.read_slot) > 0:
            return cls.read_slot
        cls.read_slot = cls.auto_sel()
        return cls.read_slot

    @classmethod
    def cut_out(cls, model_name):
        if len(cls.read_slot) <= cls.slot_read_pointer:
            return "SIG_ENDED"
        if cls.model_name == model_name:
            cls.model_name = model_name
        if cls.model_name == '':
            cls.model_name = 'zai-org/chatglm3-6b'
        if cls.model_ctx_size <= 0:
            cls.model_ctx_size = transformers.AutoConfig.from_pretrained(model_name).max_position_embeddings
        result = cls.read_slot[cls.slot_read_pointer:cls.slot_read_pointer +(cls.model_ctx_size // 45 * 100)]
        cls.slot_read_pointer = (cls.slot_read_pointer + (cls.model_ctx_size // 45 * 100))
        return result