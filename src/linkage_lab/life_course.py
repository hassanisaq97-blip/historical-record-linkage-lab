"""Aggregate accepted pairwise links into life courses (connected
components of the link graph) and run sanity checks for implausible
results, e.g. one record ending up transitively linked to more than one
record from the other source, or contradictory birth years.
"""

from __future__ import annotations

import networkx as nx
import pandas as pd

from . import config
from .data_generation import PLAUSIBLE_BIRTH_YEAR_MAX, PLAUSIBLE_BIRTH_YEAR_MIN


def build_link_graph(
    accepted_pairs: pd.DataFrame,
    census_raw: pd.DataFrame,
    parish_raw: pd.DataFrame,
) -> nx.Graph:
    census_lookup = census_raw.set_index("census_record_id")
    parish_lookup = parish_raw.set_index("parish_record_id")

    graph = nx.Graph()
    for pair in accepted_pairs.itertuples(index=False):
        census_node = ("census", pair.census_record_id)
        parish_node = ("parish", pair.parish_record_id)

        if census_node not in graph:
            record = census_lookup.loc[pair.census_record_id]
            birth_year_estimate = int(record["census_year"] - record["age"])
            graph.add_node(census_node, source="census", birth_year_estimate=birth_year_estimate)

        if parish_node not in graph:
            record = parish_lookup.loc[pair.parish_record_id]
            graph.add_node(parish_node, source="parish", birth_year_estimate=int(record["birth_year"]))

        graph.add_edge(census_node, parish_node)

    return graph


def _check_component(nodes: set, graph: nx.Graph) -> list[str]:
    issues = []
    n_census = sum(1 for n in nodes if graph.nodes[n]["source"] == "census")
    n_parish = sum(1 for n in nodes if graph.nodes[n]["source"] == "parish")

    if n_census > 1 or n_parish > 1:
        issues.append("multi_match")

    birth_years = [graph.nodes[n]["birth_year_estimate"] for n in nodes]
    if max(birth_years) - min(birth_years) > config.MAX_PLAUSIBLE_BIRTH_YEAR_SPREAD:
        issues.append("birth_year_conflict")

    if any(y < PLAUSIBLE_BIRTH_YEAR_MIN or y > PLAUSIBLE_BIRTH_YEAR_MAX for y in birth_years):
        issues.append("implausible_birth_year")

    return issues


def run_sanity_checks(graph: nx.Graph) -> pd.DataFrame:
    rows = []
    for i, nodes in enumerate(nx.connected_components(graph)):
        issues = _check_component(nodes, graph)
        rows.append(
            {
                "life_course_id": i,
                "n_nodes": len(nodes),
                "record_ids": sorted(n[1] for n in nodes),
                "birth_year_estimates": [graph.nodes[n]["birth_year_estimate"] for n in nodes],
                "issues": issues,
                "flagged": len(issues) > 0,
            }
        )
    return pd.DataFrame(rows)
