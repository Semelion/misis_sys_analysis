import numpy as np
from collections import defaultdict

def find_paths(adjacency_list, start_node, visited_nodes=None, current_path=None):
    if visited_nodes is None: visited_nodes = []
    if current_path is None: current_path = [start_node]

    visited_nodes.append(start_node)

    all_paths = []
    for neighbor in adjacency_list[start_node]:
        if neighbor not in visited_nodes:
            extended_path = current_path + [neighbor]
            all_paths.append(tuple(extended_path))
            all_paths.extend(find_paths(adjacency_list, neighbor, visited_nodes[:], extended_path))

    return all_paths

def main(input_string: str) -> tuple[list[list[bool]], list[list[bool]], list[list[bool]], list[list[bool]], list[list[bool]]]:
    edges = [line.split(',') for line in input_string.split('\n')]

    # Построение списка смежности
    adjacency_list = defaultdict(list)
    for (source, target) in edges:
        adjacency_list[source].append(target)

    # Сбор всех уникальных вершин
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
    temp_matrix = np.dot(direct_control, direct_control)

    # Определение максимальной длины пути
    all_paths = find_paths(adjacency_list, edges[0][0])
    max_path_length = max(len(path) for path in all_paths) if all_paths else 0

    for _ in range(max(0, max_path_length - 2)):
        indirect_control[np.logical_or(indirect_control, temp_matrix)] = 1
        temp_matrix = np.dot(temp_matrix, direct_control)

    # Матрица опосредованного подчинения
    indirect_subordination = indirect_control.T

    # Матрица соподчинения на одном уровне
    same_level_coordination = np.zeros((vertex_count, vertex_count), bool)

    for parent_vertex in adjacency_list:
        children = adjacency_list[parent_vertex]
        children_count = len(children)
        if children_count > 1:
            for i in range(children_count):
                first_idx = vertex_to_index[children[i]]
                for second_child in children[i+1:]:
                    second_idx = vertex_to_index[second_child]
                    same_level_coordination[first_idx][second_idx] = 1

    # Симметризуем матрицу соподчинения
    same_level_coordination[np.logical_or(same_level_coordination, same_level_coordination.T)] = 1

    return (
        direct_control.tolist(),
        direct_subordination.tolist(),
        indirect_control.tolist(),
        indirect_subordination.tolist(),
        same_level_coordination.tolist()
    )

# Тестовые данные
test_data_1 = "1,2\n1,3\n3,4\n3,5"
test_data_2 = "1,2\n1,3\n3,4\n3,5\n5,6\n6,7"
test_data_3 = "2,3\n2,1\n1,8\n1,5"
test_data_4 = "0,1\n0,2\n0,3\n0,4\n1,5\n1,6"

print(main(test_data_1))
