from math import e, log2
import numpy as np
from collections import defaultdict

def find_all_paths(adjacency_list, start_node, visited_nodes=None, current_path=None):
    if visited_nodes is None: visited_nodes = []
    if current_path is None: current_path = [start_node]

    visited_nodes.append(start_node)

    all_paths = []
    for neighbor in adjacency_list[start_node]:
        if neighbor not in visited_nodes:
            extended_path = current_path + [neighbor]
            all_paths.append(tuple(extended_path))
            all_paths.extend(find_all_paths(adjacency_list, neighbor, visited_nodes[:], extended_path))

    return all_paths

def calculate_relation_matrices(input_string: str) -> tuple[list[list[bool]], list[list[bool]], list[list[bool]], list[list[bool]], list[list[bool]]]:
    edges = [line.split(',') for line in input_string.split('\n')]

    # Построение списка смежности
    adjacency_list = defaultdict(list)
    for (source, target) in edges:
        adjacency_list[source].append(target)

    vertices = []
    for source, target in edges:
        if source not in vertices:
            vertices.append(source)
        if target not in vertices:
            vertices.append(target)

    vertex_to_index = {vertex: idx for idx, vertex in enumerate(vertices)}

    vertex_count = len(vertices)

    # Матрица непосредственного управления
    direct_control = np.zeros((vertex_count, vertex_count), bool)

    for source_vertex in adjacency_list:
        source_idx = vertex_to_index[source_vertex]
        for target_vertex in adjacency_list[source_vertex]:
            direct_control[source_idx][vertex_to_index[target_vertex]] = 1

    # Матрица непосредственного подчинения
    direct_subordination = direct_control.T

    # Матрица опосредованного управления
    indirect_control = np.zeros((vertex_count, vertex_count), bool)
    power_matrix = np.dot(direct_control, direct_control)

    # Находим максимальную длину пути для определения количества итераций
    all_paths = find_all_paths(adjacency_list, edges[0][0])
    max_path_length = max(len(path) for path in all_paths) if all_paths else 0

    for _ in range(max(0, max_path_length - 2)):
        indirect_control[np.logical_or(indirect_control, power_matrix)] = 1
        power_matrix = np.dot(power_matrix, direct_control)

    # Матрица опосредованного подчинения
    indirect_subordination = indirect_control.T

    # Матрица соподчинения на одном уровне
    same_level_coordination = np.zeros((vertex_count, vertex_count), bool)

    for parent_vertex in adjacency_list:
        children = adjacency_list[parent_vertex]
        children_count = len(children)
        if children_count > 1:
            for i in range(children_count):
                first_child_idx = vertex_to_index[children[i]]
                for second_child in children[i+1:]:
                    second_child_idx = vertex_to_index[second_child]
                    same_level_coordination[first_child_idx][second_child_idx] = 1

    # Делаем матрицу симметричной (если A соподчинен с B, то и B соподчинен с A)
    same_level_coordination[np.logical_or(same_level_coordination, same_level_coordination.T)] = 1

    return (
        direct_control.tolist(),
        direct_subordination.tolist(),
        indirect_control.tolist(),
        indirect_subordination.tolist(),
        same_level_coordination.tolist()
    )

def calculate_entropy(probability: float) -> float:
    if probability != 0:
        entropy_value = -probability * log2(probability)
        return entropy_value
    return 0.0

def main(input_string: str) -> tuple[float, float]:
    relation_matrices = calculate_relation_matrices(input_string)
    relation_types_count = 5
    vertex_count = len(relation_matrices[0])

    # Матрица для подсчета количества исходящих связей для каждой вершины и каждого типа отношений
    outgoing_connections_count = np.zeros((vertex_count, relation_types_count), int)

    for relation_idx, matrix in enumerate(relation_matrices):
        for vertex_idx in range(vertex_count):
            outgoing_connections_count[vertex_idx][relation_idx] = sum(matrix[vertex_idx])

    # Вычисляем суммарную энтропию
    total_entropy = 0.0
    for vertex_idx in range(vertex_count):
        row_sum = sum(outgoing_connections_count[vertex_idx])
        if row_sum > 0:
            for relation_idx in range(relation_types_count):
                probability = outgoing_connections_count[vertex_idx][relation_idx] / row_sum
                total_entropy += calculate_entropy(probability)

    # Вычисляем максимальную энтропию (эталонную)
    max_entropy_per_element = -1/e * log2(1/e)
    reference_entropy = max_entropy_per_element * vertex_count * relation_types_count

    # Нормированная энтропия
    normalized_entropy = total_entropy / reference_entropy
    print(reference_entropy)
    result = (round(total_entropy, 1), round(normalized_entropy, 1))
    return result

# Тестовые данные
test_data_1 = "1,2\n1,3\n3,4\n3,5"
test_data_2 = "1,2\n2,3\n2,4\n4,5\n4,6"

print(main(test_data_2))
