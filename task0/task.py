import pandas as pd
import numpy as np

df = pd.read_csv('task2.csv')

nodes = sorted(set(df.iloc[:, 0]) | set(df.iloc[:, 1]))
node_to_index = {node: i for i, node in enumerate(nodes)}

adjacency_matrix = pd.crosstab(df.iloc[:, 0], df.iloc[:, 1]).reindex(index=nodes, columns=nodes).fillna(0)
adjacency_matrix = adjacency_matrix + adjacency_matrix.T
adjacency_matrix = np.where(adjacency_matrix > 0, 1, 0).astype(int)

print(adjacency_matrix)
