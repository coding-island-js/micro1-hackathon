"""Ingredient -> allergen lookup, for the spike only.

The nine major allergens are defined by US law (FALCPA plus the 2021 FASTER Act, which
added sesame). We do not get to choose them.

The mapping below is the part we would have to author, and it is the weak point of the
whole idea. For the spike it is hand-written and deliberately focused on the HIDDEN cases
-- the ones where a fast reader misses it. If this idea survives, every row needs a public
citation before it goes near a benchmark.
"""

# allergen -> ingredient substrings that contain it
HIDDEN = {
    "milk": [
        "ghee", "butter", "casein", "whey", "paneer", "curd", "yogurt", "yoghurt",
        "cream", "custard", "ricotta", "mozzarella", "parmesan", "cheddar", "feta",
        "halloumi", "mascarpone", "creme fraiche", "buttermilk", "condensed milk",
        "evaporated milk", "milk powder", "kefir", "labneh", "queso", "alfredo",
    ],
    "tree nuts": [
        "almond", "marzipan", "frangipane", "praline", "nutella", "cashew", "pistachio",
        "walnut", "pecan", "hazelnut", "macadamia", "brazil nut", "pine nut", "nougat",
        "amaretto", "pesto",
    ],
    "peanuts": ["peanut", "groundnut", "satay", "arachis"],
    "fish": [
        "worcestershire", "anchov", "fish sauce", "nam pla", "nuoc mam", "caesar dressing",
        "gentleman's relish", "bonito", "dashi", "colatura", "surimi",
    ],
    "shellfish": [
        "shrimp", "prawn", "crab", "lobster", "crayfish", "langoustine", "belacan",
        "shrimp paste", "oyster sauce", "krill",
    ],
    "sesame": ["sesame", "tahini", "hummus", "houmous", "halva", "za'atar", "zaatar",
               "gomashio", "benne"],
    "soy": ["soy", "soya", "tofu", "edamame", "miso", "tempeh", "tamari", "hoisin",
            "teriyaki", "textured vegetable protein"],
    "wheat": ["wheat", "flour", "bread", "pasta", "couscous", "semolina", "seitan",
              "panko", "breadcrumb", "roux", "farro", "bulgur", "orzo", "soy sauce",
              "udon", "phyllo", "filo", "puff pastry", "tortilla", "naan", "chapati",
              "pita", "cracker", "barley", "malt", "spelt"],
    "eggs": ["egg", "mayonnaise", "mayo", "aioli", "meringue", "hollandaise", "custard",
             "brioche", "challah", "marshmallow"],
}

# Things that look like a violation but are not, so the spike does not cry wolf.
EXEMPT = [
    "nutmeg", "nutritional yeast", "coconut", "water chestnut", "butternut",
    "buttercup", "butterhead", "peanut-free", "nut-free", "egg-free", "dairy-free",
    "milk-free", "soy-free", "gluten-free", "wheat-free", "sesame-free", "fish-free",
    "shellfish-free", "butter lettuce", "cocoa butter", "shea butter", "coconut milk",
    "almond-free", "no nuts", "without nuts", "instead of butter", "instead of ghee",
    "rather than ghee", "buckwheat",
]


def scan(text: str, avoid: list) -> list:
    """Return every hit for the allergens this request said to avoid."""
    low = text.lower()
    for phrase in EXEMPT:
        low = low.replace(phrase, " ")
    hits = []
    for allergen in avoid:
        for token in HIDDEN.get(allergen, []):
            idx = low.find(token)
            if idx != -1:
                start = max(0, idx - 60)
                hits.append({
                    "allergen": allergen,
                    "ingredient": token,
                    "context": text[start:idx + 60].replace("\n", " ").strip(),
                })
    return hits
