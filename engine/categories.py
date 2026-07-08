from engine.index import search_index
from engine.ranking import search


class CategoryTree:

    """
    A self-contained class that builds a category tree with the imported catalog of products.
    It then gives access to a search_by_category method, which processes the category argument of the user's query
    to filter potential results before using the general search method for ranking said results.
    """

    def __init__(self):
        self.catalog = search_index.catalog
        self.tree = self._build_category_tree()


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


    def search_in_category(self, query: str, category: str, top_k: int = 10) -> list[dict]:
        """
        Runs a search by category if the user entered any in the search query's adequate argument.

        This method receives the full query, after the words have been processed. If there is a category
        argument in the search, then this method receives it, processes the category into a valid format
        while checking its existence in the catalog. If matches are found, they are then ranked by pertinence
        according to the same formula as for regular searches before being returned as a list.

        Args:
            self.tree : the tree-shaped representation of the category paths present in the catalog.
            self.catalog : the catalog as a whole.
            query (str): The search terms for the category argument entered by the user.
            category (str): The category argument entered by the user.
            top_k (int, optional): Maximum number of results to return. Defaults to 10.

        Returns:
            list[str]: A list of products (as catalog entries) matching the searched category and terms.

        Edge cases:
            - if the first category researched doesn't exist, the method stops building the path and informs the user.
            The results are limited to a maximum of 3 so that the whole catalog doesn't get printed.
            - if the path-building breaks at any point, the user is informed of the point of failure, and results are
            returned based on the full valid path built thus far. Those results are limited to 5.
        """
        category = list(word.capitalize() for word in category.split("/"))
        current_level = self.tree
        search_request = {}
        current_search_level = search_request
        full_valid_path = ""
        error_in_path = False
        limited_results_after_error = min(top_k, 3)

        # Find the deepest correct category match based on category input.
        for i, entry in enumerate(category, start=1):
            # Treat mistakes first, based on whether the category argument is fully or partially wrong.
            if entry not in current_level:
                error_in_path = True
                if full_valid_path == "":
                    print(f"The first category you entered ({entry}) doesn't exist. "
                          f"Displaying {limited_results_after_error} items based only on {query}.")
                else:
                    limited_results_after_error = min(limited_results_after_error, 5)
                    print(f"The {entry} subcategory doesn't exist. "
                          f"Displaying {limited_results_after_error} items in the {full_valid_path} category.")
                break
            is_last = (i == len(category))
            current_search_level[entry] = None if is_last else {}
            current_level = current_level[entry]
            current_search_level = current_search_level[entry]
            full_valid_path = f"{full_valid_path}/{entry}" if full_valid_path else entry

        # Safeguarding against no valid path potentially returning the whole catalog.
        if error_in_path and full_valid_path == "":
            return search(query, limited_results_after_error)
        else:
            # Run the search based on the final, deepest level reached in the category tree.
            valid_results = []
            for item in self.catalog:
                if full_valid_path in item.get("category"):
                    valid_results.append(item["id"])
            return search(query,
                        top_k if not error_in_path else limited_results_after_error,
                        lambda product_id: product_id in valid_results)