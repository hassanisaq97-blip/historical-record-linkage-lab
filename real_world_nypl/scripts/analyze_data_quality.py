"""Kvantificerer datakvalitet og finder konkrete "samme person, flere
records"-eksempler i det udtrukne NYPL-datasæt.

Læser output fra build_subject_name_subset.py og skriver to
Markdown-rapporter (på dansk) i real_world_nypl/analysis/.

Kør:
    python3 real_world_nypl/scripts/analyze_data_quality.py /tmp/nypl_pd
"""

from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd

DATA_DIR = Path(__file__).resolve().parents[1] / "data"
ANALYSIS_DIR = Path(__file__).resolve().parents[1] / "analysis"

KEY_FIELDS = [
    "Title", "Date", "Date Start", "Date End", "Contributor",
    "Subject Name", "Subject Topical", "Genre", "Description", "Collection Title",
]


def missing_value_table(items_subset: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for col in KEY_FIELDS:
        n_missing = items_subset[col].isna().sum()
        rows.append(
            {
                "felt": col,
                "n_missing": int(n_missing),
                "andel_missing": n_missing / len(items_subset),
            }
        )
    return pd.DataFrame(rows)


def near_duplicate_rate(items_subset: pd.DataFrame) -> float:
    dup_mask = items_subset.duplicated(subset=["Title", "Collection Title", "Date"], keep=False)
    return dup_mask.mean()


def write_data_quality_report(items_subset: pd.DataFrame, unique_names: pd.DataFrame, snapshot_full_size: int) -> None:
    person_names = unique_names[unique_names["looks_like_person"]]
    org_names = unique_names[~unique_names["looks_like_person"]]

    missing_table = missing_value_table(items_subset)
    dup_rate = near_duplicate_rate(items_subset)

    lines = []
    lines.append("# Datakvalitet: NYPL public-domain snapshot, Subject Name-felt\n")
    lines.append(
        f"Kilde: `NYPL-publicdomain/data-and-utilities` (snapshot frosset 2015-12-30). "
        f"Fuldt snapshot: **{snapshot_full_size} items**. "
        f"Heraf med mindst ét 'Subject Name': **{len(items_subset)}** "
        f"({len(items_subset) / snapshot_full_size:.1%}).\n"
    )

    lines.append("## Manglende værdier (blandt items med >=1 Subject Name)\n")
    lines.append(missing_table.to_markdown(index=False))
    lines.append("")

    lines.append("## Nær-dubletter\n")
    lines.append(
        f"Andel items, der deler (Title, Collection Title, Date) med mindst én anden "
        f"post: **{dup_rate:.1%}**. Dette er katalogpraksis (fx samme fotosession "
        f"registreret som flere separate 'captures'/negativer), ikke fejl i vores "
        f"udtræk - men det betyder, at en del af 'flere records for samme person' i "
        f"praksis er næsten-identiske dubletter uden reelt linkage-problem.\n"
    )

    lines.append("## Subject Name: person vs. organisation/andet\n")
    lines.append(
        "Feltet 'Subject Name' i MODS-skemaet dækker eksplicit BÅDE personer OG "
        "organisationer/bygninger/begivenheder (jf. NYPL's egen felt-dokumentation: "
        "\"people or organizations described or depicted\"). Vi har derfor bygget en "
        "simpel, gennemsigtig heuristik (komma til stede, ingen parentes, ingen "
        "virksomheds-/institutionsnøgleord) til at adskille de to - IKKE antaget at "
        "alle værdier er personer.\n"
    )
    lines.append(f"- Unikke Subject Name-strenge i alt: **{len(unique_names)}**")
    lines.append(f"- Heraf klassificeret som person: **{len(person_names)}**")
    lines.append(f"- Heraf klassificeret som organisation/andet: **{len(org_names)}**\n")

    lines.append("### Top 10 hyppigste ORGANISATIONER/andet (bekræfter at feltet er blandet)\n")
    lines.append(org_names.head(10)[["name", "n_items"]].to_markdown(index=False))
    lines.append("")

    lines.append("## Records pr. person (kun heuristisk person-klassificerede navne)\n")
    lines.append(f"- Personer med >=2 items: **{(person_names['n_items'] >= 2).sum()}**")
    lines.append(f"- Personer med >=5 items: **{(person_names['n_items'] >= 5).sum()}**")
    lines.append(f"- Personer med >=10 items: **{(person_names['n_items'] >= 10).sum()}**")
    top_person = person_names.loc[person_names["n_items"].idxmax()]
    lines.append(f"- Højeste antal items for én person: **{top_person['n_items']}** "
                 f"({top_person['name']})\n")

    lines.append("## Titel-diversitet pr. person (er 'flere records' reelt forskellige poster?)\n")
    multi = person_names[person_names["n_items"] >= 2]
    lines.append(
        f"Blandt de {len(multi)} personer med >=2 items:\n"
        f"- Andel hvor ALLE poster har identisk titel (0 reel tekstvariation): "
        f"**{(multi['n_distinct_titles'] == 1).mean():.1%}**\n"
        f"- Andel hvor >80% af titlerne er indbyrdes forskellige (reel diversitet): "
        f"**{(multi['distinct_title_ratio'] > 0.8).mean():.1%}**\n"
    )

    (ANALYSIS_DIR / "data_quality_report.md").write_text("\n".join(lines), encoding="utf-8")
    print(f"Skrev {ANALYSIS_DIR / 'data_quality_report.md'}")


def write_same_person_examples(snapshot_dir: Path, items_full: pd.DataFrame, unique_names: pd.DataFrame) -> None:
    person_names = unique_names[unique_names["looks_like_person"]]

    chosen = []
    # Høj frekvens, høj duplikering (kritisk eksempel)
    chosen += ["Bellew, Kyrle, 1855-1911"]
    # Høj frekvens, kendte historiske figurer, høj titel-diversitet
    chosen += ["Dickens, Charles, 1812-1870", "Lincoln, Abraham, 1809-1865", "Ramses II, King of Egypt"]
    # Moderat frekvens, mindre verdenskendte personer
    for name in ["Castle, Vernon, 1887-1918", "Lyons, Denny, 1866-1929", "Camprubí, Mariano", "Horemheb, King of Egypt"]:
        if name in person_names["name"].values:
            chosen.append(name)
    # Suppler med et tilfældigt, reproducerbart udvalg af mid-frekvente navne
    mid = person_names[(person_names["n_items"] >= 3) & (person_names["n_items"] <= 10)]
    sampled = mid.sample(n=min(10, len(mid)), random_state=42)["name"].tolist()
    for name in sampled:
        if name not in chosen:
            chosen.append(name)
    chosen = chosen[:18]

    lines = ["# Eksempler: samme person i flere records\n"]
    lines.append(
        "Nedenstående er udtrukket direkte fra det gemte datasæt "
        "(`data/nypl_items_with_subject_name.csv`) - ingen af eksemplerne er "
        "konstrueret eller redigeret.\n"
    )

    display_cols = ["Title", "Date", "Genre", "Collection Title", "Contributor"]

    for name in chosen:
        mask = items_full["Subject Name"].str.contains(name, case=False, na=False, regex=False)
        subset = items_full.loc[mask, display_cols].head(5)
        n_total = int(mask.sum())
        lines.append(f"## {name} ({n_total} records i alt)\n")
        lines.append(subset.to_markdown(index=False))
        lines.append("")

    (ANALYSIS_DIR / "same_person_examples.md").write_text("\n".join(lines), encoding="utf-8")
    print(f"Skrev {ANALYSIS_DIR / 'same_person_examples.md'} med {len(chosen)} eksempler")


def main() -> None:
    snapshot_dir = Path(sys.argv[1] if len(sys.argv) > 1 else "/tmp/nypl_pd")
    ANALYSIS_DIR.mkdir(parents=True, exist_ok=True)

    items_subset = pd.read_csv(DATA_DIR / "nypl_items_with_subject_name.csv", dtype=str)
    unique_names = pd.read_csv(DATA_DIR / "nypl_unique_subject_names.csv")
    unique_names["looks_like_person"] = unique_names["looks_like_person"].astype(bool)

    csv_files = sorted((snapshot_dir / "items").glob("pd_items_*.csv"))
    full_size = sum(len(pd.read_csv(f, dtype=str, usecols=["UUID"])) for f in csv_files)

    write_data_quality_report(items_subset, unique_names, full_size)
    write_same_person_examples(snapshot_dir, items_subset, unique_names)


if __name__ == "__main__":
    main()
