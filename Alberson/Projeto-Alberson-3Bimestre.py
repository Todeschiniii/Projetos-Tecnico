import mysql.connector
from prettytable import PrettyTable

def formatar_minutos(valor):
    return f'{valor}min'
    
def formatar_reais(valor):
    return f'R$ {valor:.2f}'
    
def formatar_idade(valor):
    return f'{valor} anos'
    
def formatar_serie(valor):
    return f'{valor}º ano'
    
def formatar_telefone(valor):
    return f'({valor[:2]}) {valor[2:7]}-{valor[7:]}'
  
FORMATACOES = {
    'Carga Horária': formatar_minutos,
    'Telefone do Professor': formatar_telefone,
    'Idade do Professor': formatar_idade,
    'Ano Letivo': formatar_serie,
    'Sálario do Professor': formatar_reais,
}

def abrebanco():
    try:
        global conexao
        conexao = mysql.connector.Connect(host = 'localhost', user = 'root', database = 'univap' ,password = '')

        if conexao.is_connected():
            print(f'Conectado ao servidor de Banco de Dados - Versao {conexao.get_server_info()}')
            print('Conexao OK')
            comandosql = conexao.cursor()
            comandosql.execute('select database()')
            print(f'Banco de Dados acessado: {comandosql.fetchone()}')
            return 1
        
        else:
            print('Conexão não realizada com o Banco')
            return 0
        
    except Exception as erro:
        print(f'Erro: {erro}')
        return 0
    
def mostrarTabelas(Tabela, Titulos):

    grid = PrettyTable(Titulos)
    try:
        comandosql = conexao.cursor()
        comandosql.execute(f'select *from {Tabela}')
        dados = comandosql.fetchall()

        if comandosql.rowcount > 0:
            for registro in dados:
                nova_linha = []
                for i, valor in enumerate(registro): 
                    if Titulos[i] in FORMATACOES:
                        valor = FORMATACOES[Titulos[i]](valor)
                    nova_linha.append(valor)
                grid.add_row(nova_linha)
            print(grid)
        else:
            print(f'Não existe nenhum registro na tabela {tabela}')

    except Exception as erro:
        print('Erro: ',erro)

def consultar(codigo, tabela, titulos, coluna):
    try:
        comandosql = conexao.cursor()
        comandosql.execute(f'select *from {tabela} where {coluna} = {codigo}')
        dados = comandosql.fetchone()
        sql = ''  
        if comandosql.rowcount > 0:
            tamanho = len(dados)
            for x in range(1, tamanho):
                sql += f'{titulos[x]}: {dados[x]}'
                if x < tamanho - 1:
                    sql += '\n '
            print(sql)
            print('Consulta realizada com Sucesso!')
        else:
            print('Código não existe nessa tabela!')

    except Exception as erro:
        print('Erro: ', erro)

def cadastrar(codigo, tabela, titulos):
    try:
        dados = [codigo]
        placeholders = '%s, '
        for x in range(1, len(titulos)):
            dados.append(input(f'{titulos[x]}: '))
            placeholders += '%s'
            if x < len(titulos) - 1:
                placeholders += ', '
        comandosql = conexao.cursor()
        sql = f'INSERT INTO {tabela} VALUES({placeholders})'
        comandosql.execute(sql, dados)
        conexao.commit()
        print('Cadastro feito com Sucesso!')

    except Exception as erro:
        print('Erro: ', erro)
    
def alterar(codigo, tabela, titulos, colunas):
    try:
        dados = []
        sql = f'Update {tabela} SET '
        tamanho = len(titulos)
        for x in range(1, tamanho):
            dados.append(input(f'{titulos[x]}: '))
            sql += f'{colunas[x]} = %s'
            if x < tamanho - 1:
                sql += ', '
        dados.append(codigo)
        sql += f'WHERE {colunas[0]} = %s'
        comandosql = conexao.cursor()
        comandosql.execute(sql, dados)
        conexao.commit()
        print('Alteração feita com Sucesso!')
    except Exception as erro:
        print('Erro: ', erro)

def  excluir(codigo, tabela, coluna):
    try:
        comandosql = conexao.cursor()
        comandosql.execute(f'DELETE FROM {tabela} WHERE {coluna} = {codigo}')
        conexao.commit()
        print('Exclusão finalizada com Sucesso!')
    except Exception as erro:
        print('Erro: ', erro)
        print('Não foi possível fazer a Exclusão!')
    
def verificar_codigo_existente(codigo, tabela, coluna):
    try:
        comandosql = conexao.cursor()
        comandosql.execute(f'SELECT * FROM {tabela} WHERE {coluna} = {codigo}')
        resultado = comandosql.fetchone()
        return resultado is not None
    except Exception as e:
        print("Erro SQL:", e)
        return False
    
def lervalor(titulo):
    while True:
        codigo = input(f'{titulo}: ')
        if codigo.isnumeric():
            codigo = int(codigo)
            return codigo
        print('Digite um Código Válido!')

'''
====================================== MÓDULO PRINCIPAL DO PROGRAMA ======================================
'''

if abrebanco() == 1:
    resp = input('\nDeseja entrar no Sistema Univap?\n[S] - Sim, ou qualquer tecla para Sair ===> ').upper()

    while resp == 'S':
        print()
        print('<','='*80)
        print('{:^80}'.format('SISTEMA UNIVAP'))
        print('='*80, '>')

        while True:
            tabela = input('''
<=== MOSTRAR TABELAS ===>
[D] - disciplinas
[P] - professores
[DXP] - disciplinasxprofessores
[OUTRA TECLA] - OPERAÇÕES ===> ''').upper()

            if tabela == 'D':
                mostrarTabelas('disciplinas', ['Código da Disciplina', 'Nome da Disciplina'])
                

            elif tabela == 'P':
                mostrarTabelas('professores', ['Código do Professor', 'Nome do Professor', 'Telefone do Professor', 'Idade do Professor', 'Sálario do Professor'])

            elif tabela == 'DXP':
                mostrarTabelas('disciplinasxprofessores', ['Código da Disciplina no Curso', 'Código do Professor', 'Código da Disciplina', 'Curso', 'Carga Horária', 'Ano Letivo'])    

            else:
                break

        entrada = input('''
<=== OPERAÇÕES ===> / <=== TABELA ===>
[C] - Cadastrar / [D] - Disciplinas
[CO] - Consulta / [P] -Professores
[A] - Alterar / [DXP] - DisciplinasxProfessores
[E] - Excluir 
EX: CO/DXP
[OUTRA TECLA] - Sair ===> ''').upper()
        print()
        if "/" in entrada:
            opcoes, tabela = entrada.split("/")
            if opcoes in ['CO', 'C', 'A', 'E'] and tabela in ['D', 'P', 'DXP']:

                if tabela == 'D':
                    tabela = 'disciplinas'
                    titulos = ['Código da Disciplina', 'Nome da Disciplina']
                    colunas = ['codigodisc', 'nomedisc']

                elif tabela == 'P':
                    tabela = 'professores'
                    titulos = ['Código do Professor', 'Nome do Professor', 'Telefone do Professor', 'Idade do Professor', 'Sálario do Professor']
                    colunas = ['registro', 'nomeprof', 'telefoneprof', 'idadeprof', 'salarioprof']

                else:
                    tabela = 'disciplinasxprofessores'  
                    titulos = ['Código da Disciplina no Curso', 'Código do Professor', 'Código da Disciplina', 'Curso', 'Carga Horária', 'Ano Letivo']
                    colunas = ['codigodisciplinanocurso', 'codigoprof', 'codigodisc', 'curso', 'cargahoraria', 'anoletivo']

                while resp == 'S':
                    codigo = lervalor(titulos[0])
                    if opcoes == 'C':
                        if not verificar_codigo_existente(codigo, tabela, colunas[0]):
                            cadastrar(codigo, tabela, titulos)
                            break
                        else:
                            resp = input(f'Não foi Possível realizar o Cadastro!\nJá existe um(a) {titulos[0]} com esse Código!\nDeseja Repetir a mesma Operação?\n[S] - SIM [N] - NÃO ===>').upper()

                    elif opcoes == 'CO':
                        if verificar_codigo_existente(codigo, tabela, colunas[0]):
                            consultar(codigo, tabela, titulos, colunas[0])
                            break
                        else:
                            resp = input(f'Não foi Possível realizar a Consulta!\nNão existe um(a) {titulos[0]} com esse Código!\nDeseja Repetir a mesma Operação?\n[S] - SIM [N] - NÃO ===> ').upper()
                    elif opcoes == 'A':
                        if verificar_codigo_existente(codigo, tabela, colunas[0]):
                            print('ATENÇÃO: Código da Disciplina no Curso não pode ser alterado!')
                            alterar(codigo, tabela, titulos, colunas)
                            break
                        else:
                            resp = input(f'Não foi Possível realizar a Atualização!\nNão existe um(a) {titulos[0]} com esse Código!\nDeseja Repetir a mesma Operação?\n[S] - SIM [N] - NÃO ===> ').upper()
                    else:
                        if verificar_codigo_existente(codigo, tabela, colunas[0]):
                            confirma = input('ATENÇÃO!!! O DADO SERÁ EXCLUÍDO PERMANENTEMENTE!\nCONFIRMA EXCLUSÃO? [S] - SIM [N] - NÃO ===> ').upper()
                            while confirma not in ['S', 'N']:
                                confirma = input('RESPOSTA INEXISTENTE! CONFIRMA EXCLUSÃO?\n[S] - SIM [N] - NÃO ===> ').upper()
                            if confirma == 'S':
                                excluir(codigo, tabela, colunas[0])
                                break
                            else:
                                print('Exclusão Cancelada!')
                        else:
                            resp = input(f'Não foi Possível realizar a Exclusão!\nNão existe um(a) {titulos[0]} com esse Código!\nDeseja Repetir a mesma Operação?\n[S] - SIM [N] - NÃO ===> ').upper()
            else:
                print('Entrada Inválida! Siga o Exemplo!')
        else:
            print('Entrada Inválida! Necessita de "/"!')
        resp = input('\nDeseja repetir o processo?\n[S] - SIM [OUTRA TECLA] - NÃO ===> ').upper()
        #Banana12345