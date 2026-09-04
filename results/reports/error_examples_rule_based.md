# Fejl-eksempler: rule-based

## False positives

| census_record_id   | parish_record_id   | census_given_name   | census_surname   |   census_age | census_birth_place   | parish_given_name   | parish_surname   |   parish_birth_year | parish_birth_place   |
|:-------------------|:-------------------|:--------------------|:-----------------|-------------:|:---------------------|:--------------------|:-----------------|--------------------:|:---------------------|
| C01068             | R00377             | Maren               | Soerensen        |           44 | Naestved             | Marie               | Sørensen         |                1806 | Næstved              |
| C02479             | R00836             | Marie               | Soerensen        |           46 | Naestved             | Maren               | Sørnsen          |                1806 | Naestved             |

## False negatives

| census_record_id   | parish_record_id   | census_given_name   | census_surname   |   census_age | census_birth_place   | parish_given_name   | parish_surname   |   parish_birth_year | parish_birth_place   |
|:-------------------|:-------------------|:--------------------|:-----------------|-------------:|:---------------------|:--------------------|:-----------------|--------------------:|:---------------------|
| C00004             | R00295             | Mette               | Petersen         |           54 | nan                  | Mette               | Petersen         |                1798 | Randers              |
| C00031             | R02342             | Drothe              | Larssen          |           11 | Odeense              | Dorthe              | Larssen          |                1838 | Oddensee             |
| C00039             | R01282             | Johanne             | Olsen            |           49 | Kiøbenhavn           | Johanne             | Olsen            |                1798 | Koebenhavn           |
| C00041             | R01412             | Jens                | Andersen         |           34 | Odense               | Jens                | Andeersen        |                1818 | nan                  |
| C00051             | R01696             | Peder               | Oelsen           |           39 | Svendborg            | Peder               | Olsen            |                1813 | Svenborg             |
| C00057             | R02857             | Hans                | Nielsen          |           44 | Helsingoer           | Hans                | Nielsen          |                1806 | wlsinore             |
| C00061             | R02180             | Rasmus              | Joergensen       |           56 | Odense               | Rasmus              | Jørgenssen       |                1793 | Odeense              |
| C00077             | R00932             | Knud                | Martensen        |           67 | Svendborg            | Knud                | Morteensen       |                1784 | Svendborg            |
