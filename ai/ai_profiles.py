# Optimized default strategy weights
# Base/default strategy
STRATEGY_DEFAULT = {
    "opening": {
        "mobility": 1.25, "corner": 1.5, "risk": 0.75,
        "frontier": 0.75,"pst": 1.0, "discs": 0.1,
    },
    "midgame": {
        "mobility": 1.25, "corner": 1.5,"risk": 0.5,
        "frontier": 1.0,"pst": 1.0,"discs": 0.5,
    },
    "endgame": {
        "mobility": 0.5, "corner": 1.25, "risk": 0.5,
        "frontier": 0.5,"pst": 0.5,"discs": 1.5,
    },
}


# Defensive: minimize risky exposures near empty corners
STRATEGY_DEFENSE = {
    "opening": {
        "mobility": 1.25, "corner": 1.5, "risk": 5.0,
        "frontier": 0.75, "pst": 1.0, "discs": 0.1,
    },
    "midgame": {
        "mobility": 1.25, "corner": 1.5, "risk": 5.0,
        "frontier": 1.0, "pst": 1.0, "discs": 0.5,
    },
    "endgame": {
        "mobility": 0.5, "corner": 1.25, "risk": 0.5,
        "frontier": 0.5, "pst": 0.5, "discs": 1.5,
    }
}

# Corner priority
STRATEGY_CORNERS = {
    "opening": {
        "mobility": 1.25, "corner": 5.0, "risk": 2.5,
        "frontier": 0.75, "pst": 1.0, "discs": 0.1,
    },
    "midgame": {
        "mobility": 1.25, "corner": 5.0, "risk": 2.5,
        "frontier": 1.0, "pst": 1.0, "discs": 0.5,
    },
    "endgame": {
        "mobility": 0.5, "corner": 5.0, "risk": 2.5,
        "frontier": 0.5, "pst": 0.5, "discs": 1.5,
    }
}

# Mobility priority
STRATEGY_MOBILITY = {
    "opening": {
        "mobility": 5.0, "corner": 1.5, "risk": 0.75,
        "frontier": 0.75, "pst": 2.5, "discs": 0.1,
    },
    "midgame": {
        "mobility": 5.0, "corner": 1.5, "risk": 0.5,
        "frontier": 1.0, "pst": 2.5, "discs": 0.5,
    },
    "endgame": {
        "mobility": 0.5, "corner": 1.25, "risk": 0.5,
        "frontier": 0.5, "pst": 0.5, "discs": 1.5,
    }
}

# Endgame focus
STRATEGY_ENDGAME = {
    "opening": {
        "mobility": 1.25, "corner": 1.5, "risk": 0.75,
        "frontier": 0.75, "pst": 1.0, "discs": 0.1,
    },
    "midgame": {
        "mobility": 1.25, "corner": 1.5, "risk": 0.5,
        "frontier": 1.0, "pst": 1.0, "discs": 0.5,
    },
    "endgame": {
        "mobility": 0.5, "corner": 2.0, "risk": 0.5,
        "frontier": 0.5, "pst": 1.0, "discs": 5.0,
    }
}

AI_PROFILES = [
    {
        "id": "DEFAULT",
        "name": "IA par défaut",
        "description": "Profil standard équilibré",
        "weights": STRATEGY_DEFAULT,
    },
    {
        "id": "DEFENSE",
        "name": "Défense",
        "description": "Réduit les risques près des coins vides",
        "weights": STRATEGY_DEFENSE,
    },
    {
        "id": "CORNERS",
        "name": "Coins",
        "description": "Privilégie l'obtention/maintien des coins",
        "weights": STRATEGY_CORNERS,
    },
    {
        "id": "MOBILITY",
        "name": "Mobilité",
        "description": "Maximise les options de coups valides",
        "weights": STRATEGY_MOBILITY,
    },
    {
        "id": "ENDGAME",
        "name": "Tout sur la fin",
        "description": "Accent sur le décompte final des disques",
        "weights": STRATEGY_ENDGAME,
    },
]
