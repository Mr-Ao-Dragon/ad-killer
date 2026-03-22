import logging
import os


def __init___():
    if not os.environ.get("ALL_PROXY") or not os.environ.get("HTTP_PROXY") or not os.environ.get("HTTPS_PROXY"):
        logging.warning("not set system proxy"
             "this package will try to connect huggingface without proxy,"
             "if you are in China, it may cause some problems")
        ...