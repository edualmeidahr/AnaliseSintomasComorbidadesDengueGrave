import networkx as nx
import pandas as pd

class GraphAnalyzer:
    def __init__(self, casos_graves, diferencas_frequencia):
        self.casos_graves = casos_graves
        self.diferencas_frequencia = diferencas_frequencia

    def create_graph(self, limiar_diferenca=0.01, limiar_correlacao=0.01):
        grafo = nx.Graph()
        grafo.add_node('Dengue Grave', size=20)

        sintomas_relevantes = []
        for sintoma, diferenca in self.diferencas_frequencia.items():
            if abs(diferenca) > limiar_diferenca:
                grafo.add_node(sintoma, size=abs(diferenca))
                grafo.add_edge('Dengue Grave', sintoma, weight=diferenca)
                sintomas_relevantes.append(sintoma)

        for i, sintoma1 in enumerate(sintomas_relevantes):
            for sintoma2 in sintomas_relevantes[i+1:]:
                co_ocorrencia = self.casos_graves[(self.casos_graves[sintoma1] == 1) & (self.casos_graves[sintoma2] == 1)].shape[0]
                co_ocorrencia_freq = co_ocorrencia / len(self.casos_graves)
                if co_ocorrencia_freq > limiar_correlacao:
                    grafo.add_edge(sintoma1, sintoma2, weight=co_ocorrencia_freq)

        return grafo

    def calculate_centralities(self, grafo):
        centralidade_grau = nx.degree_centrality(grafo)
        centralidade_intermediacao = nx.betweenness_centrality(grafo)
        centralidade_df = pd.DataFrame({
            "Sintoma": list(centralidade_grau.keys()),
            "Centralidade_Grau": list(centralidade_grau.values()),
            "Centralidade_Intermediação": list(centralidade_intermediacao.values())
        })
        return centralidade_df