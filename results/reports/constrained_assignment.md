# Constrained one-to-one assignment (ML-metode)

Census- og kirkebogsposter er hver især en unik person i den syntetiske population, saa hvert census-record boer i princippet matche hoejst ét kirkebogs-record og omvendt. Uafhaengig par-klassifikation haandhaever ikke dette, hvilket kan skabe konflikter (samme record accepteret i flere links).

- Accepterede par (uafhaengig klassifikation): 4113
- Records med konflikt (>1 accepteret link) FOER constraint: 2315
- Accepterede par EFTER one-to-one constraint: 2145
- Records med konflikt EFTER constraint: 0
- Par droppet af constraint: 1968

## Effekt paa precision/recall/F1 blandt de accepterede par (alle splits)

| | Precision | Recall | F1 | Accepterede par |
|---|---:|---:|---:|---:|
| Foer constraint | 0.470 | 0.996 | 0.639 | 4113 |
| Efter constraint | 0.836 | 0.924 | 0.878 | 2145 |

Constraint handler kun links, som allerede er accepteret af ML-modellen: den kan kun fjerne par (aldrig tilfoeje nye), saa recall kan ikke stige - men ved at fjerne lavere-scorende konkurrerende par til fordel for det hoejest-scorende link pr. record stiger precision markant, fordi mange af de droppede par var false positives.
