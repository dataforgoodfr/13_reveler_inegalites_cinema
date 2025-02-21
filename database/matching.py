from typing import List
import numpy as np
import pandas as pd


def normalize_and_sort(name: str) -> List[str]:
    """Normalize the name by converting to lowercase, removing punctuation, and sorting tokens."""
    # Convert to lowercase and remove punctuation
    name = "".join(char.lower() for char in name if char.isalnum() or char.isspace())
    # Split into tokens and sort
    tokens = name.split()
    return sorted(tokens)


def levenshtein_distance(s1: str, s2: str) -> int:
    """Compute the Levenshtein distance between two strings."""
    if len(s1) < len(s2):
        return levenshtein_distance(s2, s1)

    # len(s1) >= len(s2)
    if len(s2) == 0:
        return len(s1)

    previous_row = np.arange(len(s2) + 1)
    for i, c1 in enumerate(s1):
        current_row = previous_row + 1
        current_row[1:] = np.minimum(
            current_row[1:], np.add(previous_row[:-1], [c1 != c2 for c2 in s2])
        )
        previous_row = current_row

    return previous_row[-1]


def jaro_winkler_similarity(s1: str, s2: str) -> float:
    """Calculate Jaro-Winkler similarity between two strings."""
    # If strings are identical, return 1
    if s1 == s2:
        return 1.0

    # Find lengths of strings
    len1, len2 = len(s1), len(s2)
    if len1 == 0 or len2 == 0:
        return 0.0

    # Maximum distance between matching characters
    match_distance = max(len1, len2) // 2 - 1

    # Arrays to track matches
    s1_matches = [False] * len1
    s2_matches = [False] * len2

    # Count matching characters
    matches = 0
    for i in range(len1):
        start = max(0, i - match_distance)
        end = min(i + match_distance + 1, len2)

        for j in range(start, end):
            if not s2_matches[j] and s1[i] == s2[j]:
                s1_matches[i] = True
                s2_matches[j] = True
                matches += 1
                break

    if matches == 0:
        return 0.0

    # Count transpositions
    transpositions = 0
    j = 0
    for i in range(len1):
        if s1_matches[i]:
            while not s2_matches[j]:
                j += 1
            if s1[i] != s2[j]:
                transpositions += 1
            j += 1

    # Calculate Jaro similarity
    transpositions = transpositions // 2
    jaro = (
        (matches / len1) + (matches / len2) + ((matches - transpositions) / matches)
    ) / 3.0

    # Calculate Jaro-Winkler similarity
    prefix_length = 0
    max_prefix_length = 4
    for i in range(min(len1, len2, max_prefix_length)):
        if s1[i] == s2[i]:
            prefix_length += 1
        else:
            break

    # Winkler modification
    scaling_factor = 0.1
    jaro_winkler = jaro + (scaling_factor * prefix_length * (1 - jaro))
    return jaro_winkler


def compare_names(name1: str, name2: str) -> float:
    """Compare two names using normalized tokens, Levenshtein and Jaro-Winkler distances."""

    # Normalize and sort tokens
    tokens1 = normalize_and_sort(name1)
    tokens2 = normalize_and_sort(name2)

    # Join tokens back into strings
    sorted_name1 = " ".join(tokens1)
    sorted_name2 = " ".join(tokens2)

    # Calculate Levenshtein similarity
    lev_distance = levenshtein_distance(sorted_name1, sorted_name2)
    max_len = max(len(sorted_name1), len(sorted_name2))
    lev_similarity = 1 - (lev_distance / max_len)

    # Calculate Jaro-Winkler similarity
    jw_similarity = jaro_winkler_similarity(sorted_name1, sorted_name2)

    # Combine scores (equal weights)
    final_similarity = (lev_similarity + jw_similarity) / 2
    return final_similarity


def find_matches(
    name: str, names: pd.DataFrame, column: str, threshold: float = 0.9
) -> pd.DataFrame:
    """Find matches for a name in a dataframe of names using a similarity threshold, sorted by similarity."""
    # Calculate similarities for all rows at once
    similarities = names[column].apply(lambda x: compare_names(name, x))

    # Create mask for matches above threshold
    mask = similarities >= threshold

    # Create result DataFrame with similarities
    matches = names[mask].copy()
    matches["similarity_score"] = similarities[mask]

    # Sort by similarity score in descending order
    return matches.sort_values("similarity_score", ascending=False)


if __name__ == "__main__":
    # Example1
    name1 = "AGUERO Pablo"
    name2 = "AGÜERO Pablo"

    # Compare the names
    comparison_result = compare_names(name1, name2)
    print(f"Similarity between '{name1}' and '{name2}': {comparison_result:.2f}")

    # Example2
    name1 = "Jean-Luc Godard"
    name2 = "GODARD, Jean Luc"

    # Compare the names
    comparison_result = compare_names(name1, name2)
    print(f"Similarity between '{name1}' and '{name2}': {comparison_result:.2f}")

    # Example3
    name1 = "Quention Tarantino"
    name2 = "Steven Spielberg"

    # Compare the names
    comparison_result = compare_names(name1, name2)
    print(f"Similarity between '{name1}' and '{name2}': {comparison_result:.2f}")

    # Example4
    name1 = "CARPENTIER Frederic"
    name2 = "Frederic Carpentier"

    # Compare the names
    comparison_result = compare_names(name1, name2)
    print(f"Similarity between '{name1}' and '{name2}': {comparison_result:.2f}")
