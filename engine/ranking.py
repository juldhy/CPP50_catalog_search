import math
import heapq
from functools import reduce

from engine.tokenize import tokenize
from engine.index import search_index


def compute_score(product, query_tokens : set[str]) -> float:
    """
    Scores the product with this formula:
       score = (matched_tokens / total_query_tokens) * 0.5
            + (stock > 0) * 0.2
            + (1 / log2(sales_rank + 2)) * 0.3
    :param product:
    :param query_tokens: all the query tokens
    :return: the product score
    """
    if len(query_tokens) == 0:
        return 0
    else:
        return 0.5 * (len( (set(tokenize(product['name'])) | set(map(str.lower,product['tags']))) & query_tokens)  / len(query_tokens)) \
            + (0.2 if product['stock'] > 0 else 0) \
            + (1 / math.log2(product['sales_rank'] + 2)) * 0.3


def search(query: str, top_k: int = 10, filter_fn = None) -> list[str]:
    """
    This function
    - tokenises the query the same way as the index
    - finds the union of all product IDs matching any query token
    - Scores each candidate product with this formula:
        score = (matched_tokens / total_query_tokens) * 0.5
            + (stock > 0) * 0.2
            + (1 / log2(sales_rank + 2)) * 0.3
    - Returns the top_k highest-scoring products

    :pre catalog invert index of the form { token:str : set{productid:str} } is accessible
    :pre catalog is accessible

    :param filter_fn: a filter_fn to apply to the candidate product ID, before scoring and sorting.
    :param query: The query
    :param top_k: The max size of the return list
    :return: the top_k highest-scoring products as an ordered list
    """

    catalog = search_index.catalog
    query_tokens = set(tokenize(query))
    # Get the candidate product ID's as the union of the index entries of each query tokens
    candidates = reduce(lambda result, token : result.union(search_index.index.get(token, set())), query_tokens, set())
    # Find the top_k (candidate product ID, score) according to the computed score, but return the product IDs only
    return list(map(lambda id_score:catalog.get(id_score[0]),
                    heapq.nlargest(top_k,
                          map(lambda candidate_id: (candidate_id, compute_score(catalog.get(candidate_id), query_tokens)), filter(filter_fn, candidates)),
                          key=lambda x: x[1])))
