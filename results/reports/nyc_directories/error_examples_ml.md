# Fejl-eksempler: ml

## False positives

| record_id_a                    | record_id_b                    | a_given_name   | a_occupation   | a_address_business   |   a_address_home | b_given_name   | b_occupation   | b_address_business   |   b_address_home |
|:-------------------------------|:-------------------------------|:---------------|:---------------|:---------------------|-----------------:|:---------------|:---------------|:---------------------|-----------------:|
| nypl_1851_1852_doggetts_006835 | nypl_1851_1852_doggetts_006839 | Patrick        | laborer        | 184' Hester          |              nan | Patrick        | laborer        | 225 Eleventh         |              nan |
| nypl_1851_1852_doggetts_002753 | nypl_1851_1852_doggetts_002763 | A . D          | painter        | 7 E . 13th           |              nan | Allen          | painter        | 103 Delaney          |              nan |

## False negatives

| record_id_a   | record_id_b   | a_given_name   | a_occupation   | a_address_business   | a_address_home   | b_given_name   | b_occupation   | b_address_business   | b_address_home   |
|---------------|---------------|----------------|----------------|----------------------|------------------|----------------|----------------|----------------------|------------------|
