import os
import pandas as pd
import matplotlib.pyplot as plt

# Ler CSV
df = pd.read_csv(os.path.join(os.path.dirname(__file__), "iris.csv"))

# Impedir que corte os nomes das colunas
pd.set_option('display.max_colwidth', None)

# Aumenta a largura de exibição
pd.set_option('display.width', 120)

# Mostrar as 5 primeiras linhas
print("Primeiras 5 linhas:\n", df.head())

# Mostra as 10 primeiras linhas
print("Primeiras 10 linhas:\n", df.head(10))

# mostrar até 10 colunas -> .head() mostra as primeiras 5 e ultimas 5 se tiver mais de 10
pd.set_option('display.max_columns', 10)

# Informações Gerais
print("tipos de dados e colunas:\n", df.info())
print("estatísticas (média, desvio padrão, etc.):\n", df.describe())

# Selecionar colunas
coluna = df['SepalWidthCm']
print("Coluna SepalWidthCm:\n", coluna)

# Média de uma coluna ( Jeito Simples )
media = df['SepalLengthCm'].sum() / 5
print("Média de uma coluna:\n", media)

# Filtrar Linhas
filtro = df[df['SepalLengthCm'] > 7.0]
print("Filtro:\n", filtro)

# ------------------------------- MÉTODO: groupby() -------------------------------

data = {
    'categoria': ['A', 'A', 'B', 'B', 'C', 'C'],
    'valor': [10, 20, 5, 15, 30, 25]
}
df = pd.DataFrame(data)

# Transformar texto em números
df['categoria_cod'] = df['categoria'].astype('category').cat.codes
# ou
from sklearn.preprocessing import LabelEncoder
encoder = LabelEncoder()
df['categoria_cod'] = encoder.fit_transform(df['categoria'])

# Pinta o background_gradient de azul e pinta a célula com o maior valor de vermelho
df.style.background_gradient(cmap = 'Blues').highlight_max(color = 'lightcoral')

# Formata os valores com 2 casas dps da vírgula
df.style.format({'valor': '{:.2f}'})

# Salva arquivo CSV modificado
df.to_csv("maior_vermelho.csv", index = False)
df.to_html("tabela_bonita.html", index = False)

# Volta ao padrão
pd.reset_option('all')

# Visualizar como tabela HTML
styled = df.style.background_gradient(cmap = 'viridis')
styled.to_html('tabela_bonita.html')

# Soma por Categoria
teste = df.groupby('categorias')['valor'].sum()
print("Soma por Categoria:", teste)

# Contagem por Categoria 
teste = df.groupby('categoria')['valor'].count()
print("Contagem por Categoria:\n", teste)

# Valor máximo e mínimo
maior = df.groupby('categoria')['valor'].max()
menor = df.groupby('categoria')['valor'].min()
print("Maior: ", maior)
print("Menor: ", menor)

#  Mais de uma operação ao mesmo tempo: agg() = aggregate → permite combinar várias operações de uma vez.
teste = df.groupby('categoria')['valor'].agg(['sum', 'mean', 'max', 'min', 'count'])
print("Várias operações ao mesmo tempo:\n", teste)

# Média de uma coluna ( Automático )
media = df['SepalLengthCm'].mean()
print("Média da Coluna ( SepalLengthCm):\n",media)

df.head()       # Primeiras 5 linhas
df.tail()       # Últimas 5 linhas
df.info()       # tipos de dados e colunas
df.describe()   # estatísticas ( média. desvio padrão, etc.)
df.shape        # ( linhas, colunas )
df.columns      # nomes das colunas

df['SepalLengthCm']                     # Seleciona uma coluna
df[['SepalLengthCm', 'SepalWidthCm']]   # Seleciona várias colunas
df[df['SepalLengthCm'] > 6.0]           # Filtrar Linhas
df[df['Id'] == 1]                       # Filtro por Igualdade

df.sort_values(by = 'SepalLengthCm', ascending = False)
df.reset_index(drop = True)

df['Média'] = df['SepalLengthCm'].mean()     # Criar ou Modificar colunas

df.isnull().sum()     # conta quantos valores faltanm
df = df.dropna()      # remove linhas com valores faltando
df['SepalLengthCm'] = df['SepalLengthCm'].fillna(df['coluna'].mean()) # Se tiver algum dado faltando, ele é substituído pela média geral da coluna.

df = pd.read_csv('iris.csv')
novo = pd.read_csv('maior_vermelho.csv')
df_completo = pd.concat([df, novo])

df_completo.to_csv('df_completo.csv', index = False)


