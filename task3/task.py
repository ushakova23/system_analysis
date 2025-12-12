# добавить кластерную ранжировку
import json
import re
import numpy as np

def fix_json(json_str):
    # обработка исходных файлов от лишних запятых и тд
    json_str = json_str.strip()
    json_str = re.sub(r',\s*]', ']', json_str)
    json_str = re.sub(r',\s*}', '}', json_str)
    
    while ',,' in json_str:
        json_str = json_str.replace(',,', ',')
    
    return json.loads(json_str)

def ranking_to_matrix(ranking, elements):
    n = len(elements)
    matrix = np.zeros((n, n), dtype=int)
    
    # позиции элементов
    positions = {}
    for pos, group in enumerate(ranking):
        if isinstance(group, list):
            for elem in group:
                positions[elem] = pos
        else:
            positions[group] = pos
    
    # заполняем матрицу
    for i in range(n):
        for j in range(n):
            elem_i = elements[i]
            elem_j = elements[j]
            
            pos_i = positions.get(elem_i, -1)
            pos_j = positions.get(elem_j, -1)
            
            if pos_i <= pos_j:
                matrix[i][j] = 1
    
    return matrix

def find_contradictions(a, b):
    # находим ядро противоречий между двумя ранжировками
    # получаем все элементы
    elements = []
    for ranking in [a, b]:
        for item in ranking:
            if isinstance(item, list):
                elements.extend(item)
            else:
                elements.append(item)
    
    elements = sorted(set(elements))
    
    # получаем позицию элемента
    def get_position(ranking, elem):
        for i, group in enumerate(ranking):
            if isinstance(group, list):
                if elem in group:
                    return i
            elif elem == group:
                return i
        return -1
    
    # ищем противоречия
    contradictions = []
    
    for i in range(len(elements)):
        for j in range(i + 1, len(elements)):
            elem1, elem2 = elements[i], elements[j]
            
            pos1_a = get_position(a, elem1)
            pos2_a = get_position(a, elem2)
            pos1_b = get_position(b, elem1)  
            pos2_b = get_position(b, elem2)
            
            # проверяем противоречие
            if (pos1_a < pos2_a and pos1_b > pos2_b) or (pos1_a > pos2_a and pos1_b < pos2_b):
                contradictions.append([str(elem1), str(elem2)])
    
    return contradictions

def build_consistent_ranking(a, b):
    # строим согласованную кластерную ранжировку
    # Получаем все элементы
    elements = []
    for ranking in [a, b]:
        for item in ranking:
            if isinstance(item, list):
                elements.extend(item)
            else:
                elements.append(item)
    
    elements = sorted(set(elements))
    n = len(elements)
    
    # строим матрицы отношений
    Y_A = ranking_to_matrix(a, elements)
    Y_B = ranking_to_matrix(b, elements)
    
    # транспонированные матрицы
    Y_A_T = Y_A.T
    Y_B_T = Y_B.T
    
    # матрица противоречий
    P = np.logical_or(np.logical_and(Y_A, Y_B_T), np.logical_and(Y_A_T, Y_B)).astype(int)
    
    # ядро противоречий
    contradiction_pairs = []
    for i in range(n):
        for j in range(i + 1, n):
            if P[i, j] == 0:
                contradiction_pairs.append((elements[i], elements[j]))
    
    # матрица согласованного порядка
    C = np.logical_and(Y_A, Y_B).astype(int)
    
    # учет противоречий
    for elem1, elem2 in contradiction_pairs:
        i = elements.index(elem1)
        j = elements.index(elem2)
        C[i, j] = 1
        C[j, i] = 1
    
    # матрица эквивалентности
    E = np.logical_and(C, C.T).astype(int)
    
    # алгоритм Уоршелла
    E_star = E.copy()
    for k in range(n):
        for i in range(n):
            for j in range(n):
                if E_star[i, k] and E_star[k, j]:
                    E_star[i, j] = 1
    
    # выделение кластеров
    clusters = []
    visited = set()
    
    for i in range(n):
        if i not in visited:
            cluster = []
            for j in range(n):
                if E_star[i, j] == 1:
                    cluster.append(elements[j])
                    visited.add(j)
            clusters.append(sorted(cluster))
    
    # упорядочивание кластеров
    cluster_order = []
    remaining_clusters = clusters.copy()
    
    while remaining_clusters:
        # находим минимальный кластер
        for cluster in remaining_clusters:
            is_minimal = True
            rep_elem = cluster[0] 
            
            for other_cluster in remaining_clusters:
                if cluster == other_cluster:
                    continue
                    
                other_rep = other_cluster[0]
                rep_idx = elements.index(rep_elem)
                other_idx = elements.index(other_rep)

                if C[other_idx, rep_idx] == 1 and C[rep_idx, other_idx] == 0:
                    is_minimal = False
                    break
            
            if is_minimal:
                cluster_order.append(cluster)
                remaining_clusters.remove(cluster)
                break

    result = []
    for cluster in cluster_order:
        if len(cluster) == 1:
            result.append(cluster[0])
        else:
            result.append(cluster)
    
    return result

def main(ranking_a_str, ranking_b_str, output_type="contradictions"):

    # парсим ранжировки
    a = fix_json(ranking_a_str)
    b = fix_json(ranking_b_str)
    
    if output_type == "contradictions":
        # ядро противоречий
        contradictions = find_contradictions(a, b)
        return json.dumps(contradictions)
    
    elif output_type == "ranking":
        # согласованная кластерная ранжировка
        consistent_ranking = build_consistent_ranking(a, b)
        return json.dumps(consistent_ranking)

if __name__ == "__main__":
    with open('Ранжировка  A.json', 'r', encoding='utf-8') as f:
        a_str = f.read()
    
    with open('Ранжировка  B.json', 'r', encoding='utf-8') as f:
        b_str = f.read()

    contradictions = main(a_str, b_str, "contradictions")
    print("ядро противоречий:", contradictions)

    consistent_ranking = main(a_str, b_str, "ranking")
    print("согласованная ранжировка:", consistent_ranking)
