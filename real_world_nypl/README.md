# NYPL real-world eksperiment — undersøgelsesfase

**Status: kun dataundersøgelse. Intet er (endnu) integreret i linkage-modellerne
i `src/linkage_lab`, og den syntetiske benchmark-pipeline er urørt.**

Dette dokument besvarer punkt for punkt, om NYPL Digital Collections' public
domain-metadata er egnet til det planlagte "real-world"-supplement til
projektets syntetiske record-linkage-eksperiment.

## 1-2. Snapshot hentet, og "Print Collection portrait file" lokaliseret

Det officielle bulk-snapshot er hentet fra
[`NYPL-publicdomain/data-and-utilities`](https://github.com/NYPL-publicdomain/data-and-utilities)
(se `scripts/fetch_snapshot.sh`) — ingen API-nøgle, ingen scraping.
Snapshottet er **frosset 2015-12-30** og indeholder **190.494 items** og
**932 collections**.

**Vigtig, uventet opdagelse:** Vores oprindelige antagelse — at "Print
Collection portrait file" (beskrevet på den levende hjemmeside som ~71.500
billeder) ville give et stort, brugbart datasæt — holder **ikke** i dette
snapshot. Se `data/portrait_file_presence_check.csv`:

| Match-metode | Antal items |
|---|---:|
| Collection Title = "Print Collection portrait file" | **10** |
| Collection Title = "Portrait collection" | **6** |
| "Collection Title" indeholder "portrait" (alle poster) | 71 |
| "Parent Hierarchy" indeholder "portrait" | 265 |
| "Genre" indeholder "portrait" | 407 |
| "Title" indeholder "portrait" | 567 |

Den mest sandsynlige forklaring: Portrait File er i vid udstrækning
digitaliseret/katalogiseret **efter** dec. 2015, og indgår derfor ikke i
dette specifikke public domain-snapshot. Den ~71.500-store samling, vi så
på den levende hjemmeside, er altså ikke tilgængelig ad denne (nøglefri,
robuste) vej.

## 3. Faktiske kolonner — ikke antaget på forhånd

Kolonnenavnene er læst direkte fra CSV-headeren og krydstjekket mod
snapshottets eget README. De 39 felter matcher præcis snapshot-repoets
egen dokumentation (UUID, Title, Contributor, Date/Date Start/Date End,
Subject Topical/Name/Geographic/Temporal/Title, Genre, Collection
Title/UUID, Digital Collections URL, m.fl.). Ingen overraskelser her —
usikkerheden lå i **dækningen**, ikke i **skemaet**.

## 4. Reproducerbar preprocessing

```bash
bash real_world_nypl/scripts/fetch_snapshot.sh /tmp/nypl_pd
python3 real_world_nypl/scripts/build_subject_name_subset.py /tmp/nypl_pd
python3 real_world_nypl/scripts/analyze_data_quality.py /tmp/nypl_pd
```

Da hverken Portrait File eller nogen anden enkelt collection i snapshottet
er stor nok, pivoterede vi til at bruge **hele "Subject Name"-feltet på
tværs af alle 190.494 items** som udgangspunkt — det felt, der (per NYPL's
egen skemadokumentation) angiver personer/organisationer, der er afbildet
eller beskrevet i et item. Output:

- `data/nypl_items_with_subject_name.csv` — 20.531 items med ≥1 Subject Name
- `data/nypl_unique_subject_names.csv` — 4.441 unikke Subject Name-strenge
  med antal items, antal distinkte titler, og en person/organisation-klassifikation

## 5-6. Linkage-relevante felter og datakvalitet

Fuld rapport: [`analysis/data_quality_report.md`](analysis/data_quality_report.md).

Hovedpunkter:

- **Subject Name** findes kun på **10,8 %** af alle items (20.531/190.494).
- **Description** er stort set tom (98,8 % missing) — kan ikke bruges som
  tekstfelt til linkage.
- **Date End** mangler i 75,9 % af tilfældene — de fleste items har kun én
  enkelt dato, ikke et interval.
- **27,8 %** af items deler (Title, Collection Title, Date) med mindst én
  anden post — et ikke-trivielt indslag af nær-dubletter i selve kataloget.
- Subject Name-feltet er **blandet**: 3.073 af 4.441 unikke strenge ligner
  personnavne (vores heuristik), men 1.368 er organisationer, bygninger,
  udstillinger eller sportshold (fx "New York Public Library" i 1.228
  items, "Centennial Exhibition (1876 : Philadelphia, Pa.)" i 770).

## 7. Kan Subject Name reelt bruges som ground truth/entity ID?

**Empirisk kontrolleret, ikke antaget — svaret er: delvist, med tre
konkrete forbehold:**

1. **Feltet blander enheder.** Uden vores efterfølgende person/organisation-
   heuristik ville "samme entitet går igen" i virkeligheden ofte betyde
   "samme bygning" eller "samme udstilling", ikke "samme person".
2. **Feltet er ikke selv 100 % konsistent.** Eksempel: samme person
   optræder som både `Camprubí, Mariano` og
   `Camprubí, Mariano, active 1834-1862` i forskellige poster (se
   `analysis/same_person_examples.md`). Den "facitliste", vi ville
   validere imod, har selv variation.
3. **Feltet betyder ikke altid "afbildet i".** For "Dickens, Charles,
   1812-1870" er de fleste af de 276 poster manuskripter **skrevet af**
   Dickens (Charles Dickens collection of papers), ikke portrætter **af**
   ham. Subject Name dækker altså både "er afbildet/omtalt" og reelt
   overlapper med ophavsmandsrollen (Contributor) for arkivmateriale.

## 8. Eksempler på samme person i flere records

18 konkrete eksempler, uredigerede, i
[`analysis/same_person_examples.md`](analysis/same_person_examples.md) —
spændende fra ren duplikering (Kyrle Bellew: 85 poster, identisk titel,
identisk dato) til reel navneform-variation (Lambert Cadwalader: "Col.
Lambert Cadwalader." / "Lambert Cadwalader" / "[L. Cadwalader]" på tværs af
forskellige stik fra Emmet Collection).

## 9. Kritisk vurdering: er datasættet egnet til vores record-linkage-eksperiment?

**Nej — ikke i den form, vi oprindeligt forestillede os, og det er
vigtigt at sige det direkte i stedet for at tvinge det til at passe.**

Tre strukturelle grunde:

1. **Den antagne datamængde findes ikke her.** Portrait File-antagelsen
   (71.500 billeder) holdt ikke empirisk (se punkt 1-2). Det, vi reelt
   har adgang til uden API-nøgle, er en langt mindre og skævere delmængde.
2. **Entiteterne er overvejende berømte/historiske figurer, ikke
   almindelige mennesker.** Washington, Lincoln, Dickens, Ramses II, Jeanne
   d'Arc — det er præcis det modsatte problem af HisPeR's: her er
   identiteten allerede fuldstændigt opløst af Library of Congress'
   autoritetsstyring, **før** vi rører dataene. Der er intet reelt
   "er dette samme person?"-spørgsmål tilbage at besvare på selve
   navnedimensionen.
3. **Der er ingen demografiske attributter.** Ingen alder, adresse,
   erhverv, familierelation. Datoerne er kunstværkets/optagelsens
   dato, ikke personens fødsels-/livshændelser. Der er dermed intet at
   bygge et "livsforløb" af, og ingen af vores eksisterende sanity checks
   (fødselsårskonflikt, umulig alder) giver mening på disse data.

Datasættet er derimod fint egnet til et **andet, mindre, ærligt afgrænset**
problem: at forudsige/matche en Library of Congress-autoritetsheading ud
fra fri tekst (titel/billedtekst) — en entity linking/tekstklassifikations-
opgave, ikke en demografisk person-record-linkage-opgave. At kalde det
"det samme eksperiment, bare med rigtige data" ville være misvisende over
for en HisPeR-reviewer, der kender forskellen.

### Anbefalede veje herfra (afventer din beslutning — intet er ændret i linkage-modellerne)

- **A.** Drop NYPL som "samme problem, rigtige data"-eksperiment. Behold
  det syntetiske benchmark som projektets kerne, og nævn evt. denne
  undersøgelse i README som dokumentation af, at vi undersøgte og bevidst
  fravalgte en kandidat — det er i sig selv en del af den kritiske,
  metodiske historie, HisPeR-briefet efterspørger.
- **B.** Behold NYPL-data, men reframe eksperimentet ærligt som et
  **andet, mindre supplement**: "kan vi forudsige subject-headingen fra fri
  tekst?" — tydeligt adskilt fra person-record-linkage-pipelinen, med sit
  eget README-afsnit, der forklarer forskellen.
- **C.** Gå tilbage til NYC City Directories-sporet (fra forrige
  undersøgelse), men accepter, at det kræver en OCR/parsing-indsats, vi
  endnu ikke har bygget, og en tilsvarende udvidelse af tidsrammen.

Jeg har ikke ændret `src/linkage_lab`, `workflow/Snakefile` eller den
eksisterende dokumentation. Alt ovenstående ligger isoleret i
`real_world_nypl/`.
