import json


class CategoryTree:


    # Copied Julien's structure for initializing the tree from the json file
    def __init__(self, json_file: str):
        self.json_file = json_file
        self.catalog = self._build_catalog()
        self.tree = self._build_category_tree()


    def _build_catalog(self) -> list:
        with open(self.json_file, "r", encoding="utf-8") as f:
            return json.load(f)


    def _build_category_tree(self) -> dict:
        # Must be processed before scoring as to avoid unnecessary scoring on items that will end up discarded.
        """
        Creates and returns a series of nested dictionaries representing a tree with all the categories.
        """
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


    def search_in_category(self, query: str, top_k: int = 10) -> list:
        """
        Only starts searching from the start of the tree, which matches the requirements of the assignment.
        """
        query = query.split("/")
        current_level = self.tree
        search_request = {}
        current_search_level = search_request
        full_valid_path = ""

        # Find the deepest correct category match based on query input
        for i, entry in enumerate(query, start=1):
            if entry not in current_level:
                print(f"Your search yielded no results in the {entry} category.")
                break
            else:
                is_last = (i == len(query))
                current_search_level[entry] = None if is_last else {}
            current_level = current_level[entry]
            current_search_level = current_search_level[entry]
            full_valid_path = f"{full_valid_path}/{entry}" if full_valid_path else entry

        # Run the search based on the final, deepest level reached in the category tree
        valid_results = []
        for item in self.catalog:
            if full_valid_path in item.get("category"):
                valid_results.append(item["id"])
        # Need the top_k method here to limit the output to best results. todo
        return valid_results


# test = CategoryTree("./catalog.json")
# print(test.search_in_category("Electronics/Computers/Peripherals"))