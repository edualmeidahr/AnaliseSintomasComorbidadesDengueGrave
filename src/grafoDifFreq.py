import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt

# Carregar a base de dados (substitua o caminho pelo correto)
df = pd.read_csv('datas/sinan_dengue_filtrada.csv')

# Filtrar os casos de dengue e dengue grave
casos_dengue = df[df['CLASSI_FIN'] == 10]
casos_graves = df[df['CLASSI_FIN'] == 12]

# Definir as colunas de sintomas (ajuste se necessário)
sintomas_cols = ['FEBRE', 'MIALGIA', 'CEFALEIA', 'EXANTEMA', 'VOMITO', 'NAUSEA',
                 'DOR_COSTAS', 'CONJUNTVIT', 'ARTRITE', 'ARTRALGIA', 'PETEQUIA_N',
                 'LEUCOPENIA', 'LACO', 'DOR_RETRO', 'DIABETES', 'HEMATOLOG', 'HEPATOPAT',
                 'RENAL', 'HIPERTENSA', 'ACIDO_PEPT', 'AUTO_IMUNE']

# Garantir que as colunas sejam numéricas (1/2 para Sim/Não)
for casos in [casos_dengue, casos_graves]:
    casos.loc[:, sintomas_cols] = casos[sintomas_cols].replace({1: 1, 2: 0})

# Calcular as frequências dos sintomas
frequencias_dengue = casos_dengue[sintomas_cols].mean()
frequencias_graves = casos_graves[sintomas_cols].mean()

# Calcular a diferença de frequências
diferencas_frequencia = frequencias_graves - frequencias_dengue

# Criar o grafo
grafo = nx.Graph()

# Adicionar o nó central
grafo.add_node('Dengue Grave', size=20)

# Adicionar sintomas ao grafo com base na diferença de frequência
limiar_diferenca = 0.1  # Ajuste o limiar conforme necessário
sintomas_relevantes = []
for sintoma, diferenca in diferencas_frequencia.items():
    if abs(diferenca) > limiar_diferenca:  # Apenas sintomas relevantes
        grafo.add_node(sintoma, size=abs(diferenca))
        grafo.add_edge('Dengue Grave', sintoma, weight=diferenca)
        sintomas_relevantes.append(sintoma)

# Adicionar correlações entre os sintomas relevantes
limiar_correlacao = 0.01  # Ajuste o limiar conforme necessário
for i, sintoma1 in enumerate(sintomas_relevantes):
    for sintoma2 in sintomas_relevantes[i+1:]:  # Evitar combinações repetidas
        # Calcular co-ocorrência entre os dois sintomas
        co_ocorrencia = casos_graves[(casos_graves[sintoma1] == 1) & (casos_graves[sintoma2] == 1)].shape[0]
        co_ocorrencia_freq = co_ocorrencia / len(casos_graves)
        
        if co_ocorrencia_freq > limiar_correlacao:
            grafo.add_edge(sintoma1, sintoma2, weight=co_ocorrencia_freq)

# Configuração do layout circular
pos = nx.circular_layout(grafo)

# Funções auxiliares para melhorar visualização
def get_edge_color(weight):
    return 'dodgerblue' if weight > 0 else 'lightcoral'

def get_edge_width(weight):
    min_width = 1  # Espessura mínima
    return max(min_width, abs(weight) * 10)

def draw_labels_with_offset(graph, pos):
    for node, (x, y) in pos.items():
        label = node
        if label == "Dengue Grave":  # Nó central
            plt.text(
                x, y, label,
                fontsize=12, fontweight="bold", ha="center", va="center",
                bbox=dict(boxstyle="circle", facecolor="lightyellow", edgecolor="black", alpha=0.8)
            )
        else:
            offset_x = 0.02 if x > 0 else -0.02
            offset_y = 0.02 if y > 0 else -0.02
            plt.text(
                x + offset_x, y + offset_y, label,
                fontsize=10, ha="center", va="center",
                bbox=dict(boxstyle="round", facecolor="white", edgecolor="black", alpha=0.7)
            )

# Visualizar o grafo
plt.figure(figsize=(15, 15))

# Desenhar os nós
sizes = [grafo.nodes[node].get('size', 1) * 500 for node in grafo.nodes()]
nx.draw_networkx_nodes(grafo, pos, node_size=sizes, node_color='skyblue', alpha=0.9)

# Desenhar as arestas com a paleta de cores refinada e espessura mínima
edges = grafo.edges(data=True)
for u, v, data in edges:
    weight = data['weight']
    nx.draw_networkx_edges(
        grafo, pos,
        edgelist=[(u, v)],
        width=get_edge_width(weight),
        edge_color=[get_edge_color(weight)],
        alpha=0.8
    )

# Adicionar rótulos aos nós com deslocamento para evitar sobreposição
draw_labels_with_offset(grafo, pos)

# Configurar título e exibição
plt.title("Relações entre Dengue Grave e Sintomas (Layout Circular Refinado)", fontsize=16)
plt.axis('off')
plt.show()



