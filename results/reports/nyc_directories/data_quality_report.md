# Datakvalitet: NYC city directory 1851/52 (udsnit)

Antal records i udsnittet: **8000**

## Parsing-succes

- `parse_ok` (efternavn + mindst erhverv eller adresse fundet): 7891 (98.6%)

- Flagget som sandsynligt kolonne-sammenblandings-artefakt (`likely_multi_entry`): 154 (1.9%)

## Manglende værdier

- surname: 53 mangler (0.7%)
- given_name: 125 mangler (1.6%)
- occupation: 496 mangler (6.2%)
- address_business: 776 mangler (9.7%)
- address_home: 5658 mangler (70.7%)

## Navnevariation og OCR-fejl

- Fornavne med formodet OCR-artefakt ("J ames" i stedet for "James"): 490 (6.2% af ikke-manglende fornavne), rettet af `standardization.fix_split_first_letter`.

- Eksakte (efternavn, fornavn)-kombinationer, der optræder mere end én gang: 485 ud af 6807 unikke kombinationer. Det højeste antal gentagelser af samme (efternavn, fornavn) er 16 (('campbell', 'james')).

Dette er ikke nødvendigvis dubletter - almindelige for- og efternavne i 1850'ernes New York (fx "John", "Cook") gentages i sagens natur på tværs af forskellige, ikke-relaterede personer. Se `data/raw/nyc_directories/MANUAL_BENCHMARK.md`.

## Erhvervsvariation

- Unikke rå erhvervsstrenge: 2017
- Unikke kanoniserede erhverv (efter opslag i IPUMS-ordliste): 1868
- Records hvor kanonisering ændrede den observerede streng: 3992 (49.9%)

## Adressevariation

- Records med business-adresse: 7224 (90.3%)
- Records med separat hjemme-adresse ('h.'/'r.'): 2342 (29.3%)

## Blocking false-negative-risiko (proxy, ikke fuld recall)

Ægte blocking recall kræver et fuldstændigt facit for alle mulige par, som vi ikke har (se docs/limitations.md). Som en billig proxy tælles records, der deler fornavn, erhverv OG adresse (stærk indikation af samme underliggende linje/person), men som blocking IKKE ville sætte i samme kandidat-blok pga. forskellig Soundex-kode for efternavnet (fx pga. en OCR-fejl i efternavnet):

- Grupper med samme fornavn+erhverv+adresse, men uenige om efternavns-Soundex: 3
