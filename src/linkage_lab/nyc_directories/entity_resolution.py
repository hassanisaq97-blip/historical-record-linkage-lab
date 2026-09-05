"""Aggregates accepted within-source links into entity clusters and runs
sanity checks. Deliberately NOT called "life course": these are single-
year, single-source records, so there is no time dimension to reconstruct
a life course from (see docs/limitations.md). What this represents is
entity resolution - deciding which directory line-entries most likely
describe the same real individual - traceable back to the original OCR
lines, and never asserted as a certain identity when linkage is only
probabilistic.
"""

from __future__ import annotations

import networkx as nx
import pandas as pd


def build_link_graph(accepted_pairs: pd.DataFrame, entries: pd.DataFrame) -> nx.Graph:
    indexed = entries.set_index("record_id")
    graph = nx.Graph()

    for record_id, row in indexed.iterrows():
        graph.add_node(
            record_id,
            surname=row.get("surname_std"),
            given_name=row.get("given_name_std"),
            occupation=row.get("occupation_canonical"),
            address_business=row.get("address_business_std"),
            address_home=row.get("address_home_std"),
        )

    for pair in accepted_pairs.itertuples(index=False):
        score = getattr(pair, "predicted_proba", None)
        graph.add_edge(
            pair.record_id_a,
            pair.record_id_b,
            score=float(score) if score is not None else None,
            occupation_jw=getattr(pair, "occupation_jw", None),
            best_address_jw=getattr(pair, "best_address_jw", None),
        )

    # Only keep nodes that participate in at least one accepted link -
    # isolated records are not "entities" produced by linkage.
    linked_nodes = {n for edge in graph.edges() for n in edge}
    return graph.subgraph(linked_nodes).copy()


def _check_component(nodes: set, graph: nx.Graph) -> list[str]:
    issues = []
    if len(nodes) > 2:
        issues.append("multi_match")

    edges = list(graph.subgraph(nodes).edges(data=True))
    if edges and all(
        (d.get("occupation_jw") or 0) < 0.5 and (d.get("best_address_jw") or 0) < 0.5 for _, _, d in edges
    ):
        issues.append("weak_corroboration")

    for _, _, d in edges:
        occ_jw = d.get("occupation_jw")
        if occ_jw is not None and occ_jw < 0.3:
            issues.append("conflicting_occupation")
            break

    for _, _, d in edges:
        addr_jw = d.get("best_address_jw")
        if addr_jw is not None and addr_jw < 0.2:
            issues.append("conflicting_address")
            break

    return issues


def run_sanity_checks(graph: nx.Graph) -> pd.DataFrame:
    rows = []
    for i, nodes in enumerate(nx.connected_components(graph)):
        issues = _check_component(nodes, graph)
        avg_score = pd.Series(
            [d.get("score") for _, _, d in graph.subgraph(nodes).edges(data=True) if d.get("score") is not None]
        ).mean()
        rows.append(
            {
                "entity_id": i,
                "n_records": len(nodes),
                "record_ids": sorted(nodes),
                "mean_link_confidence": avg_score,
                "issues": issues,
                "flagged": len(issues) > 0,
            }
        )
    return pd.DataFrame(rows)


def build_entity_table(graph: nx.Graph, checks: pd.DataFrame) -> pd.DataFrame:
    """One row per (entity, source record) - the traceable, source-linked
    output requested for entity resolution: entity id, source record id,
    year, name, occupation, address, and link confidence. Never labelled
    a certain identity - `mean_link_confidence` makes the probabilistic
    nature explicit.
    """
    rows = []
    for entity in checks.itertuples(index=False):
        for record_id in entity.record_ids:
            attrs = graph.nodes[record_id]
            rows.append(
                {
                    "entity_id": entity.entity_id,
                    "record_id": record_id,
                    "surname": attrs.get("surname"),
                    "given_name": attrs.get("given_name"),
                    "occupation": attrs.get("occupation"),
                    "address_business": attrs.get("address_business"),
                    "address_home": attrs.get("address_home"),
                    "mean_link_confidence": entity.mean_link_confidence,
                    "flagged": entity.flagged,
                    "issues": entity.issues,
                }
            )
    return pd.DataFrame(rows)
