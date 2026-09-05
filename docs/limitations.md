# Metodiske begrænsninger

Dette dokument beskriver bevidste afgrænsninger i projektet - hvad det
ikke forsøger at gøre, og hvorfor - for begge datasæt: det syntetiske
benchmark og NYC city directory-casen. Se også
[docs/dataset_selection_notes.md](dataset_selection_notes.md) for
processen bag valget af real-world datasæt.

## 1. Synthetic-to-real gap

Det syntetiske datasæt (4.000 individer, kontrolleret støjmodel) er
bevidst lille og forenklet. Det siger intet om, hvordan metoderne ville
performe på titusinder eller millioner af poster, og intet om egnetheden
til en produktionsskala på ca. 100 millioner poster. Støjmodellen
(`linkage_lab/noise_model.py`) er designet til at producere realistisk
*retning* af fejl (stavevarianter, aldersunøjagtighed, manglende felter),
ikke til at gengive faktiske fejlrater fra virkelige historiske kilder.

NYC directory-casen lukker en del af dette gap ved at bruge ægte OCR'et
tekst med ægte fejl - men kun i lille skala (8.000 af 87.674 tilgængelige
linjer, én årgang) og kun for én kildetype. De to datasæt supplerer
hinanden metodisk (kontrolleret vs. ægte), men ingen af dem beviser noget
om skalerbarhed til produktionsstørrelse.

## 2. Manglende/ufuldstændig ground truth

- **Syntetisk:** ground truth er fuldstændig og korrekt per konstruktion
  (vi genererede selv `person_id`), men det er netop derfor en model af
  virkeligheden, ikke virkeligheden selv.
- **NYC directories:** der findes intet pålideligt felt for "samme
  person" i city directory-data. Se
  `data/raw/nyc_directories/MANUAL_BENCHMARK.md` for den fulde
  metodebeskrivelse. Kort: 92 kandidatpar blev manuelt vurderet af
  projektets forfatter (ikke en uafhængig ekspert, ikke krydstjekket mod
  andre kilder), og stikprøven blev bevidst beriget med
  stærk-evidens-par, fordi en ren tilfældig stikprøve på 80 par kun gav
  ét klart positivt eksempel. De rapporterede NYC-metrics (se
  `docs/results.md`) er derfor indikative, ikke en præcis performance-måling, og
  benchmarkets 15,2 % positive andel afspejler **ikke** den sande
  dublet-rate i datasættet.

## 3. OCR-fejl

NYC directory-teksten indeholder ægte OCR/typesetting-fejl, kvantificeret
i `results/reports/nyc_directories/data_quality_report.md`: bl.a. 6,2 %
af fornavnene har et formodet "delt bogstav"-artefakt ("J ames" for
"James"), og digit-for-letter-fejl forekommer i erhvervsfelter (fx
"p1umber" for "plumber"). Vi retter kun det første, veldokumenterede
mønster eksplicit (`fix_split_first_letter`) - vi bygger ikke en generel
OCR-fejlkorrektor, da det ville være et selvstændigt (og stort) projekt i
sig selv, og linkage-metoderne (similarity-baserede features) er netop
designet til at være robuste over for resterende støj i stedet.

## 4. Kildebias

NYC directory-uddraget dækker kun de første 8.000 linjer (alfabetisk
efter efternavn, startende omkring "Bu-") af én enkelt årgang af én
udgiver (Doggett's). Det er ikke en repræsentativ stikprøve af hele byens
befolkning i 1851/52 - visse efternavne, og dermed visse
befolkningsgrupper, er over- eller underrepræsenteret afhængigt af det
alfabetiske udsnit. Erhvervsfordelingen (dominans af håndværks- og
arbejdererhverv) afspejler også, hvem der overhovedet blev optaget i en
datidens city directory.

## 5. Blocking-fejl

- **Syntetisk:** kun 86,2 % af de faktisk overlappende individer har
  overhovedet et kandidatpar efter blocking (se
  `results/reports/blocking_recall.md`, målt direkte mod den kendte
  ground truth). De resterende ~14 % kan aldrig genfindes, uanset hvor
  god linkage-metoden er.
- **NYC directories:** ægte blocking recall kan ikke måles direkte (det
  manuelle benchmark er udtrukket fra kandidatparrene selv, hvilket ville
  gøre recall tautologisk 100 %). En billig proxy - records med samme
  fornavn+erhverv+adresse men uenig efternavns-Soundex - finder 3 sådanne
  grupper i udsnittet (se `data_quality_report.md`), hvilket antyder, at
  blocking-baserede false negatives forekommer, men ikke kan kvantificere
  omfanget præcist.

## 6. Threshold-følsomhed

Klassifikationstærsklen for "match" (standard: 0,5 sandsynlighed for
ML-metoderne) er en direkte precision/recall-afvejning, ikke en naturlig
grænse. `results/reports/nyc_directories/threshold_behaviour.csv` viser
precision/recall ved tærskler fra 0,3 til 0,8. En produktionsversion ville
sandsynligvis vælge tærsklen ud fra den relative omkostning ved false
positives vs. false negatives i den konkrete anvendelse (fx er en falsk
sammenkobling i et livsforløb dyrere at opdage bagefter end en manglende
kobling) - dette projekt bruger 0,5 konsekvent for sammenlignelighed på
tværs af metoder, ikke fordi det er bevist optimalt.

## 7. False-positive-forplantning

Se docs/results.md ("Fejlanalyse") for den fulde diskussion: en forkert
pairwise-kobling bliver til en strukturel fejl (multi_match) når den
aggregeres til et livsforløb/en entitet. Dette er empirisk bekræftet på
begge datasæt: den mere permissive ML-metode har markant flere flaggede
livsforløb/entiteter end den mere konservative regelbaserede metode,
primært drevet af multi_match - ikke af de andre sanity-check-typer.

## 8. Begrænsninger ved pairwise linkage og one-to-one-constraint

Uafhængig par-klassifikation kan acceptere flere links til samme record.
Dette er nu afhjulpet med generisk one-to-one constrained assignment
(`constrained_assignment.py`, se docs/architecture.md) - men constraint har
selv en begrænsning: den kan kun **fjerne** par, aldrig tilføje eller
korrigere dem. Et par, der individuelt er forkert klassificeret men ikke
konkurrerer med et bedre alternativ om samme record, overlever constraint
uændret (jf. de resterende `conflicting_occupation`-flag efter constraint
i NYC-resultaterne - uændret 73 tilfælde før og efter). Constraint retter
altså strukturelle konflikter, ikke indholdsmæssige fejl.

Derudover antager one-to-one-constrainten, at hver record kun kan tilhøre
én virkelig person - en rimelig antagelse for census/kirkebog og for et
enkelt directory-opslag, men ikke universelt sand for alle historiske
kildetyper (fx kan en husstandsliste med flere navne på én linje bryde
denne antagelse).

## 9. Usikkerhed i rekonstruerede livsforløb/entiteter

Ingen output fra dette projekt bør læses som en sikker identitetspåstand.
Både `life_course.py` og `entity_resolution.py` er eksplicitte om dette:
et "livsforløb"/en "entitet" er en sammenhængende komponent i en graf af
**probabilistiske** links, annoteret med en konfidence-score
(`mean_link_confidence`), aldrig en garanteret identitet. Sanity checks
fanger nogle, men ikke alle, former for fejl - fx fanger de ikke en
selvkonsistent, men faktuelt forkert kobling (to forskellige personer med
identisk navn, erhverv OG adresse ville ikke blive flagget).

## 10. LLM-begrænsninger

`llm_assist.py`/`linkage_llm.py` er et eksperimentelt supplement, der
**ikke kunne køres i dette udviklingsmiljø**: `ollama.com` og
`registry.ollama.ai` er blokeret af netværkspolitikken her (verificeret
empirisk ved direkte forbindelsesforsøg), så hverken Ollama eller en
model kunne installeres. Ingen LLM-resultater er derfor rapporteret eller
opfundet - se `results/reports/llm_experimental_supplement.md` for den
faktiske (tomme) status og docs/architecture.md for en fuld, ærlig diskussion
af metodens generelle begrænsninger (non-determinisme, hallucination,
reproducerbarhed, latency, kalibrering, privacy, beregningsomkostning).

## 11. Ikke inkluderet (bevidst fravalgt)

- **Graph neural networks** og andre graf-læringsmetoder. Nævnt som
  fremtidig retning i det oprindelige brief, der inspirerede projektet,
  men et forsøg på at implementere det på dette projekts datamængder
  ville være overfladisk snarere end en reel demonstration.
- **Fuld familie-/husstandsrekonstruktion.** Ingen af datasættene
  indeholder pålidelige familierelationsfelter; at opfinde dem ville
  modsige kravet om ikke at opfinde ground truth.
- **Skalering til HPC.** Snakemake-workflowet kører lokalt på begge
  datasæts beskedne størrelse. Det er ikke testet eller designet til at
  køre på egentlig HPC-infrastruktur.
- **Frontend/dashboard.** Resultater leveres som CSV/Markdown-rapporter
  og statiske figurer, ikke en interaktiv applikation.
- **Flere directory-årgange.** Se `docs/architecture.md` og
  `docs/dataset_selection_notes.md` - kun én årgang er tilgængelig uden
  API-nøgle fra et miljø med denne netværksbegrænsning.
- **Professionel erfaring med historical record linkage, HPC, GNN eller
  produktionsdrift af Ollama/LLM'er.** Dette projekt demonstrerer, at
  eksisterende kompetencer inden for Python, datarensning, ML-evaluering
  og reproducerbare workflows kan overføres til dette problemfelt - det
  er ikke en påstand om forudgående professionel erfaring med disse
  specifikke teknologier eller domænet.
