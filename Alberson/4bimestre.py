import pandas as pd
from prettytable import PrettyTable
import os

# Função para formatar nota com cor no HTML
def format_nota(nota):
    if nota == "NÃO INFORMADA":
        return f'<span style="color:gray;">{nota}</span>'
    try:
        n = float(nota)
        nota_formatada = f"{n:.1f}"  # sempre 1 casa decimal
        if n < 6.0:
            return f'<span style="color:red;">{nota_formatada}</span>'
        else:
            return f'<span style="color:blue;">{nota_formatada}</span>'
    except:
        return f'<span>{nota}</span>'

# Função para gerar página HTML do aluno
def gerar_pagina_html(aluno_data, disciplinas, linha):
    codigo = aluno_data['Código']
    nome = aluno_data['Aluno']
    turma = aluno_data['TURMA']
    # Procurar o nome da coluna que contém "MÉDIA"
    for c in aluno_data.keys():
        if "MÉDIA" in c.upper():
            nome_coluna_media = c
            break

    # Pegar o valor da média usando o nome da coluna
    media = aluno_data.get(nome_coluna_media, "NÃO INFORMADA")
    
    # Começa HTML
    html = f'''
    <html lang="pt-BR">
    <head>
        <meta charset="UTF-8">
        <title>Notas do aluno {nome}</title>
        <style>
            body {{
                font-family: Arial, sans-serif;
                background-color:#f0f0f0;
                display: flex;
                flex-direction: column;
                align-items: center; /* Centraliza horizontalmente */
                justify-content: flex-start; /* Alinha ao topo */
                min-height: 100vh;
                margin: 0;
                padding: 40px 20px; /* Espaço do topo e laterais */
            }}
            h2 {{
                color:#333;
                text-align: center;
                margin-bottom: 20px;
            }}
            table {{
                border-collapse: collapse;
                width: 60%;
                margin-bottom: 20px;
                box-shadow: 0 0 10px rgba(0,0,0,0.1);
                background: #fff;
            }}
            th, td {{
                padding: 12px 15px;
                border: 1px solid #ddd;
                text-align: center;
            }}
            th {{
                background-color: #38CFFF;
                color: white;
            }}
            .nota-vermelha {{
                color: red;
                font-weight: bold;
            }}
            .nota-azul {{
                color: blue;
                font-weight: bold;
            }}
            #btnPdf {{
                padding: 10px 20px;
                background-color: #0063DB;
                color: white;
                border: none;
                border-radius: 5px;
                cursor: pointer;
                font-size: 16px;
            }}
            #btnPdf:hover {{
                background-color: #0051DB;
            }}
        </style>
    </head>
    <body>
        <h2>Aluno: {nome} (Código: {codigo}) - Turma: {turma}</h2>
        <table>
            <tr>
                <th>Disciplina</th>
                <th>Nota</th>
            </tr>
    '''
    # Para cada disciplina, pega a nota ou "NÃO INFORMADA"
    for disc in disciplinas:
        nota = aluno_data.get(disc, "NÃO INFORMADA")
        nota_html = format_nota(nota)
        html += f'<tr><td>{disc}</td><td>{nota_html}</td></tr>'
    
    # Média
    media_html = format_nota(media)
    html += f'''
            <tr>
                <th>MÉDIA AT FINAL</th>
                <th>{media_html}</th>
            </tr>
        </table>

        <!-- Botão para PDF (funcionalidade pode ser ligada via JS ou backend) -->
        <button id="btnPdf" onclick="window.print()">Gerar PDF</button>
    </body>
    </html>
    '''
    return html

# Carregar Excel
arquivo_excel = "alberson.xlsx"  # alterar conforme seu arquivo
df = pd.read_excel(arquivo_excel)

# Padronizar nomes das colunas para evitar espaços estranhos
df.columns = [c.strip() for c in df.columns]

# Identificar colunas de disciplinas (todas entre 'IPC' e 'MÉDIA AT-FINAL' exceto colunas iniciais)
colunas = df.columns.tolist()

# Supondo que colunas iniciais são: Código, Aluno, TURMA
# Disciplinas começam após TURMA e antes de MÉDIA AT-FINAL
idx_turma = colunas.index('TURMA')

# Percorre todas as colunas (for i, c in enumerate(colunas)),
# Converte o nome da coluna para maiúsculas (c.upper()),
# Procura a primeira que contém "MÉDIA",
# Retorna o índice dela (next(...)).
for i, c in enumerate(colunas):
    if "MÉDIA" in c.upper():
        idx_media = i
        break

disciplinas = colunas[idx_turma+1:idx_media]

# Criar pasta para armazenar html
pasta_html = 'paginas_alunos'
if not os.path.exists(pasta_html):
    os.makedirs(pasta_html)

# Percorrer alunos linha a linha
for idx, row in df.iterrows():
    linha_excel = idx + 2  # +2 porque índice começa em 0 e tem o cabeçalho na linha 1
    print(f"Linha {linha_excel}:")

    # Construir PrettyTable para exibir
    tabela = PrettyTable()
    tabela.field_names = ["Disciplina", "Nota"]

    # Exibir código, nome e turma
    codigo = row['Código']
    nome = row['Aluno']
    turma = row['TURMA']
    for i, c in enumerate(colunas):
        if "MÉDIA" in c.upper():
            idx_media = i
            break
    media = row[idx_media]
    print(f"Código: {codigo} | Aluno: {nome} | Turma: {turma}")

    for disc in disciplinas:
        nota = row.get(disc, "NÃO INFORMADA")
        if pd.isna(nota):
            nota = "NÃO INFORMADA"
        tabela.add_row([disc, nota])

    # Média
    media_display = media if not pd.isna(media) else "NÃO INFORMADA"
    tabela.add_row(["MÉDIA AT FINAL", media_display])

    print(tabela)

    # Gerar HTML
    aluno_data = row.to_dict()
    html = gerar_pagina_html(aluno_data, disciplinas, linha_excel)

    nome_arquivo = os.path.join(pasta_html, f"{codigo}.html")
    with open(nome_arquivo, 'w', encoding='utf-8') as f:
        f.write(html)
    print(f"Arquivo HTML gerado: {nome_arquivo}\n")
