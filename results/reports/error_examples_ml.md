# Fejl-eksempler: ml

## False positives

| census_record_id   | parish_record_id   | census_given_name   | census_surname   |   census_age | census_birth_place   | parish_given_name   | parish_surname   |   parish_birth_year | parish_birth_place   |
|:-------------------|:-------------------|:--------------------|:-----------------|-------------:|:---------------------|:--------------------|:-----------------|--------------------:|:---------------------|
| C00004             | R02490             | Mette               | Petersen         |           54 | nan                  | Mette               | Pedersen         |                1791 | Slagelse             |
| C00017             | R00273             | Christen            | AAndersen        |           43 | Fredericia           | Christian           | Andersne         |                1804 | Kolding              |
| C00020             | R00591             | Johanne             | Johansen         |           14 | Svenborg             | Johanne             | Jensen           |                1835 | Ribe                 |
| C00032             | R01157             | Maren               | Hansen           |           51 | Helsingoer           | Karen               | Hansen           |                1800 | Viborg               |
| C00046             | R01563             | Kirstine            | Andersen         |           36 | Slagelse             | Kirstine            | Andersen         |                1816 | Randers              |
| C00057             | R02950             | Hans                | Nielsen          |           44 | Helsingoer           | Hans                | Niielsen         |                1808 | Fredericia           |
| C00073             | R01013             | Morten              | Peedersen        |           57 | Roskilde             | Morten              | Pedersen         |                1794 | Slagelse             |
| C00077             | R01402             | Knud                | Martensen        |           67 | Svendborg            | Knud                | Martensen        |                1785 | Odense               |

## False negatives

| census_record_id   | parish_record_id   | census_given_name   | census_surname   |   census_age | census_birth_place   | parish_given_name   | parish_surname   |   parish_birth_year | parish_birth_place   |
|:-------------------|:-------------------|:--------------------|:-----------------|-------------:|:---------------------|:--------------------|:-----------------|--------------------:|:---------------------|
| C00113             | R02816             | Ellen               | Christensen      |           52 | Roeskilde            | Ellen               | Christensen      |                1790 | Roskilde             |
| C00683             | R02094             | Peder               | Jenssen          |           39 | Vbiorg               | Peder               | Jensen           |                1817 | Viborg               |
| C00902             | R01792             | lOe                 | Pedersen         |           12 | Roeskilde            | Oel                 | Pedersen         |                1838 | Rtskilde             |
| C01451             | R02612             | Dorte               | Olsen            |           31 | Koebenhavn           | Doethe              | Olsen            |                1821 | Koebenhavn           |
| C01736             | R02746             | Erpk                | Mortensen        |           64 | Ribe                 | Erik                | Mortensen        |                1793 | Ribe                 |
