# Historical Record Linkage Lab

Et selvstændigt portfolio-projekt i historisk record linkage: at afgøre,
hvornår to poster fra støjfyldte, transskriberede kilder beskriver samme
person - uden et CPR-nummer at slå op på, og med almindelige navne, der
kolliderer på tværs af forskellige, urelaterede individer. Projektet
bygger hele pipelinen fra rå data til kvalitetssikrede koblinger, på
både et kontrolleret syntetisk datasæt og et ægte historisk OCR-datasæt.

**Dette er et selvstændigt lærings-/portfolio-projekt.** Det er **ikke**
udviklet af eller for Rigsarkivet, og bruger **ingen** HisPeR-data.

## Pipeline

```
Historiske data → Standardisering → Blocking → Similarity features
→ Record linkage → One-to-one matching → Kvalitetskontrol
```

- **Standardisering** – renser navne/erhverv/adresser uden at fjerne information, der er nyttig til kobling.
- **Blocking** – reducerer kandidatpar med over 99 %, så vi ikke sammenligner alle poster med alle.
- **Similarity features** – Jaro-Winkler-similaritet på navn, erhverv, adresse, fødselsår m.m.
- **Record linkage** – regelbaseret og ML-klassifikation af kandidatpar.
- **One-to-one matching** – sikrer at én post kun kan matche én anden post.
- **Kvalitetskontrol** – sanity checks der flager modstridende eller usandsynlige koblinger.

Se [docs/architecture.md](docs/architecture.md) for den fulde metodik.

## Data

- **Syntetisk benchmark:** genereret census + kirkebogsdata (4.000 individer) med kontrolleret støj og kendt facit.
- **Real-world case study:** 8.000 OCR-baserede records fra NYPL's Doggett's New York City Directory, 1851/52 (hentet fra NYPL's officielle GitHub, MIT-licens).

NYC-datasættet bruges som real-world case study **uden komplet ground
truth** - der findes intet facit-felt for "samme person" i kildedata, så
evalueringen bygger på et lille, manuelt vurderet benchmark (92 par). Se
[docs/dataset_selection_notes.md](docs/dataset_selection_notes.md).

## Metoder

- Rule-based linkage (faste similaritets-tærskler)
- Random Forest-klassifikation
- One-to-one constrained graph matching (`networkx.max_weight_matching`)
- Eksperimentel LLM-assistance via Ollama/Llama 3.2 - **implementeret, men ikke kørt** i dette miljø (Ollama er utilgængeligt her, se begrænsninger)

## Resultater

Syntetisk benchmark, testsplit:

| Metode | F1 |
|---|---:|
| Rule-based | 0,721 |
| Random Forest | 0,846 |
| Random Forest + constrained assignment | 0,878 |

One-to-one constrained assignment løfter precision fra **0,470 til
0,836** blandt de accepterede par, og eliminerer samtlige 2.315
tilfælde, hvor samme post var koblet til mere end ét match. Uafhængig
klassifikation kan acceptere modstridende links; constraint tvinger hver
post til højst ét match, valgt efter højeste model-score. Det kan kun
fjerne par, ikke tilføje nye, så recall falder let mens precision stiger
markant.

NYC-directory-metoderne følger samme mønster (rule-based F1 0,833 vs. ML
0,857), men benchmarket består af kun **37 testpar** og skal derfor ikke
overfortolkes. Fulde tal og fejlanalyse: [docs/results.md](docs/results.md).

## Teknologi

Python · pandas · scikit-learn · NetworkX · Snakemake · pytest · Ollama/Llama 3.2

## Kør projektet

```bash
pip install -e ".[dev]"
snakemake --snakefile workflow/Snakefile --cores 1
pytest tests/ -v
```

## Begrænsninger

- Synthetic-to-real gap: det syntetiske benchmark er kontrolleret og forenklet.
- Begrænset ground truth på NYC-data: kun et lille, manuelt benchmark.
- Kun én NYC-årgang tilgængelig (netværksadgang til NYPL/Internet Archive er blokeret i dette miljø).
- LLM-eksperimentet er ikke kørt her (Ollama utilgængeligt).

Fuld gennemgang: [docs/limitations.md](docs/limitations.md).

## Projektstruktur

```
src/linkage_lab/            Syntetisk benchmark-pipeline
src/linkage_lab/nyc_directories/  Real-world case study
workflow/Snakefile          Reproducerbar pipeline (begge datasæt)
tests/                      pytest-tests
results/                    Committede rapporter og figurer
data/raw/nyc_directories/   Vendored kildedata + manuelt benchmark
docs/                       Uddybende metodik, resultater og begrænsninger
```
