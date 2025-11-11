import json
import re

def fix_json(json_str):
    #обработка исходных файлов от лишних запятых и тд
    json_str = json_str.strip()

    json_str = re.sub(r',\s*]', ']', json_str)
    json_str = re.sub(r',\s*}', '}', json_str)

    while ',,' in json_str:
        json_str = json_str.replace(',,', ',')
    
    return json.loads(json_str)

def main(ranking_a_str, ranking_b_str):
    #парсим ранжировки
    a = fix_json(ranking_a_str)
    b = fix_json(ranking_b_str)
    
    #получаем все элементы
    elements = []
    for ranking in [a, b]:
        for item in ranking:
            if isinstance(item, list):
                elements.extend(item)
            else:
                elements.append(item)
    
    elements = sorted(set(elements))
    
    #получаем позицию элемента
    def get_position(ranking, elem):
        for i, group in enumerate(ranking):
            if isinstance(group, list):
                if elem in group:
                    return i
            elif elem == group:
                return i
        return -1
    
    #ищем противоречия
    contradictions = []
    
    for i in range(len(elements)):
        for j in range(i + 1, len(elements)):
            elem1, elem2 = elements[i], elements[j]
            
            pos1_a = get_position(a, elem1)
            pos2_a = get_position(a, elem2)
            pos1_b = get_position(b, elem1)  
            pos2_b = get_position(b, elem2)
            
            #проверяем противоречие
            if (pos1_a < pos2_a and pos1_b > pos2_b) or (pos1_a > pos2_a and pos1_b < pos2_b):
                contradictions.append([str(elem1), str(elem2)])
    
    return json.dumps(contradictions)

if __name__ == "__main__":
    with open('Ранжировка  A.json', 'r', encoding='utf-8') as f:
        a_str = f.read()
    
    with open('Ранжировка  B.json', 'r', encoding='utf-8') as f:
        b_str = f.read()
    
    result = main(a_str, b_str)
    print(result)
