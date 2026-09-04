"""Command-line entry points, one per pipeline stage. Wired together by
workflow/Snakefile, but each command also runs standalone.
"""

from __future__ import annotations

import argparse

import joblib
import pandas as pd

from . import (
    benchmark,
    blocking,
    config,
    data_generation,
    evaluation,
    features,
    life_course,
    linkage_llm,
    linkage_ml,
    linkage_rule_based,
    standardization,
    visualize,
)

PATHS = {
    "population": config.DATA_RAW_DIR / "ground_truth_population.csv",
    "census_raw": config.DATA_RAW_DIR / "census.csv",
    "parish_raw": config.DATA_RAW_DIR / "parish_register.csv",
    "census_std": config.DATA_PROCESSED_DIR / "census_std.csv",
    "parish_std": config.DATA_PROCESSED_DIR / "parish_std.csv",
    "candidate_pairs": config.DATA_PROCESSED_DIR / "candidate_pairs.csv",
    "labeled_pairs": config.DATA_PROCESSED_DIR / "labeled_pairs.csv",
    "predictions_rule_based": config.DATA_PROCESSED_DIR / "predictions_rule_based.csv",
    "predictions_ml": config.DATA_PROCESSED_DIR / "predictions_ml.csv",
    "ml_model": config.DATA_PROCESSED_DIR / "ml_model.joblib",
    "metrics_comparison": config.RESULTS_REPORTS_DIR / "metrics_comparison.csv",
    "error_examples_rule_based": config.RESULTS_REPORTS_DIR / "error_examples_rule_based.md",
    "error_examples_ml": config.RESULTS_REPORTS_DIR / "error_examples_ml.md",
    "life_course_report": config.RESULTS_REPORTS_DIR / "life_course_sanity_checks.md",
    "figure_comparison": config.RESULTS_FIGURES_DIR / "method_comparison.png",
    "figure_importance": config.RESULTS_FIGURES_DIR / "feature_importance.png",
}


def cmd_generate_data(_args) -> None:
    data_generation.save_all()


def cmd_standardize(_args) -> None:
    census_raw = pd.read_csv(PATHS["census_raw"])
    parish_raw = pd.read_csv(PATHS["parish_raw"])
    standardization.standardize_census(census_raw).to_csv(PATHS["census_std"], index=False)
    standardization.standardize_parish(parish_raw).to_csv(PATHS["parish_std"], index=False)


def cmd_build_dataset(_args) -> None:
    census_std = pd.read_csv(PATHS["census_std"])
    parish_std = pd.read_csv(PATHS["parish_std"])
    census_raw = pd.read_csv(PATHS["census_raw"])
    parish_raw = pd.read_csv(PATHS["parish_raw"])

    census_blocked = blocking.add_blocking_keys_census(census_std)
    parish_blocked = blocking.add_blocking_keys_parish(parish_std)
    pairs = blocking.generate_candidate_pairs(census_blocked, parish_blocked)
    pairs.to_csv(PATHS["candidate_pairs"], index=False)

    pair_features = features.build_candidate_features(pairs, census_std, parish_std)
    labeled = benchmark.build_full_benchmark(pairs, census_raw, parish_raw)
    full = pair_features.merge(
        labeled[["census_record_id", "parish_record_id", "is_true_match", "split"]],
        on=["census_record_id", "parish_record_id"],
    )
    full.to_csv(PATHS["labeled_pairs"], index=False)

    n_candidates = len(full)
    n_true_matches_in_candidates = int(full["is_true_match"].sum())
    n_true_overlap = len(set(census_raw["person_id"]) & set(parish_raw["person_id"]))
    blocking_recall = n_true_matches_in_candidates / n_true_overlap if n_true_overlap else 0.0

    print(f"Candidate pairs: {n_candidates}, true matches among them: {n_true_matches_in_candidates}")
    print(full["split"].value_counts())
    print(f"Blocking recall: {n_true_matches_in_candidates}/{n_true_overlap} = {blocking_recall:.1%}")

    with open(config.RESULTS_REPORTS_DIR / "blocking_recall.md", "w") as f:
        f.write("# Blocking recall\n\n")
        f.write(
            "Blocking begrænser hvilke par der overhovedet kan sammenlignes. "
            "Denne metrik viser, hvor stor en andel af de faktiske sande matches "
            "(individer der findes i både census og kirkebog) der overlever "
            "blocking-trinnet og dermed kan genfindes af linkage-metoderne "
            "nedenfor. Par der ikke overlever blocking, kan aldrig blive TP - "
            "uanset hvor god linkage-metoden er.\n\n"
        )
        f.write(f"- Sande overlappende individer (i begge kilder): {n_true_overlap}\n")
        f.write(f"- Heraf med mindst ét candidate-par efter blocking: {n_true_matches_in_candidates}\n")
        f.write(f"- **Blocking recall: {blocking_recall:.1%}**\n")


def cmd_link_rule_based(_args) -> None:
    df = pd.read_csv(PATHS["labeled_pairs"])
    df["predicted_match"] = linkage_rule_based.predict(df)
    df[["census_record_id", "parish_record_id", "split", "is_true_match", "predicted_match"]].to_csv(
        PATHS["predictions_rule_based"], index=False
    )


def cmd_link_ml(_args) -> None:
    df = pd.read_csv(PATHS["labeled_pairs"])
    train_df = df[df["split"] == "train"]
    model = linkage_ml.train_model(train_df)
    joblib.dump(model, PATHS["ml_model"])

    df["predicted_match"] = linkage_ml.predict(model, df)
    df["predicted_proba"] = linkage_ml.predict_proba(model, df)
    df[
        ["census_record_id", "parish_record_id", "split", "is_true_match", "predicted_match", "predicted_proba"]
    ].to_csv(PATHS["predictions_ml"], index=False)

    importances = linkage_ml.feature_importances(model)
    visualize.plot_feature_importance(importances, PATHS["figure_importance"])
    importances.to_csv(config.RESULTS_REPORTS_DIR / "feature_importances.csv", header=["importance"])


def _format_markdown_table(df: pd.DataFrame) -> str:
    return df.to_markdown(index=False)


def cmd_evaluate(_args) -> None:
    census_raw = pd.read_csv(PATHS["census_raw"])
    parish_raw = pd.read_csv(PATHS["parish_raw"])
    labeled = pd.read_csv(PATHS["labeled_pairs"])

    rule_preds = pd.read_csv(PATHS["predictions_rule_based"])
    ml_preds = pd.read_csv(PATHS["predictions_ml"])

    rule_test = rule_preds[rule_preds["split"] == "test"]
    ml_test = ml_preds[ml_preds["split"] == "test"]

    metrics = {
        "rule_based": evaluation.compute_metrics(rule_test["is_true_match"], rule_test["predicted_match"]),
        "ml_random_forest": evaluation.compute_metrics(ml_test["is_true_match"], ml_test["predicted_match"]),
    }
    comparison = evaluation.build_comparison_table(metrics)
    comparison.to_csv(PATHS["metrics_comparison"])
    print(comparison)

    visualize.plot_method_comparison(comparison, PATHS["figure_comparison"])

    labeled_test = labeled[labeled["split"] == "test"].merge(
        rule_test[["census_record_id", "parish_record_id"]], on=["census_record_id", "parish_record_id"]
    )

    rule_errors = evaluation.get_error_examples(
        labeled_test, rule_test["predicted_match"], census_raw, parish_raw
    )
    ml_labeled_test = labeled[labeled["split"] == "test"].merge(
        ml_test[["census_record_id", "parish_record_id"]], on=["census_record_id", "parish_record_id"]
    )
    ml_errors = evaluation.get_error_examples(
        ml_labeled_test, ml_test["predicted_match"], census_raw, parish_raw
    )

    for name, errors, path in (
        ("rule-based", rule_errors, PATHS["error_examples_rule_based"]),
        ("ml", ml_errors, PATHS["error_examples_ml"]),
    ):
        with open(path, "w") as f:
            f.write(f"# Fejl-eksempler: {name}\n\n## False positives\n\n")
            f.write(_format_markdown_table(errors["false_positives"]) + "\n\n")
            f.write("## False negatives\n\n")
            f.write(_format_markdown_table(errors["false_negatives"]) + "\n")


def _life_course_section(method_name: str, predictions: pd.DataFrame, census_raw, parish_raw) -> tuple[str, pd.DataFrame]:
    accepted = predictions[predictions["predicted_match"] == 1][["census_record_id", "parish_record_id"]]
    graph = life_course.build_link_graph(accepted, census_raw, parish_raw)
    checks = life_course.run_sanity_checks(graph)

    n_total = len(checks)
    n_flagged = int(checks["flagged"].sum())
    issue_counts = checks[checks["flagged"]]["issues"].explode().value_counts()

    section = [f"## Metode: {method_name}\n"]
    section.append(f"Antal rekonstruerede livsforløb (sammenhængende komponenter): {n_total}\n")
    section.append(f"Heraf markeret med mindst ét problem: {n_flagged} ({n_flagged / n_total:.1%} hvis n_total > 0)\n")
    section.append("Fordeling af problemtyper:\n")
    section.append("```\n" + issue_counts.to_string() + "\n```\n")
    section.append("Eksempler på markerede livsforløb:\n")
    flagged_examples = checks[checks["flagged"]].head(5)
    section.append(
        _format_markdown_table(
            flagged_examples[["life_course_id", "n_nodes", "record_ids", "birth_year_estimates", "issues"]]
        )
    )
    section.append("\n")
    return "\n".join(section), checks


def cmd_life_course(_args) -> None:
    census_raw = pd.read_csv(PATHS["census_raw"])
    parish_raw = pd.read_csv(PATHS["parish_raw"])
    rule_preds = pd.read_csv(PATHS["predictions_rule_based"])
    ml_preds = pd.read_csv(PATHS["predictions_ml"])

    rule_section, rule_checks = _life_course_section("rule-based", rule_preds, census_raw, parish_raw)
    ml_section, ml_checks = _life_course_section("ml_random_forest", ml_preds, census_raw, parish_raw)

    rule_checks.to_csv(config.RESULTS_REPORTS_DIR / "life_course_checks_rule_based.csv", index=False)
    ml_checks.to_csv(config.RESULTS_REPORTS_DIR / "life_course_checks_ml.csv", index=False)

    with open(PATHS["life_course_report"], "w") as f:
        f.write("# Livsforløb: sanity checks\n\n")
        f.write(
            "Livsforløb konstrueres som sammenhængende komponenter i graf af "
            "accepterede par-links (uden en one-to-one-begrænsning på match). "
            "Se docs/limitations.md for diskussion af denne begrænsning.\n\n"
        )
        f.write(rule_section)
        f.write("\n")
        f.write(ml_section)

    print(f"Rule-based life courses: {len(rule_checks)}, flagged: {int(rule_checks['flagged'].sum())}")
    print(f"ML life courses: {len(ml_checks)}, flagged: {int(ml_checks['flagged'].sum())}")


def cmd_link_llm_experimental(_args) -> None:
    import os

    census_raw = pd.read_csv(PATHS["census_raw"])
    parish_raw = pd.read_csv(PATHS["parish_raw"])
    ml_preds = pd.read_csv(PATHS["predictions_ml"])

    gray_zone = linkage_llm.select_gray_zone_pairs(ml_preds)
    gray_zone = evaluation.attach_raw_fields(gray_zone, census_raw, parish_raw)
    gray_zone["census_year"] = data_generation.CENSUS_YEAR

    report_path = config.RESULTS_REPORTS_DIR / "llm_experimental_supplement.md"

    if not os.environ.get("ANTHROPIC_API_KEY"):
        with open(report_path, "w") as f:
            f.write("# LLM-assisteret linkage (eksperimentelt tillæg) - IKKE kørt\n\n")
            f.write(
                f"Fandt {len(gray_zone)} 'gråzone'-par (ML predicted_proba mellem "
                f"{linkage_llm.GRAY_ZONE_LOW} og {linkage_llm.GRAY_ZONE_HIGH}), men "
                "ANTHROPIC_API_KEY er ikke sat, så intet API-kald er foretaget.\n\n"
                "Dette er forventet: dette trin kræver brugerens egen API-nøgle og "
                "indgår bevidst ikke i hovedpipelinen eller i README's rapporterede "
                "precision/recall/F1-tal. Se docs/limitations.md.\n"
            )
        print(f"ANTHROPIC_API_KEY not set - wrote placeholder report for {len(gray_zone)} gray-zone pairs.")
        return

    import anthropic

    client = anthropic.Anthropic()
    results = []
    for _, row in gray_zone.iterrows():
        prompt = linkage_llm.build_prompt(row)
        raw_response = linkage_llm.classify_pair_with_llm(prompt, client)
        results.append(linkage_llm.parse_response(raw_response))

    gray_zone["llm_verdict"] = results
    gray_zone.to_csv(config.RESULTS_REPORTS_DIR / "llm_experimental_supplement.csv", index=False)
    print(f"Classified {len(gray_zone)} gray-zone pairs with the LLM supplement.")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="linkage_lab")
    subparsers = parser.add_subparsers(dest="command", required=True)

    commands = {
        "generate-data": cmd_generate_data,
        "standardize": cmd_standardize,
        "build-dataset": cmd_build_dataset,
        "link-rule-based": cmd_link_rule_based,
        "link-ml": cmd_link_ml,
        "evaluate": cmd_evaluate,
        "life-course": cmd_life_course,
        "link-llm-experimental": cmd_link_llm_experimental,
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
