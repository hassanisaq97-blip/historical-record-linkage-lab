"""Static name/place pools and spelling-variant maps used by the synthetic
data generator. Entirely fabricated for this project - not sourced from any
real archive or register.
"""

GIVEN_NAMES_MALE = [
    "Anders", "Christian", "Frederik", "Hans", "Jens", "Joergen", "Lars",
    "Mads", "Niels", "Ole", "Peder", "Rasmus", "Soeren", "Thomas",
    "Christen", "Morten", "Iver", "Knud", "Poul", "Erik",
]

GIVEN_NAMES_FEMALE = [
    "Anna", "Bodil", "Dorthe", "Else", "Gunhild", "Inger", "Karen",
    "Kirsten", "Maren", "Marie", "Mette", "Sidsel", "Sophie", "Ingeborg",
    "Johanne", "Kirstine", "Ellen", "Birgitte", "Cathrine", "Margrethe",
]

SURNAMES = [
    "Jensen", "Nielsen", "Hansen", "Pedersen", "Andersen", "Christensen",
    "Larsen", "Soerensen", "Rasmussen", "Joergensen", "Petersen", "Madsen",
    "Kristensen", "Olsen", "Thomsen", "Christiansen", "Poulsen",
    "Johansen", "Moeller", "Mortensen",
]

# Deliberately overlapping / confusable spelling variants: transcription
# noise can turn one canonical surname into a string that collides with a
# *different* canonical surname (e.g. Christensen <-> Kristensen). This is
# a realistic source of false positives/negatives in patronymic naming
# systems, not a data-generation bug.
SURNAME_VARIANTS = {
    "Jensen": ["Jenssen", "Jensen", "Jenson"],
    "Nielsen": ["Nielssen", "Nilsen"],
    "Hansen": ["Hanssen", "Hantzen"],
    "Pedersen": ["Peedersen", "Peiderssen"],
    "Andersen": ["Anderssen", "Andersøn"],
    "Christensen": ["Kristensen", "Christiansen"],
    "Larsen": ["Larssen", "Larsøn"],
    "Soerensen": ["Sørensen", "Sørrensen"],
    "Rasmussen": ["Rasmusen", "Rasmusøn"],
    "Joergensen": ["Jørgensen", "Jørgenssen"],
    "Petersen": ["Peetersen", "Peterßen"],
    "Madsen": ["Matzen", "Madtzen"],
    "Kristensen": ["Christensen", "Kristensøn"],
    "Olsen": ["Olssen", "Oelsen"],
    "Thomsen": ["Tomsen", "Thomssen"],
    "Christiansen": ["Christensen", "Kristiansen"],
    "Poulsen": ["Paulsen", "Poulssen"],
    "Johansen": ["Johannsen", "Johanssen"],
    "Moeller": ["Møller", "Moeler"],
    "Mortensen": ["Mortenssen", "Martensen"],
}

CANONICAL_PLACES = [
    "Koebenhavn", "Odense", "Aarhus", "Aalborg", "Roskilde", "Ribe",
    "Viborg", "Randers", "Helsingoer", "Slagelse", "Svendborg",
    "Fredericia", "Horsens", "Kolding", "Naestved",
]

PLACE_VARIANTS = {
    "Koebenhavn": ["Kjøbenhavn", "Kiøbenhavn", "Kbh"],
    "Odense": ["Odensee", "Odence"],
    "Aarhus": ["Århus", "Aarhuus"],
    "Aalborg": ["Ålborg", "Aalborrig"],
    "Roskilde": ["Roeskilde", "Roskilda"],
    "Ribe": ["Ripen", "Riibe"],
    "Viborg": ["Wiborg", "Viiborg"],
    "Randers": ["Randerss", "Randres"],
    "Helsingoer": ["Helsingør", "Elsinore"],
    "Slagelse": ["Slaugelse", "Slagelsse"],
    "Svendborg": ["Svenborg", "Svendborrig"],
    "Fredericia": ["Frederitia", "Fredericea"],
    "Horsens": ["Horssens", "Horsends"],
    "Kolding": ["Coldingen", "Koldinng"],
    "Naestved": ["Næstved", "Nestved"],
}

OCCUPATIONS = [
    "gaardmand", "husmand", "tjenestepige", "daglejer", "skraedder",
    "smed", "fisker", "skomager", "murer", "handelsmand",
]
