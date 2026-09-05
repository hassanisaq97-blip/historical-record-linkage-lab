# Livsforløb: sanity checks

Livsforløb konstrueres som sammenhængende komponenter i graf af accepterede par-links. For ML-metoden sammenlignes uafhængig par-klassifikation med one-to-one constrained assignment (se results/reports/constrained_assignment.md) - constraint fjerner per konstruktion alle 'multi_match'-konflikter, men retter ikke individuelt forkerte links.

## Metode: rule-based

Antal rekonstruerede livsforløb (sammenhængende komponenter): 1132

Heraf markeret med mindst ét problem: 34 (3.0% hvis n_total > 0)

Fordeling af problemtyper:

```
issues
multi_match            34
birth_year_conflict     5
```

Eksempler på markerede livsforløb:

|   life_course_id |   n_nodes | record_ids                               | birth_year_estimates     | issues                                 |
|-----------------:|----------:|:-----------------------------------------|:-------------------------|:---------------------------------------|
|               32 |         4 | ['C00098', 'C00669', 'R01527', 'R01556'] | [1802, 1803, 1803, 1802] | ['multi_match']                        |
|               51 |         3 | ['C00154', 'R00404', 'R02143']           | [1783, 1781, 1784]       | ['multi_match']                        |
|               59 |         4 | ['C00176', 'C02539', 'R01337', 'R02778'] | [1825, 1822, 1823, 1821] | ['multi_match', 'birth_year_conflict'] |
|               65 |         3 | ['C00189', 'C02827', 'R02885']           | [1822, 1825, 1824]       | ['multi_match']                        |
|               70 |         3 | ['C00198', 'C02747', 'R02934']           | [1812, 1810, 1811]       | ['multi_match']                        |



## Metode: ml_random_forest (uden constraint)

Antal rekonstruerede livsforløb (sammenhængende komponenter): 1456

Heraf markeret med mindst ét problem: 718 (49.3% hvis n_total > 0)

Fordeling af problemtyper:

```
issues
multi_match            684
birth_year_conflict    412
```

Eksempler på markerede livsforløb:

|   life_course_id |   n_nodes | record_ids                                                                                                                                             | birth_year_estimates                                                                       | issues                                 |
|-----------------:|----------:|:-------------------------------------------------------------------------------------------------------------------------------------------------------|:-------------------------------------------------------------------------------------------|:---------------------------------------|
|                0 |         4 | ['C00000', 'C01843', 'R01267', 'R02231']                                                                                                               | [1785, 1785, 1784, 1783]                                                                   | ['multi_match']                        |
|                1 |         5 | ['C00001', 'C00354', 'C01686', 'R00096', 'R00174']                                                                                                     | [1806, 1804, 1807, 1804, 1805]                                                             | ['multi_match']                        |
|                2 |        15 | ['C00002', 'C00251', 'C00612', 'C00762', 'C01289', 'C01892', 'C02420', 'C02615', 'R00426', 'R00541', 'R00557', 'R01149', 'R01546', 'R01765', 'R02881'] | [1828, 1827, 1828, 1833, 1822, 1830, 1827, 1831, 1828, 1822, 1828, 1827, 1827, 1822, 1820] | ['multi_match', 'birth_year_conflict'] |
|                3 |         9 | ['C00003', 'C00950', 'C01278', 'C02007', 'C02741', 'R00515', 'R00850', 'R01377', 'R02831']                                                             | [1784, 1785, 1782, 1787, 1791, 1792, 1794, 1781, 1794]                                     | ['multi_match', 'birth_year_conflict'] |
|                4 |         5 | ['C00004', 'C00910', 'R00295', 'R01458', 'R02490']                                                                                                     | [1797, 1797, 1798, 1791, 1796]                                                             | ['multi_match', 'birth_year_conflict'] |



## Metode: ml_random_forest (med one-to-one constraint)

Antal rekonstruerede livsforløb (sammenhængende komponenter): 2145

Heraf markeret med mindst ét problem: 81 (3.8% hvis n_total > 0)

Fordeling af problemtyper:

```
issues
birth_year_conflict    81
```

Eksempler på markerede livsforløb:

|   life_course_id |   n_nodes | record_ids           | birth_year_estimates   | issues                  |
|-----------------:|----------:|:---------------------|:-----------------------|:------------------------|
|               19 |         2 | ['C00029', 'R02682'] | [1798, 1802]           | ['birth_year_conflict'] |
|               20 |         2 | ['C00030', 'R00910'] | [1840, 1845]           | ['birth_year_conflict'] |
|               45 |         2 | ['C00065', 'R00854'] | [1805, 1800]           | ['birth_year_conflict'] |
|               46 |         2 | ['C00066', 'R00097'] | [1808, 1804]           | ['birth_year_conflict'] |
|              114 |         2 | ['C00165', 'R01930'] | [1783, 1787]           | ['birth_year_conflict'] |

