from engine.index import search_index


def suggest(query: str, max_suggestions: int = 3, lexicon: list[str] = search_index.get_index_tokens()) -> list[str]:
    """
    Suggests a plausible search token based on the user's initial output if no match was found,
    based on edit distance.

    This method scans the global catalog lexicon for words that are close to what the user typed,
    and returns a short list of suggestions if any are found. Only one query word is treated per call,
    meaning the parsing and splitting needs to be performed ahead of the calls.

    Args:
        query (str): The search terms entered by the user.
        max_suggestions (int, optional): Maximum number of results to return.
            Default is 3.
        lexicon (list[str], optional): The list of lexicon tokens to use.

    Returns:
        list[str]: A list of words closely resembling the searched term.
    """
    possible_matches = []
    query = query.lower()
    for word in lexicon:
        # avoids processing words that are much longer or much shorter than the failed query
        # based on the constraints of the assignment
        if len(query) > len(word) + 2 or len(query) < len(word) - 2:
            continue
        distance = check_edit_distance(query, word)
        if distance < 3:
            possible_matches.append((distance, word))
    possible_matches.sort()
    # Added Alain's suggestion to build the final list in a single line with list comprehension
    return [match[1] for match in possible_matches[0:min(len(possible_matches), max_suggestions)]]


def check_edit_distance(long_word: str, short_word : str) -> int:
    if len(short_word) > len(long_word):
        short_word, long_word = long_word, short_word
    # Creating the 2D-list, and filling the starting "cells"
    matrix = [[-1 for _ in range(len(long_word) + 1)] for _ in range(len(short_word) + 1)]
    for k in range(len(matrix[0])):
        matrix[0][k] = k
        if k < len(matrix):
            matrix[k][0] = k
    for i in range(len(short_word)):
        for j in range (len(long_word)):
            # Early exit when the word is already too different to be a valid suggestion
            if i == j and matrix[i][j] > 2:
                return 100
            if short_word[i] == long_word[j]:
                matrix[i+1][j+1] = min(matrix[i][j], matrix[i][j+1], matrix[i+1][j])
            else:
                matrix[i+1][j+1] = min(matrix[i][j], matrix[i][j+1], matrix[i+1][j]) + 1
    return matrix[-1][-1]