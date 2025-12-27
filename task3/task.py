import numpy as np


def parse_hierarchy_string(hierarchy_str: str) -> dict:
    """Парсит строку иерархии и возвращает словарь индексов элементов."""
    if hierarchy_str.startswith('[') and hierarchy_str.endswith(']'):
        hierarchy_str = hierarchy_str[1:-1].strip()

    element_to_index = {}
    current_index = 0
    position = 0
    string_length = len(hierarchy_str)

    while position < string_length:
        if hierarchy_str[position] == '[':
            closing_bracket_position = hierarchy_str.find(']', position)
            if closing_bracket_position == -1:
                raise ValueError("Отсутствует закрывающая скобка ']'")
            group_content = hierarchy_str[position+1:closing_bracket_position]
            group_items = [item.strip() for item in group_content.split(',') if item.strip() != ""]
            for element in group_items:
                element_to_index[element] = current_index
            current_index += 1
            position = closing_bracket_position + 1
        elif hierarchy_str[position] == ',' or hierarchy_str[position].isspace():
            position += 1
        else:
            start_position = position
            while position < string_length and hierarchy_str[position] not in ',[':
                position += 1
            element = hierarchy_str[start_position:position].strip()
            if element:
                element_to_index[element] = current_index
                current_index += 1
    return element_to_index


def create_hierarchy_matrix(index_mapping: dict, elements_list: list) -> np.ndarray:
    """Создает матрицу иерархии на основе отображения индексов и списка элементов."""
    elements_count = len(elements_list)
    hierarchy_matrix = np.zeros((elements_count, elements_count), dtype=bool)

    for i in range(elements_count):
        index_i = index_mapping[elements_list[i]]
        for j in range(elements_count):
            index_j = index_mapping[elements_list[j]]
            if index_i <= index_j:
                hierarchy_matrix[i][j] = True

    return hierarchy_matrix


def compare_hierarchies(hierarchy_str1: str, hierarchy_str2: str) -> str:
    """Сравнивает две иерархии и находит противоречия и упорядоченные кластеры."""
    # Извлекаем все элементы из первой строки
    elements = [item.strip(',[]') for item in hierarchy_str1.split(',')]

    # Парсим обе иерархии
    hierarchy1_index_map = parse_hierarchy_string(hierarchy_str1)
    hierarchy2_index_map = parse_hierarchy_string(hierarchy_str2)

    # Создаем матрицы иерархий
    hierarchy_matrix1 = create_hierarchy_matrix(hierarchy1_index_map, elements)
    hierarchy_matrix2 = create_hierarchy_matrix(hierarchy2_index_map, elements)

    # Транспонированные матрицы
    transposed_matrix1 = hierarchy_matrix1.T
    transposed_matrix2 = hierarchy_matrix2.T

    # Пересечение матриц
    intersection_matrix = hierarchy_matrix1 * hierarchy_matrix2
    transposed_intersection_matrix = transposed_matrix1 * transposed_matrix2
    disagreement_matrix = intersection_matrix + transposed_intersection_matrix

    # Находим ядро противоречий
    contradiction_coordinates = list(zip(*np.where(~disagreement_matrix)))
    unique_contradiction_pairs = {tuple(sorted(pair)) for pair in contradiction_coordinates}
    contradiction_pairs = [(elements[i], elements[j])
                           for i, j in unique_contradiction_pairs]

    # Создаем матрицу согласованного порядка
    consistent_matrix = intersection_matrix.copy()

    # Учитываем противоречия (делаем противоречивые элементы сравнимыми)
    for (element_a, element_b) in contradiction_pairs:
        index_a = elements.index(element_a)
        index_b = elements.index(element_b)
        consistent_matrix[index_a, index_b] = True
        consistent_matrix[index_b, index_a] = True

    # Матрица эквивалентности
    equivalence_matrix = consistent_matrix * consistent_matrix.T

    # Транзитивное замыкание матрицы эквивалентности
    elements_count = len(elements)
    transitive_closure = equivalence_matrix.copy()

    for k in range(elements_count):
        for i in range(elements_count):
            for j in range(elements_count):
                transitive_closure[i, j] = (transitive_closure[i, j] or
                                           (transitive_closure[i, k] and transitive_closure[k, j]))

    # Находим кластеры (компоненты связности)
    visited_elements = [False] * elements_count
    clusters = []

    for i in range(elements_count):
        if not visited_elements[i]:
            current_cluster = []
            for j in range(elements_count):
                if transitive_closure[i, j]:
                    current_cluster.append(elements[j])
                    visited_elements[j] = True
            clusters.append(current_cluster)

    # Сортируем кластеры с использованием отношения порядка
    def is_cluster_preceding(cluster1: list, cluster2: list) -> bool:
        """Проверяет, предшествует ли cluster1 cluster2 в согласованном порядке."""
        for element_a in cluster1:
            index_a = elements.index(element_a)
            for element_b in cluster2:
                index_b = elements.index(element_b)
                if consistent_matrix[index_a, index_b] == False:
                    return False
        return True

    # Пузырьковая сортировка кластеров
    has_swapped = True
    while has_swapped:
        has_swapped = False
        for i in range(len(clusters) - 1):
            if is_cluster_preceding(clusters[i+1], clusters[i]):
                clusters[i], clusters[i+1] = clusters[i+1], clusters[i]
                has_swapped = True

    # Форматируем результат
    result = []
    for cluster in clusters:
        if len(cluster) == 1:
            result.append(cluster[0])
        else:
            result.append(cluster)

    result_string = (f"Ядро противоречий: {contradiction_pairs}\n"
                     f"Упорядоченный набор кластеров: {result}")

    return result_string


# Примеры использования
hierarchy1 = '[1,[2,3],4,[5,6,7],8,9,10]'
hierarchy2 = '[[1,2],[3,4,5],6,7,9,[8,10]]'
print(compare_hierarchies(hierarchy1, hierarchy2))

# Дополнительные примеры (закомментированы)
# hierarchy3 = "[x1,[x2,x3],x4,[x5,x6,x7],x8,x9,x10]"
# hierarchy4 = "[x3,[x1,x4],x2,x6,[x5,x7,x8],[x9,x10]]"
# print(compare_hierarchies(hierarchy3, hierarchy4))

# hierarchy5 = '[T,[K,M],D,Z]'
# hierarchy6 = '[[T,K],M,Z,D]'
# print(compare_hierarchies(hierarchy5, hierarchy6))
