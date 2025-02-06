import matplotlib.pyplot as plt
import networkx as nx
import community as community_louvain

class Visualizer:
    @staticmethod
    def visualize_graph(grafo, titulo="Grafo de Relações - Dengue Grave"):
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

    @staticmethod
    def visualize_communities(grafo):
        partition = community_louvain.best_partition(grafo)
        nx.set_node_attributes(grafo, partition, 'comunidade')

        pos = nx.circular_layout(grafo)
        communities = set(partition.values())
        color_map = {community: plt.cm.tab20.colors[i % 20] for i, community in enumerate(communities)}

        plt.figure(figsize=(12, 8))
        for community, color in color_map.items():
            nodes = [node for node in partition if partition[node] == community]
            nx.draw_networkx_nodes(grafo, pos, nodelist=nodes, node_color=[color], label=f"Comunidade {community}")

        nx.draw_networkx_edges(grafo, pos, alpha=0.5)
        nx.draw_networkx_labels(grafo, pos, font_size=10, font_color='black')

        plt.title("Comunidades detectadas pelo algoritmo Louvain")
        plt.legend(loc='best')
        plt.show()