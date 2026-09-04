# historical-record-linkage-lab

Et selvstændigt data science-eksperiment i historisk record linkage:
standardisering, blocking, regelbaseret og ML-baseret kobling af to
syntetiske historiske kilder, benchmark-evaluering med precision/recall/F1,
rekonstruktion af livsforløb og systematiske sanity checks.

**Dette er ikke et Rigsarkivet- eller HisPeR-projekt.** Det bruger ingen
ægte historiske data, ingen data fra Rigsarkivet, og det hverken
repræsenterer eller hævder professionel erfaring med record linkage i
produktionsskala, Snakemake på HPC, eller graph neural networks. Se
[docs/limitations.md](docs/limitations.md) for en fuld liste over bevidste
afgrænsninger.

## Motivation

Projektet er lavet for at demonstrere, at kompetencer inden for Python,
datarensning, feature engineering, ML-evaluering og reproducerbare
workflows - opbygget bl.a. gennem arbejde med longitudinelle danske
registerdata og kliniske data - kan overføres til problemstillinger inden
for historisk record linkage: kobling af heterogene, støjfyldte kilder,
konstruktion af forløb over tid, og systematisk evaluering af
metodekvalitet frem for blot at "få et resultat".

Det metodiske udgangspunkt er inspireret af en offentligt beskrevet
udfordring: at store, longitudinelle koblinger af historiske kilder over
tid afslører problemer som ujævn linkage-kvalitet, modstridende links,
usandsynlige livsforløb og metoder udviklet på forskellige tidspunkter -
og at det derfor kræver systematisk evaluering, dokumentation og løbende
forbedring eller udskiftning af metoder. Dette projekt er en lille,
selvstændig demonstration af netop den arbejdsform, på egne syntetiske
data og uden tilknytning til det faktiske arbejde, denne udfordring stammer
fra.

## Data

Alle data er syntetisk og genereret af `linkage_lab/data_generation.py`
med en fast seed (reproducerbart, se `linkage_lab/config.py`):

- En skjult "grundsandhed"-population på 4.000 individer (navn, køn,
  fødselsår, fødested).
- **Census** (75 % dækning, ~3.000 poster, år 1850): fornavn, efternavn,
  alder, fødested, bopæl, erhverv.
- **Kirkebog** (75 % dækning, ~3.000 poster): fornavn, efternavn,
  fødselsår, fødested, sogn, hændelsestype.

Hver kilde er støjet uafhængigt (`linkage_lab/noise_model.py`):
stavevarianter og enkelttegns-transskriptionsfejl i navne, stednavne fra en
lille varianttabel, alders-/fødselsårsunøjagtighed, manglende felter, og en
lille sandsynlighed for en stor "brøler" (5-20 års fejl), som giver
sanity-check-logikken noget reelt at fange. Ingen af de to kilder dækker
hele populationen, og de overlapper kun delvist - ligesom to uafhængige
historiske kilder ville gøre.

## Metode

1. **Standardisering** (`standardization.py`): store/små bogstaver,
   diakritiske tegn (æøå), og et lille gazetteer for stednavne. Efternavne
   kanoniseres bevidst *ikke* mod en facitliste - se
   [docs/limitations.md](docs/limitations.md).
2. **Blocking** (`blocking.py`): kandidatpar genereres kun inden for samme
   Soundex-kode for efternavn og fødselsår ± 1 bucket (5-års buckets).
3. **Features** (`features.py`): Jaro-Winkler-similaritet og exact match på
   fornavn/efternavn, absolut fødselsårsdifference, og fødestedsmatch (med
   eksplicit "begge observeret"-flag, så manglende data ikke tæller som
   uoverensstemmelse).
4. **Benchmark og entity-level split** (`benchmark.py`): kandidatpar
   labelles ud fra den skjulte grundsandhed. Train/test-split sker på
   **individ-niveau** (70/30): et individs poster ligger enten udelukkende
   i træning eller udelukkende i test. Par, hvor de to poster hører til
   individer fra hver sin side af splittet, udelades helt - for at undgå
   data leakage mellem træning og evaluering.
5. **Regelbaseret linkage** (`linkage_rule_based.py`): faste
   similaritets-tærskler, ingen træning.
6. **ML-linkage** (`linkage_ml.py`): Random Forest trænet udelukkende på
   træningssplittet.
7. **Evaluering** (`evaluation.py`): precision/recall/F1 på testsplittet,
   samt konkrete false positive/false negative-eksempler.
8. **Livsforløb og sanity checks** (`life_course.py`): accepterede par
   aggregeres til en graf; sammenhængende komponenter er "livsforløb".
   Checks: (a) mere end én post fra samme kilde i ét livsforløb
   ("multi_match" - mangel på en one-to-one-begrænsning), (b)
   modstridende fødselsårsestimater (>3 år), (c) fødselsår uden for
   plausibelt interval.
9. **LLM-assisteret linkage** (`linkage_llm.py`) - eksperimentelt tillæg,
   ikke en hovedmetode. Se afsnittet nedenfor.

## Resultater

Genereret af `snakemake --snakefile workflow/Snakefile --cores 1` med
standard-seed (42). Alle tal kan reproduceres, se "Reproducér" nedenfor.

**Blocking recall:** 1.941 af 2.253 faktisk overlappende individer (86,2 %)
har mindst ét kandidatpar efter blocking - se
[results/reports/blocking_recall.md](results/reports/blocking_recall.md).
Dette er et hårdt loft over den samlede recall, uanset linkage-metode.

**Linkage-metoder (testsplit, n = 11.804 par, heraf 569 sande matches):**

| Metode              | Precision | Recall | F1     | TP  | FP  | FN  | TN     |
|---------------------|----------:|-------:|-------:|----:|----:|----:|-------:|
| Regelbaseret        | 0,994     | 0,566  | 0,721  | 322 | 2   | 247 | 11.233 |
| ML (Random Forest)  | 0,737     | 0,991  | 0,846  | 564 | 201 | 5   | 11.034 |

Se figur: [results/figures/method_comparison.png](results/figures/method_comparison.png)

Den regelbaserede metode er meget konservativ (næsten ingen false
positives, men misser over 40 % af de sande matches ved kraftig støj).
ML-modellen fanger næsten alle sande matches, men til prisen af markant
flere false positives. Det er en reel afvejning, ikke en fejl i den ene
metode - se `results/reports/error_examples_rule_based.md` og
`error_examples_ml.md` for konkrete eksempler (bl.a. forskellige personer
med samme almindelige efternavn og lignende alder, som fejlagtigt kobles
af ML-modellen).

**Feature importance (ML-model):** fornavns-similaritet dominerer klart
([results/figures/feature_importance.png](results/figures/feature_importance.png)).
Efternavns-similaritet bidrager næsten intet - fordi blocking allerede sker
på efternavns-soundex, er variationen i det felt i forvejen begrænset blandt
kandidatparrene. Se diskussion i [docs/limitations.md](docs/limitations.md).

**Livsforløb og sanity checks:**

| Metode              | Livsforløb | Markeret | Andel  |
|---------------------|-----------:|---------:|-------:|
| Regelbaseret        | 1.132      | 34       | 3,0 %  |
| ML (Random Forest)  | 1.456      | 718      | 49,3 % |

Den markant højere andel markerede livsforløb for ML-metoden er en direkte
konsekvens af dens lavere precision: flere false positive-links skaber
komponenter, hvor én post transitivt kobles til flere poster fra den anden
kilde. Se [results/reports/life_course_sanity_checks.md](results/reports/life_course_sanity_checks.md).

## LLM-assisteret linkage (eksperimentelt, ikke kørt her)

`linkage_lab/linkage_llm.py` lader en LLM vurdere de 685 kandidatpar, hvor
ML-modellens `predicted_proba` ligger i en gråzone (0,35-0,65). Modulet
kræver brugerens egen `ANTHROPIC_API_KEY` og indgår **ikke** i
ovenstående tal eller i standard-pipelinen. Kør det selv med:

```bash
export ANTHROPIC_API_KEY=...
snakemake --snakefile workflow/Snakefile --cores 1 llm_supplement
```

Uden en API-nøgle skriver kommandoen i stedet en placeholder-rapport, så
det er tydeligt, at trinnet bevidst er sprunget over. Se
[docs/limitations.md](docs/limitations.md).

## Reproducér

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"

# Kør hele pipelinen (genererer data/, results/reports/, results/figures/):
snakemake --snakefile workflow/Snakefile --cores 1

# Kør tests:
pytest tests/ -v
```

Alle trin kan også køres enkeltvis via `python -m linkage_lab.cli <trin>`
(`generate-data`, `standardize`, `build-dataset`, `link-rule-based`,
`link-ml`, `evaluate`, `life-course`).

## Repostruktur

```
src/linkage_lab/       Python-pakke (al kode, engelske navne)
  data_generation.py     Syntetisk datagenerering
  reference_data.py      Navne-/stednavnepools og varianttabeller
  noise_model.py          Transskriptionsstøj
  standardization.py      Normalisering + stednavnegazetteer
  blocking.py              Soundex + fødselsårs-blocking
  features.py              Pairwise similaritetsfeatures
  benchmark.py             Labelling + entity-level train/test-split
  linkage_rule_based.py    Regelbaseret baseline
  linkage_ml.py            Random Forest-klassifikator
  evaluation.py            Metrics + fejl-eksempler
  life_course.py           Grafaggregering + sanity checks
  linkage_llm.py           Eksperimentelt LLM-supplement
  visualize.py             Statiske figurer
  cli.py                   Kommandolinje-indgange pr. pipeline-trin
workflow/Snakefile      Reproducerbar pipeline (lokal, ikke HPC)
tests/                  pytest-tests af al kernelogik
docs/limitations.md     Metodiske begrænsninger (dansk)
results/                Committede rapporter og figurer fra seneste kørsel
data/                   Genereres af pipelinen (ikke committed, se .gitignore)
```
