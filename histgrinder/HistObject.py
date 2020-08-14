from typing import Any


# Object to hold histogram name & object
class HistObject(object):
    def __init__(self, name: str, hist: Any):
        self.name = name
        self.hist = hist

    def __str__(self):
        return f"{type(self.hist).__name__} object {self.name}"
