import pandas as pd

class DataProcessor:
    def __init__(self, file_path):
        self.df = pd.read_csv(file_path)
        self.sintomas_cols = ['FEBRE', 'MIALGIA', 'CEFALEIA', 'EXANTEMA', 'VOMITO', 'NAUSEA',
                              'DOR_COSTAS', 'CONJUNTVIT', 'ARTRITE', 'ARTRALGIA', 'PETEQUIA_N',
                              'LEUCOPENIA', 'LACO', 'DOR_RETRO', 'DIABETES', 'HEMATOLOG', 'HEPATOPAT',
                              'RENAL', 'HIPERTENSA', 'ACIDO_PEPT', 'AUTO_IMUNE']

    def filter_cases(self):
        casos_dengue = self.df[self.df['CLASSI_FIN'] == 10]
        casos_graves = self.df[self.df['CLASSI_FIN'] == 12]
        return casos_dengue, casos_graves

    def prepare_data(self, casos_dengue, casos_graves):
        for casos in [casos_dengue, casos_graves]:
            casos.loc[:, self.sintomas_cols] = casos[self.sintomas_cols].replace({1: 1, 2: 0})
        return casos_dengue, casos_graves

    def calculate_frequencies(self, casos_dengue, casos_graves):
        frequencias_dengue = casos_dengue[self.sintomas_cols].mean()
        frequencias_graves = casos_graves[self.sintomas_cols].mean()
        diferencas_frequencia = frequencias_graves - frequencias_dengue
        return frequencias_dengue, frequencias_graves, diferencas_frequencia