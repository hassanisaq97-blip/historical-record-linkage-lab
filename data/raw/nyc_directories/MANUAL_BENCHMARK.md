# Manuelt benchmark: nypl_1851_1852_doggetts

Der findes intet pålideligt ground-truth-felt for "samme person" i city
directory-data (modsat det syntetiske datasæt, hvor vi selv kontrollerer
den skjulte sandhed). Dette dokument beskriver, hvordan et lille, manuelt
valideret benchmark i stedet blev konstrueret - i overensstemmelse med
kravet om ikke at opfinde ground truth.

## Udvælgelseskriterier

Benchmarket dækker **92 kandidatpar** fra blocking-trinnet (surname
Soundex + fornavns-forbogstav) på de første 8.000 linjer af kilden,
sammensat af to strata:

1. **Stratificeret tilfældig stikprøve (79 par)**: 30 par med eksakt
   fornavns-match, 30 par med fornavns-similaritet 0,80-0,99, 20 par med
   similaritet under 0,80 (fast seed=42, se `/tmp` build-script-logik
   reproduceret i test-suiten). Formålet var at se den "naturlige"
   fordeling af kandidatpar efter blocking.
2. **Målrettet stikprøve af stærk evidens (13 par)**: alle par med
   samtidig eksakt erhvervs-match OG adresse-similaritet ≥ 0,90 OG
   fornavns-similaritet ≥ 0,80. Nødvendigt fordi ægte dubletter er
   **sjældne** i et enkelt directory-år (jf. fund nedenfor) - en ren
   tilfældig stikprøve gav kun ét klart positivt eksempel ud af 80 par.

**Vigtig konsekvens:** Fordi det andet stratum bevidst er beriget med
kandidater, der ligner matches, afspejler benchmarkets 14/92 (15,2 %)
positive andel **ikke** den sande dubletrate i datasættet. Benchmarket
kan bruges til at evaluere, om en metode kan **skelne** mellem match og
ikke-match, når begge forekommer - ikke til at estimere den faktiske
forekomst af dubletter i den fulde population.

## Hvem annoterede, og hvordan

Alle 92 par blev gennemgået og vurderet af projektets forfatter ud fra de
synlige, standardiserede felter (fornavn, efternavn, erhverv,
forretnings-/hjemmeadresse) og selve den rå OCR-linje - **ikke** af en
uafhængig ekspert, og **ikke** krydstjekket mod andre historiske kilder
(fx den faktiske folketælling for 1850, som kunne have bekræftet eller
afkræftet enkelte par). Der er derfor tale om et "sølv", ikke et "guld"
benchmark.

Beslutningskriterier:

- **Match (1):** samme/næsten samme fornavn OG mindst ét af (identisk
  erhverv, identisk eller meget nærliggende adresse på samme gade).
- **Ikke-match (0):** delt efternavn/forbogstav (blocking-kriteriet) uden
  understøttende erhvervs- eller adressebevis - langt den hyppigste
  situation, fordi 1850'ernes New York havde stærkt genbrugte for- og
  efternavne.
- Eksplicitte modsigelser (forskelligt køn, eksplicit "jr."/anden
  mellemnavns-initial, "enke efter X" med forskelligt X) blev altid
  kodet som ikke-match, selv ved høj tekst-similaritet.
- Ét par blev udelukket helt: `nypl_1851_1852_doggetts_007791`/`_007815`,
  hvor selve parseren fejlede (efternavnet blev fejlagtigt "35") - vi
  gætter ikke et label på et kendt parse-fejl-tilfælde.

## Usikkerheder

- **Lille stikprøve** (92 par) - for lidt til stabile procent-estimater
  med snævre konfidensintervaller.
- **Én annotator, ingen uafhængig second opinion** - annotator-bias kan
  ikke udelukkes, særligt for de mest usikre par (markeret
  `annotator_confidence=low/medium` i `manual_benchmark_labels.csv`).
- Mindst ét par (`nypl_1851_1852_doggetts_006785`/`_006794`) er kodet som
  match med lav tillid, fordi de delte felter ("ames" som erhverv) selv
  bærer præg af et OCR/kolonne-parsing-artefakt snarere end en ren
  tekstuel dublet - det er uklart, om det reelt repræsenterer to
  registreringer af samme kilde-linje eller en tilfældig sammenfaldende
  fejlparsing.
- Et par som `cook john`/`john son` @ 755 broadway (identisk adresse og
  erhverv) kunne lige så vel repræsentere far og søns fælles forretning
  ("John Cook & Son") som samme individ - kodet som match, men med
  eksplicit note om alternativ tolkning.

Se `data/processed/nyc_directories/` (genereret, ikke committed) for de
fulde standardiserede felter bag hvert par, og
`results/reports/nyc_directories/` for hvordan benchmarket bruges i
evalueringen.
