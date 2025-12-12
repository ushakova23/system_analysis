import json
import math

def interpolate(x, points):
# линейная интерполяция
    n = len(points)
    if x <= points[0][0]:
        return points[0][1]
    if x >= points[-1][0]:
        return points[-1][1]
    
    for i in range(n - 1):
        x1, y1 = points[i]
        x2, y2 = points[i + 1]
        if x1 <= x <= x2:
            if x1 == x2:
                return max(y1, y2)
            return y1 + (y2 - y1) * (x - x1) / (x2 - x1)
    return 0.0

def fuzzify(temperature, fuzzy_sets):
# фаззификация
    membership = {}
    for term in fuzzy_sets:
        term_id = term["id"]
        points = term["points"]
        membership[term_id] = interpolate(temperature, points)
    return membership

def rule_activation(temperature_membership, rule_mapping):
# вычисление уровней активации
    activation = {}
    for rule in rule_mapping:
        temp_term, control_term = rule
        # уровень активации = степень принадлежности к входному терму
        activation[control_term] = temperature_membership.get(temp_term, 0.0)
    return activation

def apply_activation(control_term_sets, activation_levels):
    activated_sets = []
    
    for control_term, level in activation_levels.items():
      # находим точки
        points = None
        for term_set in control_term_sets:
            if term_set["id"] == control_term:
                points = term_set["points"]
                break
        
        if points is None:
            continue
        
        activated_points = []
        for x, y in points:
            activated_y = min(level, y)
            activated_points.append([x, activated_y])
        
        activated_sets.append(activated_points)
    
    return activated_sets

def aggregate_sets(activated_sets, x_range=100, step=0.1):
# объединение активированных нечетких множеств
    # создаем дискретные точки для объединения
    x_values = [i * step for i in range(int(x_range / step) + 1)]
    aggregated = []
    
    for x in x_values:
        max_y = 0.0
        for points in activated_sets:
            y = interpolate(x, points)
            max_y = max(max_y, y)
        aggregated.append([x, max_y])
    
    return aggregated

def defuzzify_first_max(aggregated_set, step=0.1):
# дефаззификация
    if not aggregated_set:
        return 0.0

    max_y = max(y for _, y in aggregated_set)

    for x, y in aggregated_set:
        if abs(y - max_y) < 1e-6:  
            return x
    
    return aggregated_set[0][0] 

def main(temperature_json, control_json, rules_json, current_temp):
# функция для вычисления оптимального управления
    temp_data = json.loads(temperature_json)
    control_data = json.loads(control_json)
    rules_data = json.loads(rules_json)

    temp_sets = temp_data.get("температура", [])
    control_sets = control_data.get("температура", [])  
    if not control_sets:
        control_sets = control_data.get("уровень нагрева", [])
    if not control_sets:
        if isinstance(control_data, list):
            control_sets = control_data
        else:
            for key, value in control_data.items():
                if isinstance(value, list):
                    control_sets = value
                    break
    
    # фаззификация
    temperature_membership = fuzzify(current_temp, temp_sets)
    
    # активация правил
    activation_levels = rule_activation(temperature_membership, rules_data)
    
    # применение активации к множествам управления
    activated_sets = apply_activation(control_sets, activation_levels)
    
    # объединение результатов
    aggregated_set = aggregate_sets(activated_sets, x_range=10, step=0.01)
    
    # дефаззификация
    optimal_control = defuzzify_first_max(aggregated_set, step=0.01)
    
    return round(optimal_control, 2)

if __name__ == "__main__":
    temp_json = """
    {
      "температура": [
          {
          "id": "холодно",
          "points": [
              [0,1],
              [18,1],
              [22,0],
              [50,0]
          ]
          },
          {
          "id": "комфортно",
          "points": [
              [18,0],
              [22,1],
              [24,1],
              [26,0]
          ]
          },
          {
          "id": "жарко",
          "points": [
              [0,0],
              [24,0],
              [26,1],
              [50,1]
          ]
          }
      ]
    }
    """
    
    control_json = """
    {
      "температура": [
          {
            "id": "слабый",
            "points": [
                [0,0],
                [0,1],
                [5,1],
                [8,0]
            ]
          },
          {
            "id": "умеренный",
            "points": [
                [5,0],
                [8,1],
                [13,1],
                [16,0]
            ]
          },
          {
            "id": "интенсивный",
            "points": [
                [13,0],
                [18,1],
                [23,1],
                [26,0]
            ]
          }
      ]
    }
    """
    
    rules_json = """
    [
        ["холодно", "интенсивный"],
        ["комфортно", "умеренный"],
        ["жарко", "слабый"]
    ]
    """
    
    test_temps = [15, 20, 25, 30]
    for temp in test_temps:
        result = main(temp_json, control_json, rules_json, temp)
        print(f"Температура: {temp}°C -> Оптимальное управление: {result}")
