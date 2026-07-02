from collections import defaultdict
import json
from .tokenize import tokenize


class SearchIndex:
    """
    A class that builds index on initialization and allows searching for items based on tokens.
    """

    def __init__(self, json_file: str):
        self.json_file = json_file
        self.index = self._build_index()
        self.catalog = self._build_catalog()

    def _build_catalog(self) -> dict[str, dict]:
        with open(self.json_file, "r", encoding="utf-8") as f:
            data = json.load(f)

        catalog = {item["id"]: item for item in data}
        return catalog

    def _build_index(self) -> dict[str, set[str]]:
        with open(self.json_file, "r", encoding="utf-8") as f:
            data = json.load(f)

        idx = defaultdict(set)

        for item in data:
            for token in tokenize(item["name"]):
                idx[token].add(item["id"])

            for tag in item["tags"]:
                idx[tag].add(item["id"])

        return dict(idx)

    def get_index_tokens(self) -> list[str]:
        return list(self.index.keys())

    def search(self, token: str) -> set[str]:
        return self.index.get(token.lower().strip(), set())


search_index = SearchIndex("./catalog.json")
