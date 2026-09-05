"""Command-line entry points for the NYC-directories real-world case
study, one per pipeline stage - mirrors `linkage_lab.cli`'s structure.
"""

from __future__ import annotations

import argparse

import joblib
import pandas as pd

from .. import config, constrained_assignment, visualize
from .. import evaluation as generic_evaluation
from . import (
    benchmark,
    blocking,
    data_acquisition,
    data_quality,
    entity_resolution,
    evaluation,
    features,
    linkage_ml,
    linkage_rule_based,
    parsing,
    standardization,
)

PATHS = {
    "parsed_entries": config.NYC_DIR_PROCESSED_DIR / "parsed_entries.csv",
    "standardized_entries": config.NYC_DIR_PROCESSED_DIR / "standardized_entries.csv",
    "blocked_entries": config.NYC_DIR_PROCESSED_DIR / "blocked_entries.csv",
    "candidate_pairs": config.NYC_DIR_PROCESSED_DIR / "candidate_pairs.csv",
    "candidate_features": config.NYC_DIR_PROCESSED_DIR / "candidate_features.csv",
    "predictions_rule_based": config.NYC_DIR_PROCESSED_DIR / "predictions_rule_based.csv",
    "predictions_ml": config.NYC_DIR_PROCESSED_DIR / "predictions_ml.csv",
    "predictions_rule_based_full": config.NYC_DIR_PROCESSED_DIR / "predictions_rule_based_full.csv",
    "predictions_ml_full": config.NYC_DIR_PROCESSED_DIR / "predictions_ml_full.csv",
    "constrained_ml": config.NYC_DIR_PROCESSED_DIR / "constrained_ml.csv",
    "ml_model": config.NYC_DIR_PROCESSED_DIR / "ml_model.joblib",
}


def cmd_acquire(_args) -> None:
    data_acquisition.save_parsed_dataset()


def cmd_standardize(_args) -> None:
    df = pd.read_csv(PATHS["parsed_entries"])
    out = standardization.standardize_entries(df)
    out.to_csv(PATHS["standardized_entries"], index=False)


def cmd_data_quality(_args) -> None:
    parsed = pd.read_csv(PATHS["parsed_entries"])
    standardized = pd.read_csv(PATHS["blocked_entries"])
    report = data_quality.compute_report(parsed, standardized)
    out_path = config.NYC_DIR_RESULTS_REPORTS_DIR / "data_quality_report.md"
    out_path.write_text(report, encoding="utf-8")
    print(f"Wrote {out_path}")


def cmd_block(_args) -> None:
    df = pd.read_csv(PATHS["standardized_entries"])
    blocked = blocking.add_blocking_keys(df)
    blocked.to_csv(PATHS["blocked_entries"], index=False)
    pairs = blocking.generate_candidate_pairs(blocked)
    pairs.to_csv(PATHS["candidate_pairs"], index=False)

    stats = blocking.compute_reduction_stats(len(blocked), len(pairs))
    with open(config.NYC_DIR_RESULTS_REPORTS_DIR / "blocking_reduction.md", "w") as f:
        f.write("# Blocking: candidate space reduction\n\n")
        f.write(f"- Records: {stats['n_records']}\n")
        f.write(f"- Alle mulige par: {stats['all_possible_pairs']}\n")
        f.write(f"- Kandidatpar efter blocking: {stats['candidate_pairs']}\n")
        f.write(f"- **Reduktion: {stats['reduction_ratio']:.2%}**\n\n")
        f.write(
            "Blocking recall kan ikke måles meningsfuldt på det manuelle benchmark her: "
            "de 92 benchmark-par blev udtrukket FRA kandidatparrene efter blocking, så "
            "recall ville tautologisk være 100%. Se docs/limitations.md for en "
            "proxy-baseret vurdering af blocking's false-negative-risiko.\n"
        )
    print(stats)


def cmd_features(_args) -> None:
    entries = pd.read_csv(PATHS["blocked_entries"])
    pairs = pd.read_csv(PATHS["candidate_pairs"])
    feats = features.build_candidate_features(pairs, entries)
    feats.to_csv(PATHS["candidate_features"], index=False)


def cmd_link_rule_based(_args) -> None:
    manual_labels = benchmark.load_manual_labels()
    feats = pd.read_csv(PATHS["candidate_features"])
    labeled = benchmark.build_labeled_features(feats, manual_labels)
    labeled["predicted_match"] = linkage_rule_based.predict(labeled)
    labeled.to_csv(PATHS["predictions_rule_based"], index=False)

    # Also score every candidate pair in the full (unlabelled) corpus, so
    # entity resolution / constrained assignment operate at realistic
    # scale rather than on the 92-pair evaluation benchmark alone.
    full = feats.copy()
    full["predicted_match"] = linkage_rule_based.predict(full)
    full.to_csv(PATHS["predictions_rule_based_full"], index=False)


def cmd_link_ml(_args) -> None:
    manual_labels = benchmark.load_manual_labels()
    feats = pd.read_csv(PATHS["candidate_features"])
    labeled = benchmark.build_labeled_features(feats, manual_labels)

    train_df = labeled[labeled["split"] == "train"]
    model = linkage_ml.train_model(train_df)
    joblib.dump(model, PATHS["ml_model"])

    labeled["predicted_match"] = linkage_ml.predict(model, labeled)
    labeled["predicted_proba"] = linkage_ml.predict_proba(model, labeled)
    labeled.to_csv(PATHS["predictions_ml"], index=False)

    full = feats.copy()
    full["predicted_match"] = linkage_ml.predict(model, full)
    full["predicted_proba"] = linkage_ml.predict_proba(model, full)
    full.to_csv(PATHS["predictions_ml_full"], index=False)

    importances = pd.Series(model.feature_importances_, index=linkage_ml.FEATURE_COLUMNS).sort_values(
        ascending=False
    )
    importances.to_csv(config.NYC_DIR_RESULTS_REPORTS_DIR / "feature_importances.csv", header=["importance"])
    visualize.plot_feature_importance(importances, config.NYC_DIR_RESULTS_FIGURES_DIR / "feature_importance.png")


def cmd_constrained_assignment(_args) -> None:
    ml_preds = pd.read_csv(PATHS["predictions_ml_full"])
    accepted = ml_preds[ml_preds["predicted_match"] == 1].copy()

    n_conflicts_before = constrained_assignment.count_conflicts(accepted, "record_id_a", "record_id_b")
    constrained = constrained_assignment.solve_one_to_one_assignment(
        accepted, id_col_a="record_id_a", id_col_b="record_id_b", score_col="predicted_proba"
    )
    n_conflicts_after = constrained_assignment.count_conflicts(constrained, "record_id_a", "record_id_b")

    constrained.to_csv(PATHS["constrained_ml"], index=False)

    with open(config.NYC_DIR_RESULTS_REPORTS_DIR / "constrained_assignment.md", "w") as f:
        f.write("# Constrained one-to-one assignment (ML-metode)\n\n")
        f.write(f"- Accepterede par (uafhaengig klassifikation): {len(accepted)}\n")
        f.write(f"- Records med konflikt (>1 accepteret link) FOER constraint: {n_conflicts_before}\n")
        f.write(f"- Accepterede par EFTER one-to-one constraint: {len(constrained)}\n")
        f.write(f"- Records med konflikt EFTER constraint: {n_conflicts_after}\n")
        f.write(f"- Par droppet af constraint: {len(accepted) - len(constrained)}\n")
    print(f"conflicts before={n_conflicts_before}, after={n_conflicts_after}, pairs kept={len(constrained)}/{len(accepted)}")


def _format_markdown_table(df: pd.DataFrame) -> str:
    return df.to_markdown(index=False)


def cmd_evaluate(_args) -> None:
    entries = pd.read_csv(PATHS["blocked_entries"])
    rule_preds = pd.read_csv(PATHS["predictions_rule_based"])
    ml_preds = pd.read_csv(PATHS["predictions_ml"])

    rule_test = rule_preds[rule_preds["split"] == "test"]
    ml_test = ml_preds[ml_preds["split"] == "test"]

    metrics = {
        "rule_based": generic_evaluation.compute_metrics(rule_test["is_match"], rule_test["predicted_match"]),
        "ml_random_forest": generic_evaluation.compute_metrics(ml_test["is_match"], ml_test["predicted_match"]),
    }
    comparison = generic_evaluation.build_comparison_table(metrics)
    comparison.to_csv(config.NYC_DIR_RESULTS_REPORTS_DIR / "metrics_comparison.csv")
    print(comparison)
    visualize.plot_method_comparison(comparison, config.NYC_DIR_RESULTS_FIGURES_DIR / "method_comparison.png")

    rule_errors = evaluation.get_error_examples(rule_test, rule_test["predicted_match"], entries)
    ml_errors = evaluation.get_error_examples(ml_test, ml_test["predicted_match"], entries)

    for name, errors, fname in (
        ("rule-based", rule_errors, "error_examples_rule_based.md"),
        ("ml", ml_errors, "error_examples_ml.md"),
    ):
        with open(config.NYC_DIR_RESULTS_REPORTS_DIR / fname, "w") as f:
            f.write(f"# Fejl-eksempler: {name}\n\n## False positives\n\n")
            f.write(_format_markdown_table(errors["false_positives"]) + "\n\n")
            f.write("## False negatives\n\n")
            f.write(_format_markdown_table(errors["false_negatives"]) + "\n")

    # Threshold behaviour: precision/recall of the ML model at varying
    # probability thresholds, on the (small) test fold.
    thresholds = [0.3, 0.4, 0.5, 0.6, 0.7, 0.8]
    rows = []
    for t in thresholds:
        pred_t = (ml_test["predicted_proba"] >= t).astype(int)
        m = generic_evaluation.compute_metrics(ml_test["is_match"], pred_t)
        rows.append({"threshold": t, **m})
    threshold_df = pd.DataFrame(rows)
    threshold_df.to_csv(config.NYC_DIR_RESULTS_REPORTS_DIR / "threshold_behaviour.csv", index=False)


def cmd_entity_resolution(_args) -> None:
    entries = pd.read_csv(PATHS["blocked_entries"])

    for method_name, preds_path, accepted_col_source in (
        ("rule_based", PATHS["predictions_rule_based_full"], "predicted_match"),
        ("ml_independent", PATHS["predictions_ml_full"], "predicted_match"),
    ):
        preds = pd.read_csv(preds_path)
        accepted = preds[preds[accepted_col_source] == 1]
        graph = entity_resolution.build_link_graph(accepted, entries)
        checks = entity_resolution.run_sanity_checks(graph)
        checks.to_csv(config.NYC_DIR_RESULTS_REPORTS_DIR / f"entity_checks_{method_name}.csv", index=False)
        _write_entity_report(method_name, checks)

    constrained = pd.read_csv(PATHS["constrained_ml"])
    graph = entity_resolution.build_link_graph(constrained, entries)
    checks = entity_resolution.run_sanity_checks(graph)
    checks.to_csv(config.NYC_DIR_RESULTS_REPORTS_DIR / "entity_checks_ml_constrained.csv", index=False)
    _write_entity_report("ml_constrained", checks)

    entity_table = entity_resolution.build_entity_table(graph, checks)
    entity_table.to_csv(config.NYC_DIR_RESULTS_REPORTS_DIR / "entities_ml_constrained.csv", index=False)


def _write_entity_report(method_name: str, checks: pd.DataFrame) -> None:
    path = config.NYC_DIR_RESULTS_REPORTS_DIR / f"entity_resolution_{method_name}.md"
    n_total = len(checks)
    n_flagged = int(checks["flagged"].sum()) if n_total else 0
    issue_counts = checks[checks["flagged"]]["issues"].explode().value_counts() if n_total else pd.Series(dtype=int)

    with open(path, "w") as f:
        f.write(f"# Entity resolution sanity checks: {method_name}\n\n")
        f.write(f"Antal entities (sammenhaengende komponenter): {n_total}\n\n")
        if n_total:
            f.write(f"Markeret med mindst et problem: {n_flagged} ({n_flagged / n_total:.1%})\n\n")
        f.write("Fordeling af problemtyper:\n\n```\n" + issue_counts.to_string() + "\n```\n")


def cmd_cross_validate_parser(_args) -> None:
    labeled_csv = config.NYC_DIR_RAW_DIR / "nypl-labeled-70-training.csv"
    cv = parsing.cross_validate_parser(labeled_csv)
    with open(config.NYC_DIR_RESULTS_REPORTS_DIR / "parser_cross_validation.md", "w") as f:
        f.write("# CRF-parser: krydsvalidering paa NYPL's 70 labelede eksempler\n\n")
        f.write(f"Folds: {cv['n_splits']}\n\n")
        f.write(f"Token-niveau F1 pr. fold: {[round(x, 4) for x in cv['fold_f1_scores']]}\n\n")
        f.write(f"**Gennemsnitlig token-F1: {cv['mean_token_f1']:.4f}**\n")
    print(cv)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="nyc_directories")
    subparsers = parser.add_subparsers(dest="command", required=True)

    commands = {
        "acquire": cmd_acquire,
        "standardize": cmd_standardize,
        "block": cmd_block,
        "data-quality": cmd_data_quality,
        "features": cmd_features,
        "link-rule-based": cmd_link_rule_based,
        "link-ml": cmd_link_ml,
        "constrained-assignment": cmd_constrained_assignment,
        "evaluate": cmd_evaluate,
        "entity-resolution": cmd_entity_resolution,
        "cross-validate-parser": cmd_cross_validate_parser,
    }
    for name, func in commands.items():
        sub = subparsers.add_parser(name)
        sub.set_defaults(func=func)
    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
