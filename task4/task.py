import json


def calculate_membership_value(x_coordinate, membership_points):
    """
    Вычисляет значение функции принадлежности в заданной точке.
    membership_points = [[x1, y1], [x2, y2], ...]
    """
    for i in range(len(membership_points) - 1):
        x1, membership_value1 = membership_points[i]
        x2, membership_value2 = membership_points[i + 1]

        if x1 <= x_coordinate <= x2:
            if x2 == x1:  # Вертикальный отрезок
                return max(membership_value1, membership_value2)
            return membership_value1 + (membership_value2 - membership_value1) * (x_coordinate - x1) / (x2 - x1)

    return 0.0


def main(temperature_sets_json, control_sets_json, rules_json, current_temperature):
    """
    Реализация нечеткого контроллера для управления температурой.
    """
    temperature_sets = json.loads(temperature_sets_json)["температура"]
    control_sets = json.loads(control_sets_json)["температура"]
    inference_rules = json.loads(rules_json)

    # Фаззификация входной температуры
    temperature_membership_values = {}
    for temperature_term in temperature_sets:
        membership_value = calculate_membership_value(current_temperature, temperature_term["points"])
        temperature_membership_values[temperature_term["id"]] = membership_value

    print("Фаззификация температуры:")
    for term_id, membership_value in temperature_membership_values.items():
        print(f"  {term_id}: {membership_value:.4f}")

    # Применение правил нечеткого вывода
    control_membership_values = {control_term["id"]: 0.0 for control_term in control_sets}

    print("\nПрименение правил:")
    for antecedent, consequent in inference_rules:
        activation_strength = temperature_membership_values.get(antecedent, 0.0)
        control_membership_values[consequent] = max(control_membership_values[consequent], activation_strength)
        print(f"  ЕСЛИ {antecedent} → {consequent}: {activation_strength:.4f}")

    # Дефаззификация методом центра тяжести
    x_coordinates = []
    aggregated_membership_values = []

    # Определяем область значений для управления
    min_control_value = min(point[0] for control_term in control_sets for point in control_term["points"])
    max_control_value = max(point[0] for control_term in control_sets for point in control_term["points"])

    sampling_step = 0.1
    current_x = min_control_value
    while current_x <= max_control_value:
        aggregated_membership = 0.0
        for control_term in control_sets:
            term_membership = calculate_membership_value(current_x, control_term["points"])
            aggregated_membership = max(aggregated_membership,
                                       min(term_membership, control_membership_values[control_term["id"]]))
        x_coordinates.append(current_x)
        aggregated_membership_values.append(aggregated_membership)
        current_x += sampling_step

    numerator = sum(x * mu for x, mu in zip(x_coordinates, aggregated_membership_values))
    denominator = sum(aggregated_membership_values)

    control_output = numerator / denominator if denominator != 0 else 0.0

    print("\nДефаззификация:")
    print(f"  Числитель (сумма произведений): {numerator:.4f}")
    print(f"  Знаменатель (сумма значений принадлежности): {denominator:.4f}")
    print(f"  Результирующее управление: {control_output:.4f}")

    return control_output


# Пример использования нечеткого контроллера
temperature_sets_config = json.dumps({
    "температура": [
        {
            "id": "холодно",
            "points": [[0, 1], [18, 1], [22, 0], [50, 0]]
        },
        {
            "id": "комфортно",
            "points": [[18, 0], [22, 1], [24, 1], [26, 0]]
        },
        {
            "id": "жарко",
            "points": [[0, 0], [24, 0], [26, 1], [50, 1]]
        }
    ]
})

control_sets_config = json.dumps({
    "температура": [
        {
            "id": "слабый",
            "points": [[0, 0], [0, 1], [5, 1], [8, 0]]
        },
        {
            "id": "умеренный",
            "points": [[5, 0], [8, 1], [13, 1], [16, 0]]
        },
        {
            "id": "интенсивный",
            "points": [[13, 0], [18, 1], [23, 1], [26, 0]]
        }
    ]
})

inference_rules_config = json.dumps([
    ["холодно", "интенсивный"],
    ["комфортно", "умеренный"],
    ["жарко", "слабый"]
])

current_temperature_value = 20.0

control_result = main(
    temperature_sets_config,
    control_sets_config,
    inference_rules_config,
    current_temperature_value
)

print("\nОптимальное управление:", control_result)
