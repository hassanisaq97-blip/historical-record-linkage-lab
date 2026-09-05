# Fejl-eksempler: rule-based

## False positives

| record_id_a                    | record_id_b                    | a_given_name   | a_occupation   | a_address_business   |   a_address_home | b_given_name   | b_occupation   | b_address_business   |   b_address_home |
|:-------------------------------|:-------------------------------|:---------------|:---------------|:---------------------|-----------------:|:---------------|:---------------|:---------------------|-----------------:|
| nypl_1851_1852_doggetts_006835 | nypl_1851_1852_doggetts_006839 | Patrick        | laborer        | 184' Hester          |              nan | Patrick        | laborer        | 225 Eleventh         |              nan |

## False negatives

| record_id_a                    | record_id_b                    | a_given_name   | a_occupation   | a_address_business   | a_address_home   | b_given_name   | b_occupation   | b_address_business   |   b_address_home |
|:-------------------------------|:-------------------------------|:---------------|:---------------|:---------------------|:-----------------|:---------------|:---------------|:---------------------|-----------------:|
| nypl_1851_1852_doggetts_004877 | nypl_1851_1852_doggetts_004878 | J ohn          | fishtackle     | 52 Fulton            | 160 Av . 1       | J ohn C        | fishtackle     | 52 Fulton            |              nan |
