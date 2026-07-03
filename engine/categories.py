import json
from engine.ranking import compute_score
from engine.ranking import search


class CategoryTree:

    def __init__(self, json_file: str):
        self.json_file = json_file
        self.catalog = self._build_catalog()
        self.tree = self._build_category_tree()


    def _build_catalog(self) -> list:
        with open(self.json_file, "r", encoding="utf-8") as f:
            return json.load(f)


    def _build_category_tree(self) -> dict:
        # Creates and returns a series of nested dictionaries representing a tree with all the categories.
        category_tree = {}
        index_categories = {}
        for entry in self.catalog:
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
                # Creation of the new entry happens here: None if we're at the end of a branch,
                # empty dict otherwise because we know it will be filled on the next step anyway.
                if step not in current_level:
                    is_last = (i == len(path))
                    current_level[step] = None if is_last else {}
                index_categories[accumulated_path] = current_level[step]
                current_level = current_level[step]
        return category_tree


    def search_in_category(self, query: str, category: str, top_k: int = 10) -> list:
        category = list(word.capitalize() for word in category.split("/"))
        current_level = self.tree
        search_request = {}
        current_search_level = search_request
        full_valid_path = ""

        # Find the deepest correct category match based on category input.
        for i, entry in enumerate(category, start=1):
            if entry not in current_level:
                if full_valid_path != "":
                    print(f"The {entry} category doesn't exist. Displaying items in the {full_valid_path} category.")
                else:
                    print(f"The {entry} category doesn't exist. Displaying 10 items based only on {query}.")
                break
            is_last = (i == len(category))
            current_search_level[entry] = None if is_last else {}
            current_level = current_level[entry]
            current_search_level = current_search_level[entry]
            full_valid_path = f"{full_valid_path}/{entry}" if full_valid_path else entry

        # Safeguarding against no valid path potentially returning the whole catalog.
        if full_valid_path == "":
            final_results = search(query, 10)

        else:
            # Run the search based on the final, deepest level reached in the category tree.
            valid_results = []
            for item in self.catalog:
                if full_valid_path in item.get("category"):
                    valid_results.append(item)

            # Weigh valid products based on the scoring algorithm.
            weighted_results = []
            for item in valid_results:
                score = compute_score(item, set(query))
                weighted_results.append((score, item["name"]))

            # Sort by relevance and limit the amount of results displayed.
            weighted_results.sort(reverse=True)
            final_results = []
            for i in range(min(len(weighted_results), top_k)):
                final_results.append(weighted_results[i][1])

        return final_results