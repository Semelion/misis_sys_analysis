# task0/task.py

from __future__ import annotations
import csv
from typing import List, Dict, Union

Number = Union[int, float]

def _maybe_int(x: str) -> Union[int, str]:
    """Преобразует в int, если возможно."""
    try:
        xi = int(x)
        if str(xi) == x.strip():
            return xi
    except ValueError:
        pass
    return x

def adjacency_matrix_from_file(
    filename: str,
    directed: bool = False
) -> List[List[Number]]:
    """
    Построить матрицу смежности из CSV-файла.

    Форматы строк:
      u,v
      u,v,w  (w — вес ребра; если нет, берётся 1)
    """
    edges: list[tuple[Union[int,str], Union[int,str], Number]] = []
    vertices: set[Union[int,str]] = set()

    with open(filename, newline='', encoding='utf-8') as f:
        reader = csv.reader(f)
        for row in reader:
            if not row or row[0].startswith("#"):
                continue
            row = [c.strip() for c in row]
            if len(row) < 2:
                continue

            u = _maybe_int(row[0])
            v = _maybe_int(row[1])

            w: Number = 1
            if len(row) >= 3 and row[2] != "":
                try:
                    w = float(row[2])
                except ValueError:
                    w = 1

            edges.append((u, v, w))
            vertices.add(u); vertices.add(v)

    # Порядок вершин
    nums = sorted([v for v in vertices if isinstance(v, int)])
    strs = sorted([v for v in vertices if isinstance(v, str)])
    ordering = nums + strs
    idx: Dict[Union[int,str], int] = {v: i for i,v in enumerate(ordering)}

    n = len(ordering)
    matrix: List[List[Number]] = [[0 for _ in range(n)] for _ in range(n)]

    # Заполняем
    for u, v, w in edges:
        i, j = idx[u], idx[v]
        val = int(w) if float(w).is_integer() else float(w)
        matrix[i][j] += val
        if not directed:
            matrix[j][i] += val

    return matrix


# --- Пример использования ---
def main():
    """
    Читает путь к CSV-файлу из argv[1] и печатает матрицу смежности.
    """
    import sys
    if len(sys.argv) < 2:
        print("Usage: python task0/task.py <graph.csv>")
        sys.exit(1)

    filename = sys.argv[1]
    matrix = adjacency_matrix_from_file(filename, directed=False)

    for row in matrix:
        print(" ".join(str(x) for x in row))

if __name__ == "__main__":
    main()
