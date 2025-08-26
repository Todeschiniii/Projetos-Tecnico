import streamlit as st
import mysql.connector
from prettytable import PrettyTable

st.set_page_config(page_title='Sistema Univap - Presenças', page_icon=':book:', layout='wide')

@st.cache_resource
def abrebanco():
    try:
        global conexao
        conexao = mysql.connector.Connect(host='localhost', user='root', database='Univap_Bruno', password='Davi2008')

        if conexao.is_connected():
            st.write('Conexão OK!')

            comandosql = conexao.cursor()
            comandosql.execute('select database();')
            st.write(f'Banco de Dados acessado = {comandosql.fetchone()}')
            st.write('---')
            return 1

        else:
            st.error('Conexão não realizada com o Banco!')
            return 0

    except Exception as erro:
        st.error(f"Erro: {erro}")
        return 0

@st.cache_data
def mostrarAlunos():
    grid = st.table(['Códigos dos Alunos', 'Nome dos Alunos', 'Presente'])
    try:
        comandosql = conexao.cursor()
        comandosql.execute('select * from Presenca')
        dados = comandosql.fetchall()

        if comandosql.rowcount > 0:
            for registro in dados:
                grid.add_row([registro[0], registro[1], registro[2]])
            st.write(grid)

        else:
            st.write('Não existem Alunos Cadastrados!')

    except Exception as erro:
        st.error(f"Erro: {erro}")


def cadastrarAluno(id=0, nomealuno='', presente=''):
    try:
        comandosql = conexao.cursor()
        if presente == 'S':
            presente = 'Sim'
        else:
            presente = 'Não'
        comandosql.execute(f'INSERT INTO Presenca VALUES ({id}, "{nomealuno}", "{presente}")')
        conexao.commit()
        st.write('Cadastro do Aluno realizado com Sucesso!')

    except Exception as erro:
        if '1062' in str(erro):
            st.write('Já existe um Aluno com esse ID!')
        else:
            st.error(f"Erro: {erro}")


def alterarAluno(id=0, nomealuno='', presente=''):
    try:
        comandosql = conexao.cursor()

        if presente == 'S':
            presente = 'Sim'
        else:
            presente = 'Não'

        comandosql.execute(f'Update Presenca SET nomeAluno = {nomealuno}, Presente = {presente} WHERE idAluno = {id}')
        conexao.commit()
        st.write('Aluno alterado com Sucesso!')

    except Exception as erro:
        if '1054' in str(erro):
            st.write('Nenhum Aluno encontrado com esse ID para Atualizar!')
        else:
            st.error(f"Erro: {erro}")


def excluirAluno(id=0):
    try:
        comandosql = conexao.cursor()
        comandosql.execute(f'DELETE FROM Presenca WHERE idAluno = {id}')
        conexao.commit()

        if comandosql.rowcount > 0:
            st.write('Aluno excluído com Sucesso!')
        else:
            st.error('Nenhum Aluno encontrado com esse ID para excluir!')

    except Exception as erro:
        st.error(f"Erro: {erro}")
        st.write('Não foi possível excluir esse Aluno')


if abrebanco() == 1:
    resp = st.text_input('Deseja entrar no módulo de Presenças?\n[S] - SIM [OUTRA TECLA] - SAIR ===> ').upper()

    while resp == 'S':
        st.write('---')
        st.title('{:^80}'.format('SISTEMA UNIVAP - PRESENCA'))
        st.write('---')

        while True:
            codigo = st.text_input('ID do Aluno: [0] - Mostrar Relatório ===> ')
            if codigo.isnumeric() or codigo:
                codigo = int(codigo)
                break
            st.error('Código deve ser um Número!')

        if codigo == 0:
            mostrarAlunos()
        else:
            opcoes = st.selectbox(
                "<=== OPERAÇÕES ===>",
                ["Cadastrar", "Alterar", "Excluir", "Sair"]
            )
            st.write('---')

            if opcoes in ['Cadastrar', 'Alterar', 'Excluir']:
                if opcoes == 'Cadastrar':
                    nomeAluno = st.text_input('Nome do Aluno: ')
                    presente = st.selectbox(
                        "O Aluno estava presente?",
                        ["S", "N"]
                    )
                    cadastrarAluno(codigo, nomeAluno, presente)

                elif opcoes == 'Alterar':
                    nomeAluno = st.text_input('Nome do Aluno: ')
                    presente = st.selectbox(
                        "O Aluno estava presente?",
                        ["S", "N"]
                    )
                    alterarAluno(codigo, nomeAluno, presente)

                else:
                    confirma = st.text('ATENÇÃO!!! O DADO SERÁ EXCLUÍDO PERMANENTEMENTE!\nCONFIRMA EXCLUSÃO? [S] - SIM [N] - NÃO ===> ')
                    if st.button("Sim"):
                        confirma = "S"
                    if st.button("NÃO"):
                        confirma = "N"
                    if confirma == 'S':
                        excluirAluno(codigo)
                    else:
                        st.write('Exclusão Cancelada!')
    st.write('Processo Finalizado!')