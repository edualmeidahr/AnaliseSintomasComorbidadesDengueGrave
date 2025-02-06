import pandas as pd
from scipy.stats import chi2_contingency

class StatisticalAnalyzer:
    def __init__(self, df, sintomas_cols):
        self.df = df
        self.sintomas_cols = sintomas_cols

    def perform_chi2_tests(self):
        testes_qui2 = {}
        for sintoma in self.sintomas_cols:
            tabela = pd.crosstab(self.df['CLASSI_FIN'], self.df[sintoma])
            try:
                chi2, p, _, _ = chi2_contingency(tabela)
                testes_qui2[sintoma] = {'p-valor': p, 'estatística': chi2}
            except ValueError:
                print(f"Erro ao calcular o qui-quadrado para o sintoma {sintoma}")
        return testes_qui2

    def create_ranking(self, testes_qui2):
        df_testes = pd.DataFrame.from_dict(testes_qui2, orient='index').sort_values(by='p-valor')
        return df_testes