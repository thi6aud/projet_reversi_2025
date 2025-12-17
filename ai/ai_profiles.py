# Optimized default strategy weights
# Base/default strategy
STRATEGY_DEFAULT = {
    "opening": {
        "mobility": 1.25,
        "corner": 1.5,
        "risk": 0.75,
        "frontier": 0.75,
        "pst": 1.0,
        "discs": 0.1,
    },
    "midgame": {
        "mobility": 1.25,
        "corner": 1.5,
        "risk": 0.5,
        "frontier": 1.0,
        "pst": 1.0,
        "discs": 0.5,
    },
    "endgame": {
        "mobility": 0.5,
        "corner": 1.25,
        "risk": 0.5,
        "frontier": 0.5,
        "pst": 0.5,
        "discs": 1.5,
    },
}


# Godlike: stronger corners/stability, lower risk, added advanced signals
STRATEGY_GODLIKE = {
    "opening": {
        "mobility": 4.5,
        "corner": 3.5,
        "risk": 1,
        "frontier": 0.5,
        "pst": 2.5,
        "discs": 0.5,
        "potential_mobility": 1,
        "corner_access": 3.0,
        "x_c_penalty": 2.0,
        "stability": 2.0,
        "parity": 0.0,
    },
    "midgame": {
        "mobility": 5.0,
        "corner": 4.0,
        "risk": 1.0,
        "frontier": 1.0,
        "pst": 3.0,
        "discs": 1.0,
        "potential_mobility": 1.0,
        "corner_access": 3.0,
        "x_c_penalty": 2.0,
        "stability": 3.0,
        "parity": 0.0,
    },
    "endgame": {
        "mobility": 1.0,
        "corner": 4.0,
        "risk": 0.5,
        "frontier": 0.5,
        "pst": 1.5,
        "discs": 5.0,
        "potential_mobility": 0.5,
        "corner_access": 1.0,
        "x_c_penalty": 0.5,
        "stability": 5.0,
        "parity": 1.0,
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
        "id": "BETTER_DEFAULT",
        "name": "IA optimisée",
        "description": "Poids optimisés par recherche",
        "weights": STRATEGY_BETTER_DEFAULT,
    },
    {
        "id": "GODLIKE",
        "name": "Godlike",
        "description": "Coins forts, mobilité max, fin de partie discs",
        "weights": STRATEGY_GODLIKE,
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
