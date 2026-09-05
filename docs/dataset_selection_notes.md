# Valg af real-world datasæt: proces og fravalg

Dette dokument opsummerer, hvordan det virkelige (ikke-syntetiske) datasæt
i dette projekt blev valgt. Det er bevaret som en kort metodisk note,
fordi selve fravalgsprocessen er en del af den kritiske, undersøgende
tilgang, projektet skal demonstrere - men de fulde mellemregninger
(rådata, scripts, delrapporter fra den første, forkastede kandidat) er
fjernet fra repositoryet for at holde det fokuseret.

## Fravalgt: NYPL "Print Collection portrait file"

Første kandidat var NYPL Digital Collections' portrætsamlinger, tilgået
via NYPL's officielle public-domain metadata-snapshot
(`NYPL-publicdomain/data-and-utilities` på GitHub, intet API-nøve krav).

Efter faktisk at hente og undersøge snapshottet viste to ting sig:

1. Den ~71.500-billeder store "Print Collection portrait file" fra den
   levende hjemmeside er kun repræsenteret med **10 items** i dette
   2015-snapshot - langt for lille en delmængde.
2. Det bredere "Subject Name"-felt (personer/organisationer nævnt i
   items) viste sig at bestå overvejende af **allerede berømte,
   allerede identitetsopløste historiske figurer** (Washington, Dickens,
   Ramses II) uden demografiske attributter (alder, adresse, erhverv,
   familie). Det er strukturelt det modsatte af HisPeR's problem: der er
   intet reelt "er dette samme person?"-spørgsmål tilbage, fordi Library
   of Congress' autoritetsstyring allerede har løst identiteten, før vi
   rører dataene.

Konklusion: datasættet blev vurderet **ikke egnet** til person-record-
linkage og blev fravalgt, i stedet for at blive tvunget til at passe.

## Valgt: NYC City Directory 1851/52 (Doggett's)

Se `data/raw/nyc_directories/PROVENANCE.md` for fuld kildedokumentation og
`README.md`'s afsnit om datasæt for hvordan det bruges. Kort:

- Ægte OCR'et tekst fra NYPL's egen `city-directory-entry-parser`-repo
  (GitHub, MIT-licens), tilgængelig uden API-nøgle eller scraping.
- Har navn, erhverv og adresse pr. record - reelle demografiske/sociale
  attributter, modsat portrætmetadata.
- Kun én årgang er tilgængelig via denne vej (netværksadgang til
  digitalcollections.nypl.org, archive.org og hathitrust.org er blokeret
  i dette udviklingsmiljø - verificeret empirisk, se
  `docs/limitations.md`), så projektet demonstrerer entity resolution
  **inden for** én kilde snarere end livsforløb på tværs af årgange.
