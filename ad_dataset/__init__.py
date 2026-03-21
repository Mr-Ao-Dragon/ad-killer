import logging
import os

from transformers import AutoModel


def __init___():
    global dataset_AI
    if not os.environ.get("ALL_PROXY") or not os.environ.get("HTTP_PROXY") or not os.environ.get("HTTPS_PROXY"):
        logging.warn("not set system proxy"
             "this package will try to connect huggingface without proxy,"
             "if you are in China, it may cause some problems")
        ...
    dataset_AI=AutoModel.from_pretrained("THUDM/chatglm3-6b", trust_remote_code=True).save_pretrained("./data/chatglm3-6b")