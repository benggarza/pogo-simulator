def get_effectiveness(attack_type, defender_types):
    effectiveness = 1.0
    for defender_type in defender_types:
        effectiveness *= effect_table[attack_type][defender_type]
    return effectiveness