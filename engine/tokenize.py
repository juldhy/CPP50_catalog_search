import re


def tokenize(input: str) -> list[str]:
    values = re.split("[, .;!?]", input.strip().lower())
    return list(filter(lambda x: len(x) > 2, values))
