# Metodiske begrænsninger

Dette dokument beskriver bevidste afgrænsninger i projektet - hvad det ikke
forsøger at gøre, og hvorfor.

## Data

- Alle data i dette repository er **syntetisk genereret** (se
  `linkage_lab/data_generation.py` og `linkage_lab/reference_data.py`). Der
  indgår ingen ægte historiske kilder, ingen data fra Rigsarkivet, og ingen
  persondata af nogen art. Navne, stednavne og stavevarianter er selv
  opdigtet til formålet (delvist inspireret af almindelige danske
  patronymer og stednavne) og skal ikke læses som en model af faktiske
  danske historiske kilder.
- Skalaen (4.000 syntetiske individer, ca. 3.000 poster pr. kilde) er
  bevidst lille. Den siger intet om, hvordan metoderne ville performe på
  titusinder eller millioner af poster, og slet ikke noget om egnetheden
  til HisPeR's ca. 100 millioner poster.
- Støjmodellen (`linkage_lab/noise_model.py`) er en grov forenkling af
  virkelige transskriptionsfejl (håndskrift, OCR/HTR, forkortelser,
  daterings-usikkerhed). Den er designet til at producere realistisk
  *retning* af fejl (stavevarianter, aldersunøjagtighed, manglende felter),
  ikke til at gengive faktiske fejlrater fra historiske kilder.

## Standardisering

Stednavne standardiseres via en lille kendt synonymtabel
(`reference_data.PLACE_VARIANTS`), mens efternavne bevidst **ikke**
kanoniseres via en tilsvarende opslagstabel. Det er et bevidst designvalg:
et geografisk synonymkatalog er realistisk (og nævnes eksplicit i HisPeR's
egen beskrivelse af Link-Lives), mens en færdig facitliste over
navnevarianter ville underminere selve pointen med similarity-baseret og
ML-baseret linkage. Konsekvensen ses direkte i feature-importance-figuren:
fordi blocking allerede sker på efternavns-soundex, bærer `surname_jw` kun
lidt yderligere information for klassifikatoren - en ægte, forventelig
effekt af at bruge samme felt til både blocking og features.

## Blocking sætter et loft over recall

122.766 kandidatpar genereres fra ca. 3.000 × 3.000 mulige par. Men
blocking er ikke gratis: kun 86,2 % af de faktisk overlappende individer
har overhovedet et kandidatpar efter blocking (se
`results/reports/blocking_recall.md`). De resterende ~14 % kan aldrig
genfindes af nogen linkage-metode, uanset hvor god den er. Dette er en
reel og ofte overset begrænsning i record linkage-systemer, ikke en fejl i
selve blocking-implementeringen.

## Ingen one-to-one-begrænsning på links

Linkage-metoderne (regel-baseret og ML) klassificerer hvert kandidatpar
uafhængigt. Der er ingen efterfølgende one-to-one-tildeling (fx Ungarsk
algoritme eller grådig tildeling efter højeste score), som ville sikre, at
hver census-post højst matches til én kirkebogs-post og omvendt. Det er
årsagen til, at livsforløbs-grafen indeholder komponenter med mere end to
knuder ("multi_match"), særligt for ML-metoden (49,3 % af de rekonstruerede
livsforløb markeret, mod 3,0 % for den regelbaserede metode - se
`results/reports/life_course_sanity_checks.md`). En reel produktionsversion
ville tilføje en one-to-one-tildeling før livsforløbs-konstruktion. Det er
udeladt her for at holde projektet fokuseret på selve
linkage/evaluerings-spørgsmålet.

## Ikke inkluderet (bevidst fravalgt)

- **Graph neural networks** og andre graf-læringsmetoder. Nævnt som
  fremtidig retning i HisPeR's arbejdsplan, men et forsøg på at
  implementere det på to dages syntetisk data ville være overfladisk.
- **Fuld familie-/husstandsrekonstruktion.** Kun parvis kobling og en
  meget enkel graf-aggregering til livsforløb er inkluderet.
- **Skalering til HPC/Computerome.** Snakemake-workflowet kører lokalt på
  den lille syntetiske datamængde. Det er ikke testet eller designet til
  at køre på rigtig HPC-infrastruktur.
- **Frontend/dashboard.** Resultater leveres som CSV/Markdown-rapporter og
  statiske figurer, ikke en interaktiv applikation.
- **Professionel erfaring med historical record linkage, Snakemake, HPC
  eller GNN.** Dette projekt demonstrerer, at eksisterende kompetencer
  inden for Python, datarensning, ML-evaluering og reproducerbare
  workflows kan overføres til dette problemfelt - det er ikke en påstand
  om forudgående erfaring med disse specifikke teknologier eller domænet.

## LLM-assisteret linkage er eksperimentel og ikke kørt

`linkage_lab/linkage_llm.py` implementerer et snævert afgrænset supplement:
en LLM bruges kun til at vurdere de kandidatpar, hvor ML-modellens
`predicted_proba` ligger i en "gråzone" (0,35-0,65) - i denne kørsel 685
par. Modulet kræver brugerens egen `ANTHROPIC_API_KEY` og er bevidst
**ikke** en del af hovedpipelinen (`workflow/Snakefile`'s `all`-regel) eller
af de rapporterede precision/recall/F1-tal. Uden en API-nøgle skriver
kommandoen en tydelig placeholder-rapport i stedet for at fejle uforklaret
eller foregive et resultat. De deterministiske dele af modulet (valg af
gråzone-par, prompt-opbygning, parsing af svar) er dækket af tests i
`tests/test_linkage_llm.py` uden at kræve netværksadgang.
