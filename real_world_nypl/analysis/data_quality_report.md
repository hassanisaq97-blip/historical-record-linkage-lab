# Datakvalitet: NYPL public-domain snapshot, Subject Name-felt

Kilde: `NYPL-publicdomain/data-and-utilities` (snapshot frosset 2015-12-30). Fuldt snapshot: **190494 items**. Heraf med mindst ét 'Subject Name': **20531** (10.8%).

## Manglende værdier (blandt items med >=1 Subject Name)

| felt             |   n_missing |   andel_missing |
|:-----------------|------------:|----------------:|
| Title            |           5 |     0.000243534 |
| Date             |        5737 |     0.279431    |
| Date Start       |        6245 |     0.304174    |
| Date End         |       15581 |     0.758901    |
| Contributor      |         516 |     0.0251327   |
| Subject Name     |           0 |     0           |
| Subject Topical  |        8975 |     0.437144    |
| Genre            |        4202 |     0.204666    |
| Description      |       20287 |     0.988116    |
| Collection Title |          49 |     0.00238663  |

## Nær-dubletter

Andel items, der deler (Title, Collection Title, Date) med mindst én anden post: **27.8%**. Dette er katalogpraksis (fx samme fotosession registreret som flere separate 'captures'/negativer), ikke fejl i vores udtræk - men det betyder, at en del af 'flere records for samme person' i praksis er næsten-identiske dubletter uden reelt linkage-problem.

## Subject Name: person vs. organisation/andet

Feltet 'Subject Name' i MODS-skemaet dækker eksplicit BÅDE personer OG organisationer/bygninger/begivenheder (jf. NYPL's egen felt-dokumentation: "people or organizations described or depicted"). Vi har derfor bygget en simpel, gennemsigtig heuristik (komma til stede, ingen parentes, ingen virksomheds-/institutionsnøgleord) til at adskille de to - IKKE antaget at alle værdier er personer.

- Unikke Subject Name-strenge i alt: **4441**
- Heraf klassificeret som person: **3073**
- Heraf klassificeret som organisation/andet: **1368**

### Top 10 hyppigste ORGANISATIONER/andet (bekræfter at feltet er blandet)

| name                                                            |   n_items |
|:----------------------------------------------------------------|----------:|
| New York Public Library                                         |      1228 |
| Centennial Exhibition (1876 : Philadelphia, Pa.)                |       770 |
| New York Public Library. Humanities and Social Sciences Library |       449 |
| Temple of Hathor (Dandara, Egypt)                               |       417 |
| White House (Washington, D.C.)                                  |       407 |
| Pennsylvania Railroad                                           |       360 |
| World's Columbian Exposition (1893 : Chicago, Ill.)             |       272 |
| Geographical Surveys West of the 100th Meridian (U.S.)          |       262 |
| Independence Hall (Philadelphia, Pa.)                           |       190 |
| Central Pacific Railroad Company                                |       187 |

## Records pr. person (kun heuristisk person-klassificerede navne)

- Personer med >=2 items: **1219**
- Personer med >=5 items: **401**
- Personer med >=10 items: **166**
- Højeste antal items for én person: **643** (Washington, George, 1732-1799)

## Titel-diversitet pr. person (er 'flere records' reelt forskellige poster?)

Blandt de 1219 personer med >=2 items:
- Andel hvor ALLE poster har identisk titel (0 reel tekstvariation): **6.3%**
- Andel hvor >80% af titlerne er indbyrdes forskellige (reel diversitet): **68.7%**
