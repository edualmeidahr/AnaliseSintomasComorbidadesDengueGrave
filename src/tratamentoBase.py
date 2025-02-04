import pandas as pd

bd = pd.read_csv('datas/sinan_dengue_sample_2024.csv', low_memory=False)

# Definir as colunas de interesse
colunas_interesse = [
    # Informações temporais
    "DT_SIN_PRI",

    # Dados demográficos
    "NU_IDADE_N", "CS_SEXO",

    # Sintomas clínicos
    "FEBRE", "MIALGIA", "CEFALEIA", "EXANTEMA", "VOMITO", "NAUSEA",
    "DOR_COSTAS", "CONJUNTVIT", "ARTRITE", "ARTRALGIA", "PETEQUIA_N",
    "LEUCOPENIA", "LACO", "DOR_RETRO",

    # Comorbidades
    "DIABETES", "HEMATOLOG", "HEPATOPAT", "RENAL", "HIPERTENSA",
    "ACIDO_PEPT", "AUTO_IMUNE",

    # Resultados de exames e evolução
    "RESUL_SORO", "RESUL_NS1", "RESUL_PCR_", "HOSPITALIZ",
    "CLASSI_FIN", "EVOLUCAO"
]

# Filtrar apenas as colunas de interesse
base_filtrada = bd[colunas_interesse]


# Converter a coluna de datas (DT_SIN_PRI) para datetime
base_filtrada["DT_SIN_PRI"] = pd.to_datetime(base_filtrada["DT_SIN_PRI"], errors="coerce")

# Garantir que a coluna CS_SEXO (sexo) seja categórica
base_filtrada["CS_SEXO"] = base_filtrada["CS_SEXO"].astype("category")

# Tratamento de valores nulos
base_filtrada = base_filtrada.dropna(subset=["EVOLUCAO"])
base_filtrada = base_filtrada.dropna(subset=["CLASSI_FIN"])
base_filtrada['HOSPITALIZ'] = base_filtrada['HOSPITALIZ'].fillna(9)
# Substituindo valores nulos nas colunas de resultados de exames por 4 (exame não realizado)
colunas_exames = ['RESUL_SORO', 'RESUL_NS1', 'RESUL_PCR_']
base_filtrada[colunas_exames] = base_filtrada[colunas_exames].fillna(4)
base_filtrada = base_filtrada.dropna(subset=["CS_SEXO"])
print(base_filtrada.isnull().sum())

base_filtrada.to_csv("sinan_dengue_filtrada.csv", index=False)