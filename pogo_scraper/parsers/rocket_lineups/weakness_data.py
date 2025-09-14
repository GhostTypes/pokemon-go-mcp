"""
Handles parsing rocket weakness information
"""

from typing import List

def calculate_weakness_effectiveness(attacking_type: str, defending_types: List[str]) -> float:
    """
    Calculate type effectiveness multiplier based on Pokemon type chart
    Returns: 2.0 for super effective, 1.0 for normal, 0.5 for not very effective, 0.0 for no effect
    """
    # Pokemon Go type effectiveness chart
    TYPE_CHART = {
        'normal': {
            'weak_to': ['fighting'],
            'resists': [],
            'immune_to': ['ghost']
        },
        'fire': {
            'weak_to': ['water', 'ground', 'rock'],
            'resists': ['fire', 'grass', 'ice', 'bug', 'steel', 'fairy'],
            'immune_to': []
        },
        'water': {
            'weak_to': ['grass', 'electric'],
            'resists': ['fire', 'water', 'ice', 'steel'],
            'immune_to': []
        },
        'grass': {
            'weak_to': ['fire', 'ice', 'poison', 'flying', 'bug'],
            'resists': ['water', 'electric', 'grass', 'ground'],
            'immune_to': []
        },
        'electric': {
            'weak_to': ['ground'],
            'resists': ['flying', 'steel', 'electric'],
            'immune_to': []
        },
        'ice': {
            'weak_to': ['fire', 'fighting', 'rock', 'steel'],
            'resists': ['ice'],
            'immune_to': []
        },
        'fighting': {
            'weak_to': ['flying', 'psychic', 'fairy'],
            'resists': ['rock', 'bug', 'dark'],
            'immune_to': []
        },
        'poison': {
            'weak_to': ['ground', 'psychic'],
            'resists': ['grass', 'fighting', 'poison', 'bug', 'fairy'],
            'immune_to': []
        },
        'ground': {
            'weak_to': ['water', 'grass', 'ice'],
            'resists': ['poison', 'rock'],
            'immune_to': ['electric']
        },
        'flying': {
            'weak_to': ['electric', 'ice', 'rock'],
            'resists': ['grass', 'fighting', 'bug'],
            'immune_to': ['ground']
        },
        'psychic': {
            'weak_to': ['bug', 'ghost', 'dark'],
            'resists': ['fighting', 'psychic'],
            'immune_to': []
        },
        'bug': {
            'weak_to': ['fire', 'flying', 'rock'],
            'resists': ['grass', 'fighting', 'ground'],
            'immune_to': []
        },
        'rock': {
            'weak_to': ['water', 'grass', 'fighting', 'ground', 'steel'],
            'resists': ['normal', 'fire', 'poison', 'flying'],
            'immune_to': []
        },
        'ghost': {
            'weak_to': ['ghost', 'dark'],
            'resists': ['poison', 'bug'],
            'immune_to': ['normal', 'fighting']
        },
        'dragon': {
            'weak_to': ['ice', 'dragon', 'fairy'],
            'resists': ['fire', 'water', 'electric', 'grass'],
            'immune_to': []
        },
        'dark': {
            'weak_to': ['fighting', 'bug', 'fairy'],
            'resists': ['ghost', 'dark'],
            'immune_to': ['psychic']
        },
        'steel': {
            'weak_to': ['fire', 'fighting', 'ground'],
            'resists': ['normal', 'grass', 'ice', 'flying', 'psychic', 'bug', 'rock', 'dragon', 'steel', 'fairy'],
            'immune_to': ['poison']
        },
        'fairy': {
            'weak_to': ['poison', 'steel'],
            'resists': ['fighting', 'bug', 'dark'],
            'immune_to': ['dragon']
        }
    }

    attacking_type = attacking_type.lower()
    effectiveness = 1.0

    for defending_type in defending_types:
        defending_type = defending_type.lower()

        if defending_type not in TYPE_CHART:
            continue

        type_data = TYPE_CHART[defending_type]

        # Check immunities (0x damage)
        if attacking_type in type_data['immune_to']:
            return 0.0

        # Check weaknesses (2x damage)
        elif attacking_type in type_data['weak_to']:
            effectiveness *= 2.0

        # Check resistances (0.5x damage)
        elif attacking_type in type_data['resists']:
            effectiveness *= 0.5

    return effectiveness