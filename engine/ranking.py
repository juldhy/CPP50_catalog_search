import math
import heapq
from functools import reduce

from engine.tokenize import tokenize
from engine.index import search_index

# TODO: BEGIN replace with appropriate access to catalog and catalog index
from collections import defaultdict
import json
def get_catalog()->dict:
    with open('/home/ubuntu/PycharmProjects/CPP50_catalog_search/catalog.json') as json_file:
        return {product['id']:product for product in json.load(json_file)}
# TODO: END replace with appropriate access to catalog and catalog index


def compute_score(product, query_tokens : list[str]) -> float:
    """
    Scores the product with this formula:
       score = (matched_tokens / total_query_tokens) * 0.5
            + (stock > 0) * 0.2
            + (1 / log2(sales_rank + 2)) * 0.3
    :param product:
    :param query_tokens: all the query tokens
    :return: the product score
    """
    return 0.5 * (len((set(tokenize(product['name'])) | set(product['tags'])) & query_tokens)  / len(query_tokens)) \
        + 0.2 if product['stock'] > 0 else 0 \
        + (1 / math.log2(product['sales_rank'] + 2)) * 0.3


def search(query: str, top_k: int = 10) -> list[str]:
    """
    This function
    - tokenises the query the same way as the index
    - finds the union of all product IDs matching any query token
    - Scores each candidate product with this formula:
        score = (matched_tokens / total_query_tokens) * 0.5
            + (stock > 0) * 0.2
            + (1 / log2(sales_rank + 2)) * 0.3
    - Returns the top_k highest-scoring products
    :pre catalog invert index of the form { token:str : set{productid:str} }
    :param query: The query
    :param top_k: The max size of the return list
    :return: the top_k highest-scoring products as an ordered list
    """

    catalog = get_catalog()
    query_tokens = set(tokenize(query))
    candidates = reduce(lambda result, token : result.union(search_index.get(token, set())), query_tokens, set())
    return list(map(lambda id_score:catalog.get(id_score[0]),
                    heapq.nlargest(top_k,
                          map(lambda candidate_id: (candidate_id, compute_score(catalog.get(candidate_id), query_tokens)), candidates),
                          key=lambda x: x[1])))


if __name__ == '__main__':
    print(search("wireless keyboard", top_k=5))




