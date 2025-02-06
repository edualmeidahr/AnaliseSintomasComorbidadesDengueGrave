from data_processor import DataProcessor
from graph_analyzer import GraphAnalyzer
from visualizer import Visualizer
from statistical_analyzer import StatisticalAnalyzer

def main():
    file_path = 'datas/sinan_dengue_filtrada.csv'
    
    # Processamento dos dados
    data_processor = DataProcessor(file_path)
    casos_dengue, casos_graves = data_processor.filter_cases()
    casos_dengue, casos_graves = data_processor.prepare_data(casos_dengue, casos_graves)
    frequencias_dengue, frequencias_graves, diferencas_frequencia = data_processor.calculate_frequencies(casos_dengue, casos_graves)

    # Análise do grafo
    graph_analyzer = GraphAnalyzer(casos_graves, diferencas_frequencia)
    grafo = graph_analyzer.create_graph(limiar_diferenca=0.01, limiar_correlacao=0.01)
    centralidade_df = graph_analyzer.calculate_centralities(grafo)

    # Visualização do grafo
    visualizer = Visualizer()
    visualizer.visualize_graph(grafo)
    visualizer.visualize_communities(grafo)

    # Análise estatística
    statistical_analyzer = StatisticalAnalyzer(data_processor.df, data_processor.sintomas_cols)
    testes_qui2 = statistical_analyzer.perform_chi2_tests()
    df_testes = statistical_analyzer.create_ranking(testes_qui2)

    # Exibir resultados estatísticos
    print("Resultados dos testes qui-quadrado:")
    print(df_testes)

    # Salvar resultados em arquivos CSV (opcional)
    df_testes.to_csv('resultados_testes_qui2.csv', index=False)
    centralidade_df.to_csv('centralidades_sintomas.csv', index=False)

if __name__ == "__main__":
    main()