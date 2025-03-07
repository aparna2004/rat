import numpy as np
import matplotlib.pyplot as plt

FUZZY_SETS = {
    "NL": [0, 0, 31, 61], "NM": [31, 61, 95], "NS": [61, 95, 127], "ZE": [95, 127, 159],
    "PS": [127, 159, 191], "PM": [159, 191, 223], "PL": [191, 223, 255, 255]
}
RULES = {
    1: ["NL", "ZE", "PL"], 2: ["ZE", "NL", "PL"], 3: ["NM", "ZE", "PM"], 4: ["NS", "PS", "PS"],
    5: ["PS", "NS", "NS"], 6: ["PL", "ZE", "NL"], 7: ["ZE", "NS", "PS"], 8: ["ZE", "NM", "PM"]
}
def triangular(x, a, b, c):
    if a < x < b:
        return (x - a) / (b - a)
    if b <= x < c:
        return  (c - x) / (c - b)
    return 0

def trapezoidal(x, a, b, c, d):
    if a < x < b:
        return (x - a) / (b - a)
    if b <= x <= c:
        return 1
    if c < x < d:
        return  (d - x) / (d - c)
    return 0
  
def get_membership(x, fuzzy_sets):
    return trapezoidal(x, *fuzzy_sets) if len(fuzzy_sets) == 4 else triangular(x, *fuzzy_sets)

def fuzzify(value, sets):
    fuzzy_values = {}
    for key, fuzzy_set in sets.items():
        fuzzy_values[key] = get_membership(value, fuzzy_set)
    return fuzzy_values

def apply_rules(speed_fuzzy, accel_fuzzy):
    rules_strength = {}

    for i, (speed, accel, output) in RULES.items():
        strength = min(speed_fuzzy.get(speed, 0), accel_fuzzy.get(accel, 0))
        if strength > 0:
            rules_strength[i] = strength, output

    return rules_strength

def calculate_areas(rules_strengths):
    areas = {}
    weighted_areas = {}

    for i, (height, output) in rules_strengths.items():
        set_vals = FUZZY_SETS[output]
        centroid = (set_vals[1] if len(set_vals) == 3 else (set_vals[1] + set_vals[2])/2) 

        base = 0
        if len(set_vals) == 4:
            base1 = set_vals[0] - set_vals[3]
            base2 = set_vals[2] - set_vals[1]
            base = base1 + base2
        if len(set_vals) == 3:
            base = set_vals[2] - set_vals[0]
        
        areas[i] = (height * base) / 2
        weighted_areas[i] = centroid * areas[i]

    return areas, weighted_areas

def defuzzify(areas, weighted_areas):
    return sum(weighted_areas.values()) / sum(areas.values())

speed = 100
acceleration = 70

speed_fuzzy = fuzzify(speed, FUZZY_SETS)
accel_fuzzy = fuzzify(acceleration, FUZZY_SETS)

rules_strengths = apply_rules(speed_fuzzy, accel_fuzzy)

areas, weighted_areas = calculate_areas(rules_strengths)
throttle = defuzzify(areas, weighted_areas)

print(f"Output: {throttle:.2f}")

def plot(sets, title, highlight_x=None):
    plt.figure(figsize=(8,4))
    x_vals = np.linspace(0, 255, 500)

    for label, params in sets.items():
        y_vals = [get_membership(x, params) for x in x_vals]
        plt.plot(x_vals, y_vals, label=label)

    if highlight_x is not None:
        plt.axvline(x=highlight_x, color="red", linestyle="--", label=f"Output: {highlight_x:.2f}")

    plt.title(title)
    plt.xlabel("Value")
    plt.ylabel("Membership")
    plt.legend()
    plt.grid(True)
    plt.show()

plot(FUZZY_SETS, "Speed Fuzzy Sets")
plot(FUZZY_SETS, "Acceleration Fuzzy Sets")
plot(FUZZY_SETS, "Throttle Output Fuzzy Sets", throttle)

