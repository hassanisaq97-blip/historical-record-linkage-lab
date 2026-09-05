"""Generic one-to-one constrained assignment, shared by both the synthetic
and NYC-directories pipelines.

Independent pairwise classification can accept more than one edge per
record (e.g. one census record "matching" two different parish records).
This module takes the classifier's *accepted* pairs (already thresholded)
together with a confidence score per pair, builds a graph, and finds the
maximum-weight matching in which every record participates in at most one
accepted link - using `networkx.max_weight_matching`, which solves this
for general graphs (Galil's algorithm), not only strictly bipartite ones.
That generality is exactly what is needed here: the synthetic pipeline's
census/parish links are bipartite, but the NYC-directories case is
within-source (both sides of a pair are drawn from the same set of
records), which is not.
"""

from __future__ import annotations

import networkx as nx
import pandas as pd


def build_score_graph(
    accepted_pairs: pd.DataFrame,
    id_col_a: str,
    id_col_b: str,
    score_col: str,
) -> nx.Graph:
    graph = nx.Graph()
    for row in accepted_pairs.itertuples(index=False):
        a = getattr(row, id_col_a)
        b = getattr(row, id_col_b)
        score = getattr(row, score_col)
        graph.add_edge(a, b, weight=float(score))
    return graph


def solve_one_to_one_assignment(
    accepted_pairs: pd.DataFrame,
    id_col_a: str = "id_a",
    id_col_b: str = "id_b",
    score_col: str = "score",
) -> pd.DataFrame:
    """Returns the subset of `accepted_pairs` that survive one-to-one
    constrained assignment (maximum total score, no record reused).
    """
    if accepted_pairs.empty:
        return accepted_pairs.copy()

    graph = build_score_graph(accepted_pairs, id_col_a, id_col_b, score_col)
    matched_edges = nx.max_weight_matching(graph, maxcardinality=False, weight="weight")
    matched_pairs = {frozenset(edge) for edge in matched_edges}

    keep_mask = accepted_pairs.apply(
        lambda row: frozenset({row[id_col_a], row[id_col_b]}) in matched_pairs, axis=1
    )
    return accepted_pairs[keep_mask].reset_index(drop=True)


def count_conflicts(accepted_pairs: pd.DataFrame, id_col_a: str, id_col_b: str) -> int:
    """Number of records that appear in more than one accepted pair -
    i.e. records with a genuine one-to-one conflict before constraining."""
    all_ids = pd.concat([accepted_pairs[id_col_a], accepted_pairs[id_col_b]])
    counts = all_ids.value_counts()
    return int((counts > 1).sum())
