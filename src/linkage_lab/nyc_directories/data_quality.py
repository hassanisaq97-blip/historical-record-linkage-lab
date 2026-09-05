"""Quantifies data quality in the parsed/standardised NYC-directory subset
and writes a Danish Markdown report. Every number here is computed from
the committed pipeline, not asserted from memory.
"""

from __future__ import annotations

import re

import pandas as pd

from .. import config

_SPLIT_LETTER_RE = re.compile(r"^[A-Za-z] [a-z]{2,}$")


def compute_report(parsed: pd.DataFrame, standardized: pd.DataFrame) -> str:
    lines = ["# Datakvalitet: NYC city directory 1851/52 (udsnit)\n"]
    lines.append(f"Antal records i udsnittet: **{len(parsed)}**\n")

    lines.append("## Parsing-succes\n")
    lines.append(f"- `parse_ok` (efternavn + mindst erhverv eller adresse fundet): "
                 f"{parsed['parse_ok'].sum()} ({parsed['parse_ok'].mean():.1%})\n")
    lines.append(f"- Flagget som sandsynligt kolonne-sammenblandings-artefakt "
                 f"(`likely_multi_entry`): {parsed['likely_multi_entry'].sum()} "
                 f"({parsed['likely_multi_entry'].mean():.1%})\n")

    lines.append("## Manglende værdier\n")
    for col in ["surname", "given_name", "occupation", "address_business", "address_home"]:
        n_missing = parsed[col].isna().sum()
        lines.append(f"- {col}: {n_missing} mangler ({n_missing / len(parsed):.1%})")
    lines.append("")

    lines.append("## Navnevariation og OCR-fejl\n")
    given = parsed["given_name"].dropna().astype(str)
    split_artifact = given.str.match(_SPLIT_LETTER_RE)
    lines.append(
        f"- Fornavne med formodet OCR-artefakt (\"J ames\" i stedet for \"James\"): "
        f"{split_artifact.sum()} ({split_artifact.mean():.1%} af ikke-manglende fornavne), "
        f"rettet af `standardization.fix_split_first_letter`.\n"
    )

    dup_counts = standardized.groupby(["surname_std", "given_name_std"]).size()
    n_dup_combos = int((dup_counts > 1).sum())
    lines.append(
        f"- Eksakte (efternavn, fornavn)-kombinationer, der optræder mere end én gang: "
        f"{n_dup_combos} ud af {standardized.groupby(['surname_std','given_name_std']).ngroups} "
        f"unikke kombinationer. Det højeste antal gentagelser af samme "
        f"(efternavn, fornavn) er {int(dup_counts.max())} "
        f"({dup_counts.idxmax()}).\n"
    )
    lines.append(
        "Dette er ikke nødvendigvis dubletter - almindelige for- og efternavne i "
        "1850'ernes New York (fx \"John\", \"Cook\") gentages i sagens natur på tværs "
        "af forskellige, ikke-relaterede personer. Se `data/raw/nyc_directories/MANUAL_BENCHMARK.md`.\n"
    )

    lines.append("## Erhvervsvariation\n")
    n_unique_occ_raw = parsed["occupation"].nunique()
    n_unique_occ_canonical = standardized["occupation_canonical"].nunique()
    lines.append(f"- Unikke rå erhvervsstrenge: {n_unique_occ_raw}")
    lines.append(f"- Unikke kanoniserede erhverv (efter opslag i IPUMS-ordliste): {n_unique_occ_canonical}")
    n_canonicalized = int((standardized["occupation_std"] != standardized["occupation_canonical"]).sum())
    lines.append(f"- Records hvor kanonisering ændrede den observerede streng: {n_canonicalized} "
                 f"({n_canonicalized / len(standardized):.1%})\n")

    lines.append("## Adressevariation\n")
    lines.append(f"- Records med business-adresse: {parsed['address_business'].notna().sum()} "
                 f"({parsed['address_business'].notna().mean():.1%})")
    lines.append(f"- Records med separat hjemme-adresse ('h.'/'r.'): {parsed['address_home'].notna().sum()} "
                 f"({parsed['address_home'].notna().mean():.1%})\n")

    lines.append("## Blocking false-negative-risiko (proxy, ikke fuld recall)\n")
    lines.append(
        "Ægte blocking recall kræver et fuldstændigt facit for alle mulige par, som vi "
        "ikke har (se docs/limitations.md). Som en billig proxy tælles records, der deler "
        "fornavn, erhverv OG adresse (stærk indikation af samme underliggende linje/person), "
        "men som blocking IKKE ville sætte i samme kandidat-blok pga. forskellig "
        "Soundex-kode for efternavnet (fx pga. en OCR-fejl i efternavnet):\n"
    )
    same_evidence = standardized.dropna(subset=["given_name_std", "occupation_canonical", "address_business_std"])
    grouped = same_evidence.groupby(["given_name_std", "occupation_canonical", "address_business_std"])
    missed = 0
    for _, group in grouped:
        if len(group) > 1 and group["surname_soundex"].nunique() > 1:
            missed += 1
    lines.append(f"- Grupper med samme fornavn+erhverv+adresse, men uenige om efternavns-Soundex: {missed}\n")

    return "\n".join(lines)


if __name__ == "__main__":
    parsed = pd.read_csv(config.NYC_DIR_PROCESSED_DIR / "parsed_entries.csv")
    standardized = pd.read_csv(config.NYC_DIR_PROCESSED_DIR / "blocked_entries.csv")
    report = compute_report(parsed, standardized)
    out_path = config.NYC_DIR_RESULTS_REPORTS_DIR / "data_quality_report.md"
    out_path.write_text(report, encoding="utf-8")
    print(f"Wrote {out_path}")
