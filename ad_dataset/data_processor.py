import logging
import typing
from typing import TypedDict

import jsonlines
from transformers import AutoModel

from ad_dataset.data_manager import DataManager


class DatSingle(TypedDict):
    raw: str
    cleared: str


class DataProcessor:
    def __init__(self, model: str):
        self.model = AutoModel.from_pretrained(model, trust_remote_code=True, dtype="auto")
        self.prompt = ("你是一个数据清洗工具，负责从文本中识别并标记乱码广告内容。\n"
                       "识别标准：无法正常阅读、包含随机字符组合、看似乱码的推广信息。\n\n"
                       "输出格式要求：\n"
                       "1. 每条清洗结果占一行\n"
                       "2. 格式为：原文:::清洗后内容\n"
                       "3. 多个结果用;;;分隔\n\n"
                       "特殊规则：\n"
                       "- 若文本不包含乱码广告，输出：NOT_FOUND:::NOT_FOUND;;;\n"
                       "- 只输出结果，不要包含任何解释或额外文字\n\n"
                       "待处理文本：")
        self.result: list[DatSingle] = []
        self.result_addr = ""

    def infer(self, raw: str) -> list[DatSingle]:
        self.result.clear()
        resp, _ = self.model.generate(self.prompt + raw)
        if resp == "NOT_FOUND:::NOT_FOUND;;;":
            return []
        result: typing.List[str] = resp.split(";;;")
        if result[-1] == '':
            del result[-1]  # 这里是为了删除多余的一个空元素
        for sig_raw in result:
            if sig_raw == "NOT_FOUND:::NOT_FOUND;;;":
                break
            cuted = sig_raw.split(":::")
            sig: DatSingle = DatSingle(
                raw=cuted[0],
                cleared=cuted[1]
            )
            self.result.append(sig)
        return self.result

    def main_loop(self, model_name):
        dm = DataManager()
        raw_datas = dm.multi_cut_out(model_name)
        for raw_data in raw_datas:
            self.infer(raw=raw_data)

    def save_result(self, result_addr: str = None):
        class NoResultError(Exception):
            pass

        addr = result_addr or self.result_addr
        if len(self.result) <= 0:
            raise NoResultError("No result to save.")
        try:
            with jsonlines.open(addr, mode='w') as f:
                f.write_all(self.result)
        except Exception as e:
            logging.error(f"{e}")
            raise
