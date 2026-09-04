# Livsforløb: sanity checks

Livsforløb konstrueres som sammenhængende komponenter i graf af accepterede par-links (uden en one-to-one-begrænsning på match). Se docs/limitations.md for diskussion af denne begrænsning.

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
|               32 |         4 | ['C00098', 'C00669', 'R01527', 'R01556'] | [1802, 1802, 1803, 1803] | ['multi_match']                        |
|               51 |         3 | ['C00154', 'R00404', 'R02143']           | [1784, 1783, 1781]       | ['multi_match']                        |
|               59 |         4 | ['C00176', 'C02539', 'R01337', 'R02778'] | [1825, 1823, 1821, 1822] | ['multi_match', 'birth_year_conflict'] |
|               65 |         3 | ['C00189', 'C02827', 'R02885']           | [1822, 1824, 1825]       | ['multi_match']                        |
|               70 |         3 | ['C00198', 'C02747', 'R02934']           | [1811, 1812, 1810]       | ['multi_match']                        |


## Metode: ml_random_forest

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
|                1 |         5 | ['C00001', 'C00354', 'C01686', 'R00096', 'R00174']                                                                                                     | [1804, 1804, 1805, 1806, 1807]                                                             | ['multi_match']                        |
|                2 |        15 | ['C00002', 'C00251', 'C00612', 'C00762', 'C01289', 'C01892', 'C02420', 'C02615', 'R00426', 'R00541', 'R00557', 'R01149', 'R01546', 'R01765', 'R02881'] | [1833, 1822, 1828, 1828, 1828, 1830, 1822, 1827, 1820, 1827, 1827, 1831, 1827, 1828, 1822] | ['multi_match', 'birth_year_conflict'] |
|                3 |         9 | ['C00003', 'C00950', 'C01278', 'C02007', 'C02741', 'R00515', 'R00850', 'R01377', 'R02831']                                                             | [1784, 1781, 1794, 1787, 1792, 1782, 1794, 1791, 1785]                                     | ['multi_match', 'birth_year_conflict'] |
|                4 |         5 | ['C00004', 'C00910', 'R00295', 'R01458', 'R02490']                                                                                                     | [1791, 1797, 1796, 1797, 1798]                                                             | ['multi_match', 'birth_year_conflict'] |

