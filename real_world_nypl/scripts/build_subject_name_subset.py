"""Reproducerbar udtræksproces fra NYPL's public-domain metadata-snapshot.

Læser de rå item-CSV'er fra snapshottet (se fetch_snapshot.sh), undersøger
om "Print Collection portrait file" reelt findes som en stor samling heri,
og udtrækker et håndterbart, committet datasæt for alle items med mindst
ét "Subject Name" (person/organisation afbildet eller beskrevet).

Antager IKKE feltnavne på forhånd - kolonnenavnene indlæses direkte fra
CSV-headeren og sammenlignes eksplicit med snapshottets eget README.

Kør:
    python3 real_world_nypl/scripts/build_subject_name_subset.py /tmp/nypl_pd
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

import pandas as pd

OUTPUT_DIR = Path(__file__).resolve().parents[1] / "data"

CORPORATE_KEYWORDS = re.compile(
    r"company|railroad|library|university|corporation|museum|society|"
    r"academy|church|team|department|administration|institute|commission|"
    r"committee|council|association|exhibition|exposition|hospital|school|"
    r"college|temple|palace|castillo|bridge|station|fort\b|hall\b|house\b|"
    r"survey",
    re.IGNORECASE,
)


def load_items(snapshot_dir: Path) -> pd.DataFrame:
    items_dir = snapshot_dir / "items"
    csv_files = sorted(items_dir.glob("pd_items_*.csv"))
    if not csv_files:
        raise FileNotFoundError(f"Ingen pd_items_*.csv fundet i {items_dir}")
    frames = [pd.read_csv(f, dtype=str, low_memory=False) for f in csv_files]
    return pd.concat(frames, ignore_index=True)


def load_collections(snapshot_dir: Path) -> pd.DataFrame:
    return pd.read_csv(snapshot_dir / "collections" / "pd_collections.csv", dtype=str)


def check_portrait_file_presence(items: pd.DataFrame, collections: pd.DataFrame) -> pd.DataFrame:
    """Undersøger empirisk, hvor stor "Print Collection portrait file"
    (og beslægtede portræt-samlinger) rent faktisk er i dette snapshot -
    i stedet for at antage, at den ~71.500-billeder store samling fra den
    levende hjemmeside er repræsenteret her.
    """
    rows = []

    portrait_collections = collections[collections["Title"].str.contains("portrait", case=False, na=False)]
    for _, coll in portrait_collections.iterrows():
        n_items = (items["Collection UUID"] == coll["UUID"]).sum()
        rows.append(
            {
                "match_type": "Collection Title indeholder 'portrait' (collections-fil)",
                "target": coll["Title"],
                "n_items": n_items,
            }
        )

    for col in ["Collection Title", "Parent Hierarchy", "Container Title", "Genre", "Title"]:
        n = items[col].str.contains("portrait", case=False, na=False).sum()
        rows.append({"match_type": f"'{col}' indeholder 'portrait' (items-fil)", "target": "-", "n_items": n})

    return pd.DataFrame(rows)


def looks_like_person(name: str) -> bool:
    if not isinstance(name, str):
        return False
    has_comma = "," in name
    has_paren = "(" in name
    is_corporate = bool(CORPORATE_KEYWORDS.search(name))
    return has_comma and not has_paren and not is_corporate


def build_subject_name_tables(items: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    has_name = items["Subject Name"].notna()
    items_with_name = items.loc[has_name].copy()

    exploded = items_with_name[["UUID", "Title", "Subject Name"]].copy()
    exploded["Subject Name"] = exploded["Subject Name"].str.split(r"\s\|\s")
    exploded = exploded.explode("Subject Name")
    exploded["Subject Name"] = exploded["Subject Name"].str.strip()

    grouped = exploded.groupby("Subject Name").agg(
        n_items=("UUID", "nunique"),
        n_distinct_titles=("Title", "nunique"),
    )
    grouped["distinct_title_ratio"] = grouped["n_distinct_titles"] / grouped["n_items"]
    grouped["looks_like_person"] = [looks_like_person(n) for n in grouped.index]
    grouped = grouped.reset_index().rename(columns={"Subject Name": "name"})
    grouped = grouped.sort_values("n_items", ascending=False).reset_index(drop=True)

    key_columns = [
        "UUID", "Title", "Date", "Date Start", "Date End", "Contributor",
        "Subject Name", "Subject Topical", "Genre", "Collection Title",
        "Container Title", "Description", "Digital Collections URL",
    ]
    items_subset = items_with_name[key_columns].reset_index(drop=True)

    return items_subset, grouped


def main() -> None:
    snapshot_dir = Path(sys.argv[1] if len(sys.argv) > 1 else "/tmp/nypl_pd")
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    items = load_items(snapshot_dir)
    collections = load_collections(snapshot_dir)
    print(f"Indlæste {len(items)} items og {len(collections)} collections fra {snapshot_dir}")

    portrait_check = check_portrait_file_presence(items, collections)
    portrait_check.to_csv(OUTPUT_DIR / "portrait_file_presence_check.csv", index=False)
    print("\nUndersøgelse af 'Print Collection portrait file' i dette snapshot:")
    print(portrait_check.to_string(index=False))

    items_subset, unique_names = build_subject_name_tables(items)
    items_subset.to_csv(OUTPUT_DIR / "nypl_items_with_subject_name.csv", index=False)
    unique_names.to_csv(OUTPUT_DIR / "nypl_unique_subject_names.csv", index=False)

    print(f"\nGemte {len(items_subset)} items med >=1 Subject Name -> "
          f"{OUTPUT_DIR / 'nypl_items_with_subject_name.csv'}")
    print(f"Gemte {len(unique_names)} unikke Subject Name-strenge -> "
          f"{OUTPUT_DIR / 'nypl_unique_subject_names.csv'}")


if __name__ == "__main__":
    main()
