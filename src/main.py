import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt
from scipy.stats import chi2_contingency
import community as community_louvain

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

# Função para criar o grafo com limiares dinâmicos
def criar_grafo(limiar_diferenca=0.01, limiar_correlacao=0.01):
    grafo = nx.Graph()

    # Adicionar o nó central
    grafo.add_node('Dengue Grave', size=20)

    # Adicionar sintomas ao grafo com base na diferença de frequência
    sintomas_relevantes = []
    for sintoma, diferenca in diferencas_frequencia.items():
        if abs(diferenca) > limiar_diferenca:  # Apenas sintomas relevantes
            grafo.add_node(sintoma, size=abs(diferenca))
            grafo.add_edge('Dengue Grave', sintoma, weight=diferenca)
            sintomas_relevantes.append(sintoma)

    # Adicionar correlações entre os sintomas relevantes
    for i, sintoma1 in enumerate(sintomas_relevantes):
        for sintoma2 in sintomas_relevantes[i+1:]:  # Evitar combinações repetidas
            # Calcular co-ocorrência entre os dois sintomas
            co_ocorrencia = casos_graves[(casos_graves[sintoma1] == 1) & (casos_graves[sintoma2] == 1)].shape[0]
            co_ocorrencia_freq = co_ocorrencia / len(casos_graves)

            if co_ocorrencia_freq > limiar_correlacao:
                grafo.add_edge(sintoma1, sintoma2, weight=co_ocorrencia_freq)

    return grafo

# Função para visualizar o grafo
def visualizar_grafo(grafo, titulo="Grafo de Relações - Dengue Grave"):
    pos = nx.circular_layout(grafo)

    # Configuração dos tamanhos dos nós
    sizes = [grafo.nodes[node].get('size', 1) * 500 for node in grafo.nodes()]

    # Desenhar os nós
    nx.draw_networkx_nodes(grafo, pos, node_size=sizes, node_color='skyblue', alpha=0.9)

    # Desenhar as arestas
    edges = grafo.edges(data=True)
    for u, v, data in edges:
        weight = data['weight']
        nx.draw_networkx_edges(
            grafo, pos,
            edgelist=[(u, v)],
            width=max(1, abs(weight) * 10),
            edge_color='dodgerblue' if weight > 0 else 'lightcoral',
            alpha=0.8
        )

    # Adicionar rótulos
    nx.draw_networkx_labels(grafo, pos, font_size=10, font_color='black')

    # Configurar título e exibição
    plt.title(titulo, fontsize=16)
    plt.axis('off')
    plt.show()

# Testar diferentes limiares e documentar os resultados
limiares_diferenca = [0.1, 0.05, 0.01]
limiares_correlacao = [0.1, 0.05, 0.01]

resultados = []
grafos = {}
for lim_dif in limiares_diferenca:
    for lim_cor in limiares_correlacao:
        grafo = criar_grafo(limiar_diferenca=lim_dif, limiar_correlacao=lim_cor)
        num_nos = len(grafo.nodes)
        num_arestas = len(grafo.edges)
        resultados.append((lim_dif, lim_cor, num_nos, num_arestas))
        titulo = f"Grafo com limiar de diferença={lim_dif} e correlação={lim_cor}"
        visualizar_grafo(grafo, titulo=titulo)
                # Salvar grafo no dicionário com chave representando os limiares
        chave = f"dif={lim_dif}_corr={lim_cor}"
        grafos[chave] = grafo


# Criar DataFrame com os resultados dos testes
df_resultados = pd.DataFrame(resultados, columns=['Limiar Diferença', 'Limiar Correlação', 'Número de Nós', 'Número de Arestas'])
# print("Resultados dos testes de limiares:")
# print(df_resultados)

# Análise Estatística - Ranking dos Sintomas
ranking_sintomas = diferencas_frequencia.sort_values(ascending=False)

# Testes de hipótese para os sintomas mais destacados

testes_qui2 = {}
for sintoma in sintomas_cols:
    tabela = pd.crosstab(df['CLASSI_FIN'], df[sintoma])
    try:
        chi2, p, _, _ = chi2_contingency(tabela)
        testes_qui2[sintoma] = {'p-valor': p, 'estatística': chi2}
    except ValueError:
        print(f"Erro ao calcular o qui-quadrado para o sintoma {sintoma}")


# Criar DataFrame com os resultados dos testes
# print(testes_qui2)
if 'p-valor' in pd.DataFrame.from_dict(testes_qui2, orient='index').columns:
    df_testes = pd.DataFrame.from_dict(testes_qui2, orient='index').sort_values(by='p-valor')
else:
    print("A coluna 'p-valor' não está presente no DataFrame gerado.")
# print("Ranking dos sintomas por significância estatística:")
# print(df_testes)

# Salvar os resultados preliminares em arquivos CSV
# df_resultados.to_csv('resultados_grafo_limiares.csv', index=False)
# df_testes.to_csv('resultados_testes_qui2.csv')


# Dados corrigidos do teste qui-quadrado, incluindo HIPERTENSA
data = {
    "Sintoma": ["LEUCOPENIA", "HIPERTENSA", "VOMITO", "DIABETES", "CEFALEIA", "RENAL", "PETEQUIA_N", 
                "NAUSEA", "CONJUNTVIT", "AUTO_IMUNE", "ARTRALGIA", "HEMATOLOG", "EXANTEMA", 
                "FEBRE", "DOR_RETRO", "LACO", "HEPATOPAT", "ARTRITE", "DOR_COSTAS", "MIALGIA", "ACIDO_PEPT"],
    "Estatística_Chi2": [16847.95, 2617.51, 1600.19, 1613.14, 1060.76, 594.76, 584.87, 
                         549.66, 392.61, 256.89, 237.65, 218.80, 206.90, 
                         189.77, 130.36, 113.01, 104.76, 80.79, 72.21, 62.28, 33.01],
    "p_valor": [0.0, 0.0, 0.0, 0.0, 1.187e-229, 1.377e-128, 1.922e-126, 
                8.249e-119, 8.830e-85, 2.114e-55, 3.061e-51, 3.657e-47, 1.364e-44, 
                6.845e-41, 4.516e-28, 2.472e-24, 1.470e-22, 2.080e-17, 1.437e-15, 1.912e-13, 3.207e-07]
}

# Criar um DataFrame
df_ranking = pd.DataFrame(data)

# Ordenar o ranking pela estatística Chi2 em ordem decrescente
df_ranking = df_ranking.sort_values(by="Estatística_Chi2", ascending=False)

# Exibir o ranking
# print(df_ranking)

# df_ranking.to_csv('ranking_testes_qui2.csv')

centralidades = {}

for chave , grafo in grafos.items():
    # Centralidade de grau
    centralidade_grau = nx.degree_centrality(grafo)

    # Centralidade de intermediação
    centralidade_intermediacao = nx.betweenness_centrality(grafo)

    # Organizar as centralidades em um DataFrame
    centralidade_df = pd.DataFrame({
        "Sintoma": list(centralidade_grau.keys()),
        "Centralidade_Grau": list(centralidade_grau.values()),
        "Centralidade_Intermediação": list(centralidade_intermediacao.values())
    })
    
    centralidades[chave] = centralidade_df

# for chave, df in centralidades.items():
#     # print(f"Centralidade para o grafo {chave}")
#     # print(df.sort_values(by="Centralidade_Grau", ascending=False))
#     df.to_csv(f'centralidade_{chave}.csv', index=False)
    
    


# Comunidades
# Aplicar o algoritmo Louvain
partition = community_louvain.best_partition(grafo)

# Adicionar as comunidades como atributos dos nós
nx.set_node_attributes(grafo, partition, 'comunidade')

# # Exibir as comunidades detectadas
# for node, community_id in partition.items():
#     print(f"Nó: {node}, Comunidade: {community_id}")


# Visualizar o grafo com cores para as comunidades
# Define uma cor para cada comunidade
pos = nx.circular_layout(grafo)  # Layout do grafo
communities = set(partition.values())
color_map = {community: plt.cm.tab20.colors[i % 20] for i, community in enumerate(communities)}

# Desenhar o grafo com as cores das comunidades
plt.figure(figsize=(12, 8))
for community, color in color_map.items():
    nodes = [node for node in partition if partition[node] == community]
    nx.draw_networkx_nodes(grafo, pos, nodelist=nodes, node_color=[color], label=f"Comunidade {community}")

nx.draw_networkx_edges(grafo, pos, alpha=0.5)
nx.draw_networkx_labels(grafo, pos, font_size=10, font_color='black')

plt.title("Comunidades detectadas pelo algoritmo Louvain")
plt.legend(loc='best')
# plt.show()



# Analisar menores caminhos 

# Função para calcular menor caminho considerando pesos absolutos
# def menor_caminho_abs_dijkstra(grafo, no_inicial='Dengue Grave'):
#     try:
#         # Criar uma cópia do grafo com pesos absolutos
#         grafo_abs = grafo.copy()
#         for u, v, data in grafo_abs.edges(data=True):
#             data['weight'] = abs(data['weight'])  # Aplicar valor absoluto
        
#         # Calcular menor caminho ponderado para todos os nós
#         caminhos = nx.single_source_dijkstra_path_length(grafo_abs, source=no_inicial, weight='weight')
#         return pd.DataFrame(list(caminhos.items()), columns=['Sintoma', 'Menor Caminho'])
#     except nx.NetworkXNoPath:
#         print("Nenhum caminho encontrado no grafo.")
#         return None

# # Foco apenas no grafo com lim_diferenca=0.01 e limiar_correlacao=0.05
# chave_especifica = "dif=0.01_corr=0.05"
# if chave_especifica in grafos:
#     print(f"Calculando menor caminho para o grafo {chave_especifica}...")
#     grafo_especifico = grafos[chave_especifica]
#     resultado_menor_caminho = menor_caminho_abs_dijkstra(grafo_especifico)
    
#     # Salvar o resultado em um arquivo CSV
#     if resultado_menor_caminho is not None:
#         resultado_menor_caminho.to_csv(f'menor_caminho_{chave_especifica}.csv', index=False)
#         print(f"Resultados salvos em menor_caminho_{chave_especifica}.csv")
# else:
#     print(f"Grafo com chave '{chave_especifica}' não encontrado.")

# Função para calcular o maior peso total do caminho de cada sintoma até "Dengue Grave"
def maior_caminho_peso_ate_dengue_grave(grafo, no_central='Dengue Grave'):
    resultado = []
    
    # Função auxiliar para DFS que acumula o peso total
    def dfs_maior_peso(grafo, no_atual, peso_atual, maior_peso, no_central, visitados):
        visitados.add(no_atual)
        
        # Se alcançarmos o nó central, atualizamos o maior peso
        if no_atual == no_central:
            if peso_atual > maior_peso[0]:
                maior_peso[0] = peso_atual
        
        # Explorar os vizinhos
        for vizinho in grafo.neighbors(no_atual):
            if vizinho not in visitados:  # Evitar ciclos
                # Adicionar o peso da aresta entre o nó atual e o vizinho
                peso_aresta = grafo[no_atual][vizinho]['weight']  # Peso da aresta real do grafo
                dfs_maior_peso(grafo, vizinho, peso_atual + peso_aresta, maior_peso, no_central, visitados)
        
        visitados.remove(no_atual)  # Backtracking
    
    # Percorrer todos os nós (sintomas) no grafo
    for sintoma in grafo.nodes():
        if sintoma != no_central:  # Não faz sentido calcular para o nó central
            maior_peso = [0]  # Lista para armazenar o maior peso como referência mutável
            dfs_maior_peso(grafo, sintoma, 0, maior_peso, no_central, set())
            resultado.append((sintoma, maior_peso[0]))
    
    # Retorna um DataFrame com os pesos totais
    return pd.DataFrame(resultado, columns=['Sintoma', 'Peso Total'])

# Chave específica do grafo para calcular os pesos
chave_especifica = "dif=0.01_corr=0.05"
if chave_especifica in grafos:
    print(f"Calculando maior peso total de cada sintoma até 'Dengue Grave' no grafo {chave_especifica}...")
    grafo_especifico = grafos[chave_especifica]
    resultado_peso_total = maior_caminho_peso_ate_dengue_grave(grafo_especifico)
    
    # Salvar o resultado em um arquivo CSV
    if resultado_peso_total is not None:
        resultado_peso_total.to_csv(f'maior_peso_total_ate_dengue_grave_{chave_especifica}.csv', index=False)
else:
    print(f"Grafo com chave '{chave_especifica}' não encontrado.")


# Analisar os nós mais relevantes por comunidade no grafo específico
# def analisar_nos_comunidades(grafo, partition):
#     comunidades = set(partition.values())
#     resultados_comunidade = {}
    
#     for comunidade in comunidades:
#         nos_comunidade = [n for n in grafo.nodes if partition[n] == comunidade]
#         subgrafo = grafo.subgraph(nos_comunidade)
        
#         # Calcular menor caminho e centralidade no subgrafo
#         centralidade = nx.degree_centrality(subgrafo)
#         menor_caminho = menor_caminho_abs_dijkstra(subgrafo)
        
#         resultados_comunidade[comunidade] = {
#             "Centralidade": pd.DataFrame.from_dict(centralidade, orient='index', columns=['Centralidade_Grau']),
#             "Menor Caminho": menor_caminho
#         }
#     return resultados_comunidade

# # Verificar se a partição foi definida para o grafo específico
# if 'partition' in locals():
#     print(f"Analisando comunidades no grafo {chave_especifica}...")
#     comunidades_resultados = analisar_nos_comunidades(grafo_especifico, partition)
    
#     # Salvar os resultados
#     for comunidade, resultados in comunidades_resultados.items():
#         if 'Centralidade' in resultados:
#             resultados['Centralidade'].to_csv(f'centralidade_comunidade_{chave_especifica}_{comunidade}.csv')
#         if 'Menor Caminho' in resultados:
#             resultados['Menor Caminho'].to_csv(f'menor_caminho_comunidade_{chave_especifica}_{comunidade}.csv')
# else:
#     print("Partição não definida para análise de comunidades.")


# Função para explorar os caminhos e calcular os impactos
def caminhos_com_maior_impacto(grafo, no_inicial='Dengue Grave', limite=None):
    caminhos = []
    pesos_caminhos = []

    # Enumerar todos os caminhos para "Dengue Grave"
    print('Enumerando os caminhos para "Dengue Grave"...')
    for no_final in grafo.nodes:
        if no_final == no_inicial:
            continue
        try:
            # Encontrar todos os caminhos simples (DFS)
            for caminho in nx.all_simple_paths(grafo, source=no_inicial, target=no_final):
                # Calcular a soma dos pesos do caminho
                soma_pesos = sum(abs(grafo[u][v]['weight']) for u, v in zip(caminho[:-1], caminho[1:]))
                caminhos.append(caminho)
                pesos_caminhos.append(soma_pesos)
        except nx.NetworkXNoPath:
            pass

    print('Caminhos enumerados.')
    # Criar um DataFrame com os resultados
    df_caminhos = pd.DataFrame({
        'Caminho': caminhos,
        'Impacto': pesos_caminhos
    })

    # Ordenar pelo impacto (peso total do caminho)
    df_caminhos = df_caminhos.sort_values(by='Impacto', ascending=False)

    # Se um limite for fornecido, retornar os caminhos com maior impacto
    if limite:
        df_caminhos = df_caminhos.head(limite)

    return df_caminhos

grafo = grafos["dif=0.01_corr=0.05"]

# Analisar o grafo para os caminhos de maior impacto
resultado_caminhos = caminhos_com_maior_impacto(grafo, no_inicial='Dengue Grave', limite=10)

# # Relacionar os sintomas mais frequentes nos caminhos mais impactantes
# print('Analisando os sintomas mais frequentes nos caminhos...')
# sintomas_frequencia = {}
# for caminho in resultado_caminhos['Caminho']:
#     for sintoma in caminho:
#         if sintoma != 'Dengue Grave':  # Ignorar nó de destino
#             sintomas_frequencia[sintoma] = sintomas_frequencia.get(sintoma, 0) + 1

# # Ordenar os sintomas pela frequência
# sintomas_ordenados = sorted(sintomas_frequencia.items(), key=lambda x: x[1], reverse=True)

# # Exibir os sintomas mais frequentes
# sintomas_df = pd.DataFrame(sintomas_ordenados, columns=['Sintoma', 'Frequência'])
# sintomas_df.to_csv('sintomas_frequencia.csv', index=False)
# print(sintomas_df)

# # Comparar com o ranking qui-quadrado
# ranking_qui2 = pd.read_csv('datas/ranking_testes_qui2.csv')  # Carregar o ranking qui-quadrado
# comparacao = sintomas_df.merge(ranking_qui2, on='Sintoma', how='left')
# comparacao.to_csv('comparacao_sintomas.csv', index=False)
# print(comparacao)



# Analisando os sintomas mais frequentes nos caminhos mais impactantes com pesos
print('Analisando os sintomas mais frequentes nos caminhos considerando pesos...')
sintomas_frequencia_ponderada = {}

# Iterar sobre os caminhos mais impactantes
for caminho in resultado_caminhos['Caminho']:
    for i in range(len(caminho) - 1):  # Iterar pelas arestas no caminho
        u, v = caminho[i], caminho[i + 1]  # Nó atual e próximo nó
        if v != 'Dengue Grave':  # Ignorar nó de destino
            peso = grafo[u][v]['weight']  # Obter o peso da aresta
            sintomas_frequencia_ponderada[v] = sintomas_frequencia_ponderada.get(v, 0) + peso

# Ordenar os sintomas pela frequência ponderada
sintomas_ordenados_ponderados = sorted(sintomas_frequencia_ponderada.items(), key=lambda x: x[1], reverse=True)

# Exibir os resultados
sintomas_df_ponderado = pd.DataFrame(sintomas_ordenados_ponderados, columns=['Sintoma', 'Frequência Ponderada'])
sintomas_df_ponderado.to_csv('sintomas_frequencia_ponderada.csv', index=False)
print(sintomas_df_ponderado)

# Comparar com o ranking qui-quadrado
ranking_qui2 = pd.read_csv('datas/ranking_testes_qui2.csv')  # Carregar o ranking qui-quadrado
comparacao_ponderada = sintomas_df_ponderado.merge(ranking_qui2, on='Sintoma', how='left')
comparacao_ponderada.to_csv('comparacao_sintomas_ponderada.csv', index=False)
print(comparacao_ponderada)



# Fórmula de Indice de Risco
# Dados dos sintomas (extraídos do CSV)
sintomas = [
    {"Sintoma": "LEUCOPENIA", "Estatística_Chi2": 16847.95},
    {"Sintoma": "HIPERTENSA", "Estatística_Chi2": 2617.51},
    {"Sintoma": "DIABETES", "Estatística_Chi2": 1613.14},
    {"Sintoma": "VOMITO", "Estatística_Chi2": 1600.19},
    {"Sintoma": "CEFALEIA", "Estatística_Chi2": 1060.76},
    {"Sintoma": "RENAL", "Estatística_Chi2": 594.76},
    {"Sintoma": "PETEQUIA_N", "Estatística_Chi2": 584.87},
    {"Sintoma": "NAUSEA", "Estatística_Chi2": 549.66},
    {"Sintoma": "CONJUNTVIT", "Estatística_Chi2": 392.61},
    {"Sintoma": "AUTO_IMUNE", "Estatística_Chi2": 256.89},
    {"Sintoma": "ARTRALGIA", "Estatística_Chi2": 237.65},
    {"Sintoma": "HEMATOLOG", "Estatística_Chi2": 218.8},
    {"Sintoma": "EXANTEMA", "Estatística_Chi2": 206.9},
    {"Sintoma": "FEBRE", "Estatística_Chi2": 189.77},
    {"Sintoma": "DOR_RETRO", "Estatística_Chi2": 130.36},
    {"Sintoma": "LACO", "Estatística_Chi2": 113.01},
    {"Sintoma": "HEPATOPAT", "Estatística_Chi2": 104.76},
    {"Sintoma": "ARTRITE", "Estatística_Chi2": 80.79},
    {"Sintoma": "DOR_COSTAS", "Estatística_Chi2": 72.21},
    {"Sintoma": "MIALGIA", "Estatística_Chi2": 62.28},
    {"Sintoma": "ACIDO_PEPT", "Estatística_Chi2": 33.01},
]

# Transformar em DataFrame
df_sintomas = pd.DataFrame(sintomas)

# Lista de sintomas apresentados pelo paciente (exemplo)
sintomas_paciente = ["CEFALEIA", "MIALGIA","VOMITO", 'FEBRE',]

# Calcular o Índice de Risco
def calcular_indice_risco(df, sintomas_paciente):
    # Soma dos pesos dos sintomas apresentados
    soma_pesos_presentes = df[df["Sintoma"].isin(sintomas_paciente)]["Estatística_Chi2"].sum()
    
    # Soma total dos pesos
    soma_pesos_totais = df["Estatística_Chi2"].sum()
    
    # Índice de Risco Normalizado
    indice_risco = soma_pesos_presentes / soma_pesos_totais
    return indice_risco

# Calcular para o exemplo
indice_risco = calcular_indice_risco(df_sintomas, sintomas_paciente)
print(f"Índice de Risco: {indice_risco:.4f}")
