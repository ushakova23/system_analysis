from typing import List, Tuple, Dict, Set
import math

def main(s: str, e: str) -> Tuple[float, float]:
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
            current = next(iter(parents))
            depth += 1
            if depth > n:
                break
        return depth
    
    #определение отношений согласно заданию
    r1 = set()  #непосредственное управление
    r2 = set()  #непосредственное подчинение  
    r3 = set()  #опосредованное управление
    r4 = set()  #опосредованное подчинение
    r5 = set()  #сотрудничество на одном уровне
    
    #отношения r1 и r2
    for u, v in edges:
        r1.add((u, v))
        r2.add((v, u))
    
    #отношения r3 и r4
    for i, node_i in enumerate(node_list):
        descendants = find_descendants(node_i)
        for node_j in descendants:
            if (node_i, node_j) not in r1:  
                r3.add((node_i, node_j))
        
        ancestors = find_ancestors(node_i)
        for node_j in ancestors:
            if (node_i, node_j) not in r2: 
                r4.add((node_i, node_j))
    
    #отношение r5
    for i, node_i in enumerate(node_list):
        depth_i = find_depth(node_i)
        for j, node_j in enumerate(node_list):
            if i != j:
                depth_j = find_depth(node_j)
                if depth_i == depth_j:
                    r5.add((node_i, node_j))
    
    #расчет количества исходящих связей для каждого элемента
    l_matrix = {node: [0, 0, 0, 0, 0] for node in node_list}  
    
    for node in node_list:
        l_matrix[node][0] = sum(1 for u, v in r1 if u == node)
         
        l_matrix[node][1] = sum(1 for u, v in r2 if u == node)
        
        l_matrix[node][2] = sum(1 for u, v in r3 if u == node)
        
        l_matrix[node][3] = sum(1 for u, v in r4 if u == node)
        
        l_matrix[node][4] = sum(1 for u, v in r5 if u == node)
    
    #расчет энтропии
    max_connections = n - 1  #максимальное число уникальных связей
    total_entropy = 0.0
    
    for node in node_list:
        node_entropy = 0.0
        for rel_idx in range(5):
            l_ij = l_matrix[node][rel_idx]
            if l_ij > 0:
                p = l_ij / max_connections
                H = -p * math.log2(p)
                node_entropy += H
        total_entropy += node_entropy
    
    #нормализация
    c = 1 / (math.e * math.log(2))  
    k = 5  #количество типов отношений
    H_ref = c * n * k

    normalized_complexity = total_entropy / H_ref
    
    total_entropy = round(total_entropy, 1)
    normalized_complexity = round(normalized_complexity, 1)
    
    return total_entropy, normalized_complexity

if __name__ == "__main__":

    with open('task2.csv', 'r') as file:
            csv_data = file.read()
    
    root = "1" 
    
    entropy, complexity = main(csv_data, root)
    
    print(f"энтропия: {entropy}")
    print(f"нормированная оценка структурной сложности: {complexity}")
