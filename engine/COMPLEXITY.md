Part 1: index.py
    _build_index has a O(n) time complexity
    It loops a list of item to build a dict

    search has a O(1) time complexity
    It looks in the dict for a specific token


Part 2: ranking.py
    The sort() and sorted() algorhythms have complexity O(n log n).
    The min heap algorythm to retrieve top_k sorted elements has complexity O(n log top_k). However, there is an extra 
    cost for building the min heap binary tree, of which the complexity is O(n).
    The total complexity of using min heap is then O(n + n log top_k), which, for top_k << n, is less than O(n log n).
    When top_k==n, the min heap perf is lower than the sort()/sorted() perf.
    

Part 3: categories.py
    Step 1: Building the catalog
    - Data structure choice: nested dictionaries, as all access operations are O(1).
        A set of sets would have had the same complexity, but is less common for "tree"-type structures.
    - Build-time complexity: O(n*k) where k is the average path depth is the absolute worst case scenario.
        More reasonably, O(n) will be the expected time complexity, particularly as the catalog gets bigger.
        If there are n=5000 entries and 50 unique paths of average depth k=3,
        the total would be 5150 which is basically equal to n.
        BFS/DFS would not have been faster here, as each entry in the catalog needs to be looked up either way.
    Step 2: Running a search by category
    - Query-time complexity: O(n) where n is the length of the catalog. The other parts of the method can bring this
        up to 2n + k where k = (length of the category path + amount of results returned), and 2n because the whole
        catalog may be in the initial valid results, but ultimately it all simplifies to O(n).
        It is most likely possible to run this in a much faster way by previously indexing all possible category paths
        and assigning them an id, assuming we are allowed to add a "CategoryID" field to the products.
    - Example:
        Running the following command: python3 search "Wireless Adaptor" --category "Electronics/Phone" will first
        decouple the path branch by branch and break off at the first invalid one. Whatever was valid before that point
        serves as the category used for filtering results. If no valid category exists, the method branches back to the
        standard search function and forces 10 results to be displayed based on the query terms.
            If the path is valid, the method then searches through the whole catalog for path membership in the
            "Category" field, then scores those results based on relevance with the query terms.
            Finally, the results are sorted by score and the requested (or default) amount of results is displayed.


Part 4: suggest.py
    Step 1: Building the index of valid words
    - Data structure choice: a list of strings, created by re-using the tokenize method for indexing the catalog.
        The list (lexicon) is created from the existing set of all unique strings contained in all product names.
        Keeping the set format would have worked here as well, but lists are usually easier to work with
        and have more features that can be useful if it turns out they're needed (sorting, for example).
    - Build-time complexity: technically speaking, zero. The data is already created for Part 1, and we're simply
        re-using it here. The complexity of that method is O(n*(k+l)) where k and l are the average amounts of
        words in the product names and tags per product, respectively.
    Step 2: Suggesting corrections based on a failed search query
    - Query-time complexity: O(V + Q²*C) where V is the size of the lexicon, Q is the length of the initial query,
        and C is the amount of words in the lexicon whose length is Close to that of Q (C = Q±2).
            While this might look expensive at first, note that, for a Q that gets ridiculously large,
            C will converge towards zero (at least, for most known languages).
                Q² is explained by the fact that two words are being compared,
                and the one that is compared to the initial query is of average length Q as well.
        This beats the "expected" O(V*L²) where L is the average word length in the entire lexicon because the
        method filters out lexicon words that are too much longer or too much shorter than the initial query.
        In return for that check, the resource-intensive edit distance calculator method is called less often.
            Math comparison:
            Q²*C ~= L²*V in the worst case scenario where the query's length is close to every word of the lexicon.
            This matches the second formula, but that one is static regardless of Q.
            V is also the much bigger number for any reasonable catalog, therefore, its absence from the multiplication
            is almost always going to be an advantage.
            On the other hand, when Q is small, the squaring is negligible, and when Q grows very large, C is expected
            to shrink. In the middle, Q²*C can be read as L²*L, which is almost always smaller than L²*V.
    - Example:
        With the following parameters: V = 200; Q = 12; C = 100; L = 10 (Q > L is a bad scenario, and C is large here)
            V + Q²*C = 200 + 14400 = 14600 (or V + Q*L*C = 12200)
            V*L² = 20000
        With Q = 8 (a better scenario), this becomes:
            V + Q²*C = 200 + 6400 = 6600 (or V + Q*L*C = 8200)
        Thus, even when half (C) the lexicon (V) matches the tolerated edit difference size, filtering ahead yields
        better results, nearly averaging a 50% cut in processing time even when half of the lexicon's entries
        approach the length of the query.


Part 5: search
    A method that uses previous parts in it.
    Consider it as the entry point of the project