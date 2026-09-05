# Datakilde: NYC City Directory 1851/52 (Doggett's)

**Kilde:** [`nypl-spacetime/city-directory-entry-parser`](https://github.com/nypl-spacetime/city-directory-entry-parser)
(NYPL's officielle GitHub-organisation for NYC Space/Time Directory-projektet).

- Commit: `cb695a94a4d4ef57561a77f62f518d773321fe6d` (2017-11-17)
- Licens: MIT (© 2017 Stephen Balogh) - se `LICENSE.md` i kilde-repoet
- Filer vendored uændret:
  - `nypl-1851-1852-entries-sample.txt` - 87.674 rå OCR-linjer fra Doggett's
    New York City Directory, 1851/52
  - `nypl-labeled-70-training.csv` - 70 håndlabelede eksempler (token-niveau:
    navn/erhverv/adresse), brugt til at træne og krydsvalidere parseren
  - `nypl_occupations_vocab.json` - IPUMS-baseret erhvervsordliste, hentet fra
    en tidligere commit (`300c9e5`) i samme repo, hvor filen endnu fandtes

## Hvorfor vendored i stedet for downloadet ved kørsel

Dette repository kan normalt genskabe alle datasæt reproducerbart via
download-scripts. For NYC-directory-data er det ikke muligt i dette
udviklingsmiljø: direkte netværksadgang til `digitalcollections.nypl.org`,
`archive.org`, `hathitrust.org` og `loc.gov` er blokeret af miljøets
egress-politik (verificeret empirisk - se `docs/limitations.md`). Kun
GitHub og pakke-registre (PyPI mv.) er tilgængelige. Da city directory-data
kun findes tilgængeligt via denne ene GitHub-fil (ingen officiel bulk-CSV
findes for flere årgange, jf. undersøgelsen i `real_world_nypl_investigation_notes.md`),
er filerne vendored direkte. De er små (< 4 MB tilsammen), rene tekstfiler
(ikke binære), og MIT-licenserede - i overensstemmelse med instruksen om
kun at undgå at committe *store binære* datasæt, der kunne hentes
reproducerbart.

## Hvorfor kun én årgang

Den oprindelige plan var 3-5 årgange for at kunne demonstrere linkage på
tværs af tid. NYPL har digitaliseret 1786-1922, men har - så vidt vi kan
verificere inden for dette miljøs netværksbegrænsninger - kun publiceret
**denne ene årgangs** OCR-tekst som et frit tilgængeligt bulk-udtræk uden
API-nøgle. Det reelle datasæt bruges derfor til at demonstrere
standardisering, blocking, similarity-features og entity resolution
**inden for én kilde** (personer optræder i visse tilfælde mere end én
gang i samme årgang - se `docs/limitations.md`), mens tværgående
livsforløb (over tid/kilder) fortsat demonstreres på det syntetiske
datasæt, hvor det rent faktisk er understøttet af data.
