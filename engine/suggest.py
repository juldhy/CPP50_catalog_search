from engine.index import search_index


lexicon = search_index.get_index_tokens()

def suggest(query: str, max_suggestions: int = 3) -> list[str]:
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
    final_results = []
    # avoids iterating out of index range if there are few possible results
    for i in range(min(len(possible_matches), max_suggestions)):
        final_results.append(possible_matches[i][1])
    return final_results

def check_edit_distance(long_word: str, short_word : str) -> int:
    if len(short_word) > len(long_word):
        short_word, long_word = long_word, short_word
    chars_long = list(char for char in long_word)
    chars_short = list(char for char in short_word)
    # Creating the 2D-list and filling the static "cells"
    matrix = [[-1 for _ in range(len(long_word) + 1)] for _ in range(len(short_word) + 1)]
    for k in range(len(matrix[0])):
        matrix[0][k] = k
        if k < len(matrix):
            matrix[k][0] = k
    for i in range(len(short_word)):
        for j in range (len(long_word)):
            if chars_short[i] == chars_long[j]:
                matrix[i+1][j+1] = min(matrix[i][j], matrix[i][j+1], matrix[i+1][j])
            else:
                matrix[i+1][j+1] = min(matrix[i][j], matrix[i][j+1], matrix[i+1][j]) + 1
    return matrix[-1][-1]