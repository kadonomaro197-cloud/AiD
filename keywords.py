# keywords.py

# Expanded Keywords for selecting relevant RAG datasets
CATEGORY_KEYWORDS = {
    "astronomy": [
        "astronomy", "stars", "planet", "cosmos", "universe",
        "galaxy", "nebula", "black hole", "supernova", "solar", "lunar",
        "orbit", "comet", "asteroid", "exoplanet", "telescope",
        "pulsar", "quasar", "meteor", "dark matter", "dark energy",
        "space", "interstellar", "intergalactic", "stellar", "light-year",
        "cosmology", "big bang", "gravity well", "event horizon", "redshift",
        "planetary system", "celestial", "observatory", "cosmic radiation"
    ],
    "physics": [
        "physics", "energy", "force", "quantum", "relativity",
        "motion", "gravity", "particle", "wave", "mechanics",
        "thermodynamics", "electromagnetic", "nuclear", "atomic",
        "field", "potential", "kinetic", "momentum", "spin", "boson",
        "fermion", "photon", "entanglement", "uncertainty", "superposition",
        "string theory", "quantum tunneling", "acceleration", "inertia"
    ],
    "materials": [
        "material", "metal", "alloy", "crystal", "atomic",
        "semiconductor", "ceramic", "polymer", "nanomaterial",
        "conductivity", "hardness", "density", "elasticity",
        "tensile", "strength", "fatigue", "corrosion", "magnetism",
        "superconductor", "composite", "amorphous", "microstructure",
        "grain boundary", "thermal expansion", "lattice", "phase transition"
    ],
    "politics": [
        "politics", "government", "policy", "election", "democracy",
        "dictatorship", "monarchy", "republic", "parliament", "senate",
        "congress", "constitution", "law", "legislation", "rights",
        "civil rights", "liberty", "justice", "authority", "power",
        "corruption", "diplomacy", "foreign policy", "domestic policy",
        "campaign", "ideology", "political party", "propaganda",
        "sovereignty", "citizenship", "voting", "representation"
    ],
    "warfare": [
        "warfare", "war", "battle", "conflict", "army",
        "military", "navy", "air force", "soldier", "troop",
        "strategy", "tactics", "weapon", "armor", "fortification",
        "siege", "artillery", "infantry", "cavalry", "guerrilla",
        "insurgency", "rebellion", "revolution", "occupation",
        "peace treaty", "armistice", "genocide", "nuclear weapon",
        "missile", "espionage", "intelligence", "special forces",
        "logistics", "supply lines", "alliance", "militarization"
    ],
    "psychology": [
        "psychology", "mind", "behavior", "cognition", "emotion",
        "memory", "perception", "consciousness", "subconscious",
        "learning", "motivation", "stress", "personality", "intelligence",
        "developmental", "therapy", "counseling", "mental health",
        "depression", "anxiety", "psychopathology", "disorder",
        "neuroscience", "brain", "cognitive science", "conditioning",
        "bias", "heuristic", "dream", "trauma", "social psychology"
    ],
    "philosophy": [
        "philosophy", "ethics", "morality", "logic", "reason",
        "metaphysics", "ontology", "epistemology", "existentialism",
        "stoicism", "nihilism", "idealism", "realism", "dualism",
        "determinism", "free will", "aesthetics", "virtue",
        "utilitarianism", "deontology", "rationalism", "empiricism",
        "knowledge", "truth", "wisdom", "meaning of life",
        "consciousness", "self", "mind-body", "paradox", "philosopher"
    ]
}

def get_categories_for_query(user_query):
    """
    Returns a list of categories to query based on the user_query.
    """
    query_lower = user_query.lower()
    matched_categories = []

    for category, keywords in CATEGORY_KEYWORDS.items():
        if any(word in query_lower for word in keywords):
            matched_categories.append(category)

    # Default to all if no match
    if not matched_categories:
        matched_categories = list(CATEGORY_KEYWORDS.keys())

    return matched_categories
