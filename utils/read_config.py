import configparser
import os

CONFIG_DIRECTORY = os.path.join("./messages", "messages.py")


class ReadConfig:
    path = CONFIG_DIRECTORY

    def __init__(self):
        pass

    @classmethod
    def read_message(cls, sections: str, key: str):
        cf = configparser.ConfigParser()
        cf.read(cls.path, encoding="utf8")
        return cf.get(sections, key)
