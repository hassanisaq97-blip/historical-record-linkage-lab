# Detaljerede resultater

Se README for et kort resumé. Alle tal her er genereret af
`snakemake --snakefile workflow/Snakefile --cores 1` og kan reproduceres.

## Evaluering

**Syntetisk (testsplit, n = 11.804 par, 569 sande matches):**

| Metode | Precision | Recall | F1 | TP | FP | FN | TN |
|---|---:|---:|---:|---:|---:|---:|---:|
| Regelbaseret | 0,994 | 0,566 | 0,721 | 322 | 2 | 247 | 11.233 |
| ML (Random Forest) | 0,737 | 0,991 | 0,846 | 564 | 201 | 5 | 11.034 |

**NYC directories (test-split af det manuelle benchmark, n = 37 par):**

| Metode | Precision | Recall | F1 | TP | FP | FN | TN |
|---|---:|---:|---:|---:|---:|---:|---:|
| Regelbaseret | 0,833 | 0,833 | 0,833 | 5 | 1 | 1 | 30 |
| ML (Random Forest) | 0,750 | 1,000 | 0,857 | 6 | 2 | 0 | 29 |

NYC-tallene bygger på et lille, 92-par manuelt benchmark (14 positive, 78
negative, se `data/raw/nyc_directories/MANUAL_BENCHMARK.md`) og skal
læses som en indikation, ikke en præcis performance-måling.

**Feature importance (syntetisk ML-model):** fornavns-similaritet
dominerer klart; efternavns-similaritet bidrager næsten intet, fordi
blocking allerede sker på efternavns-soundex (se `docs/architecture.md`).

**Threshold-behaviour:** `results/reports/nyc_directories/threshold_behaviour.csv`
viser precision/recall ved klassifikationstærskler 0,3-0,8 på ML-modellen.

## Constrained assignment

**Syntetisk datasæt** (ML-metoden, alle splits):

| | Precision | Recall | F1 | Accepterede par |
|---|---:|---:|---:|---:|
| Før constraint | 0,470 | 0,996 | 0,639 | 4.113 |
| Efter constraint | 0,836 | 0,924 | 0,878 | 2.145 |

Konflikter (records med >1 accepteret link) går fra 2.315 til 0.

**NYC directories** (ML-metoden, hele korpus af 41.393 kandidatpar):
1.532 accepterede par, 608 records med konflikt før constraint, 775 par
tilbage efter (757 droppet), 0 konflikter tilbage.

## Livsforløb / entity resolution

**Syntetisk:**

| Metode | Livsforløb | Markeret | Andel |
|---|---:|---:|---:|
| Regelbaseret | 1.132 | 34 | 3,0 % |
| ML, uden constraint | 1.456 | 718 | 49,3 % |
| ML, med one-to-one constraint | 2.145 | 81 | 3,8 % |

Constraint fjerner **alle** multi_match-konflikter per konstruktion, men
retter ikke individuelt forkerte par - deraf det lille residuale antal
flag.

**NYC directories:**

| Metode | Entiteter | Markeret | Andel |
|---|---:|---:|---:|
| Regelbaseret | 234 | 42 | 17,9 % |
| ML, uden constraint | 572 | 189 | 33,0 % |
| ML, med one-to-one constraint | 775 | 73 | 9,4 % |

Samme mønster som på det syntetiske datasæt: constraint fjerner alle
`multi_match`-flag (151 → 0), men det resterende `conflicting_occupation`
(73 tilfælde, uændret af constraint) er par, der individuelt blev
accepteret forkert.

## Fejlanalyse: hvorfor false positives er særligt problematiske

Begge datasæt viser samme mønster: den mere permissive metode (ML) har
lavere precision end den regelbaserede metode. Det har en konkret
nedstrøms-konsekvens. Når pairwise-links aggregeres til
livsforløb/entiteter, bliver hver false positive-link en kant i en graf.
Hvis en post fejlagtigt linkes til to forskellige andre poster, opstår en
komponent med >2 knuder ("multi_match") - et livsforløb, der påstår at
forbinde poster, der reelt beskriver forskellige personer.

Dette er direkte målt: den syntetiske pipelines ML-metode (uden
constraint) har 49,3 % af sine livsforløb flagget, mod 3,0 % for den
regelbaserede metode - næsten udelukkende drevet af multi_match. En false
positive er altså ikke isoleret til én forkert prædiktion; den forplanter
sig til at gøre en hel rekonstrueret entitets struktur upålidelig.

## Opsummering

- Regelbaseret linkage er konsekvent mere præcis, men fanger færre sande
  matches, på begge datasæt.
- One-to-one constrained assignment giver en stor, målt precision/F1-
  gevinst på begge datasæt, uden at kunne øge recall (matematisk umuligt
  for en post-hoc filtrering).
- Et manuelt 92-par benchmark for NYC directories viser, at ægte
  dubletter er **sjældne** i én enkelt directory-årgang: en ren
  tilfældig stikprøve på 80 kandidatpar gav kun ét klart positivt
  eksempel, så benchmarket måtte suppleres med en målrettet søgning efter
  stærk tværfelts-evidens for overhovedet at indeholde begge klasser.
