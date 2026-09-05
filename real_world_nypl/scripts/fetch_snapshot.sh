#!/usr/bin/env bash
# Henter NYPL's officielle public-domain metadata-snapshot (item- og
# collection-niveau, CSV + NDJSON). Ingen API-nøgle kræves.
#
# Kilde: https://github.com/NYPL-publicdomain/data-and-utilities
# Snapshot er frosset 2015-12-30 (se repoets README.md) - det er IKKE en
# live eksport af NYPL Digital Collections.
#
# Filerne er store (~600 MB tilsammen) og hentes derfor uden for git -
# de committes ikke til dette repository. Kun de udtræk, som
# build_subject_name_subset.py producerer, committes (se data/).
#
# Brug:
#   bash real_world_nypl/scripts/fetch_snapshot.sh /tmp/nypl_pd

set -euo pipefail

TARGET_DIR="${1:-/tmp/nypl_pd}"

if [ -d "$TARGET_DIR/.git" ]; then
    echo "Snapshot findes allerede i $TARGET_DIR - springer over."
else
    git clone --depth 1 https://github.com/NYPL-publicdomain/data-and-utilities.git "$TARGET_DIR"
fi

echo "Snapshot hentet til: $TARGET_DIR"
echo "Items:       $TARGET_DIR/items/pd_items_1.csv, pd_items_2.csv"
echo "Collections: $TARGET_DIR/collections/pd_collections.csv"
