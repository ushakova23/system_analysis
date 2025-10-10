from typing import List, Tuple, Dict, Set
import pandas as pd
import numpy as np
from google.colab import files

def main(s: str, e: str) -> Tuple[
    List[List[bool]],
    List[List[bool]],
    List[List[bool]],
    List[List[bool]],
    List[List[bool]]
]:
    #парсим входную строку
    edges = []
    lines = s.strip().split('\n')
    for line in lines:
        if line:
            u, v = line.split(',')
            edges.append((u, v))

    #узлы
    nodes = set()
    for u, v in edges:
        nodes.add(u)
        nodes.add(v)

    #узлы в список
    node_list = sorted(nodes)
    node_index = {node: idx for idx, node in enumerate(node_list)}
    n = len(node_list)

    #матрицы
    A1 = [[False] * n for _ in range(n)] 
    A2 = [[False] * n for _ in range(n)]  
    A3 = [[False] * n for _ in range(n)] 
    A4 = [[False] * n for _ in range(n)]  
    A5 = [[False] * n for _ in range(n)]  

    #граф
    graph = {node: [] for node in node_list}
    for u, v in edges:
        graph[u].append(v)

    #поиск потомков узла
    def find_descendants(node: str, visited: Set[str] = None) -> Set[str]:
        if visited is None:
            visited = set()
        visited.add(node)
        for child in graph.get(node, []):
            if child not in visited:
                find_descendants(child, visited)
        return visited

    #поиск предков узла
    def find_ancestors(node: str) -> Set[str]:
        #обратный граф
        reverse_graph = {n: [] for n in node_list}
        for u, v in edges:
            reverse_graph[v].append(u)

        visited = set()
        stack = [node]
        while stack:
            current = stack.pop()
            if current not in visited:
                visited.add(current)
                for parent in reverse_graph.get(current, []):
                    if parent not in visited:
                        stack.append(parent)
        return visited

    #поиск глубины узла
    def find_depth(node: str) -> int:
        if node == e:  
            return 0
        depth = 0
        current = node
        visited = set()
        while current != e and current not in visited:
            visited.add(current)
            parents = find_ancestors(current) - {current}
            if not parents:
                break
            #берём родителя
            current = next(iter(parents))
            depth += 1
            if depth > n:  
                break
        return depth

    #матрицы отношений (заполняем согласно набору отношений в пояснении к заданию)
    for i, node_i in enumerate(node_list):
        for j, node_j in enumerate(node_list):
            if (node_i, node_j) in edges:
                A1[i][j] = True

            descendants_i = find_descendants(node_i)
            if node_j in descendants_i:
                A2[i][j] = True

            parents_i = find_ancestors(node_i) - {node_i} 
            parents_j = find_ancestors(node_j) - {node_j}
            common_parents = parents_i.intersection(parents_j)
            if common_parents:
                A3[i][j] = True

            if i != j and Q[i][j]:
                A4[i][j] = True

            depth_i = find_depth(node_i)
            depth_j = find_depth(node_j)
            if depth_i == depth_j:
                A5[i][j] = True

    return A1, A2, A3, A4, A5

if __name__ == "__main__":

    with open('task2.csv', 'r') as file:
            csv_data = file.read()

    root = "1"  

    A1, A2, A3, A4, A5 = main(csv_data, root)

    #список узлов
    nodes = set()
    lines = csv_data.strip().split('\n')
    for line in lines:
        if line:
            u, v = line.split(',')
            nodes.add(u)
            nodes.add(v)
    node_list = sorted(nodes)

    print("A1")
    for row in A1:
        print([1 if x else 0 for x in row])

    print("A2")
    for row in A2:
        print([1 if x else 0 for x in row])

    print("A3")
    for row in A3:
        print([1 if x else 0 for x in row])

    print("A4")
    for row in A4:
        print([1 if x else 0 for x in row])

    print("A5")
    for row in A5:
        print([1 if x else 0 for x in row])
