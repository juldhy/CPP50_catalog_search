import json
JSON_FILE_PATH = "./catalog.json"

def search_in_category(query: str, category: str, top_k: int = 10): # todo add return type
    # Definitely going for a BFS here to offer all the choices that are at depth + 1 instead of reaching
    # the end of each path before suggesting the next one. This means the results will be going from the
    # more generic items to the more specific ones.
    # This may need to change if sorting based on score influences/bypasses this concept.
    """
    Only starts searching from the start of the tree, but that matches the requirements of the assignment.
    """
    ...

with open(JSON_FILE_PATH, "r", encoding="utf-8") as f:
    data = json.load(f)


def build_category_tree(catalog: list[dict]) -> dict:
    # Must be processed before scoring as to avoid unnecessary scoring on items that will end up discarded.
    """
    Creates and returns a series of nested dictionaries representing a tree with all the categories.
    """
    category_tree = {}
    index_categories = {}
    for entry in catalog:
        category_str = entry.get("category", "")
        # Skip processing if the WHOLE path already exists, or is empty somehow.
        if category_str in index_categories or not category_str:
            continue
        path = category_str.split("/")
        current_level = category_tree
        accumulated_path = ""
        for i, step in enumerate(path, start=1):
            # Proper formatting to avoid putting a / on the final category of a branch.
            accumulated_path = f"{accumulated_path}/{step}" if accumulated_path else step
            # Skip ahead if this part of the path already exists.
            if accumulated_path in index_categories:
                current_level = index_categories[accumulated_path]
                continue
            is_last = (i == len(path))
            # Creation of the new entry happens here: None if we're at the end of a branch,
            # empty dict otherwise because we know it will be filled on the next step anyway.
            if step not in current_level:
                current_level[step] = None if is_last else {}
            index_categories[accumulated_path] = current_level[step]
            current_level = current_level[step]
    return category_tree

print(build_category_tree(data))