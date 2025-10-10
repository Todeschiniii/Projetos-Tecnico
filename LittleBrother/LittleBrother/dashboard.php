<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Document</title>
    <link rel="stylesheet" href="styledash.css">
</head>
<body>

<?php
session_start();
include 'config.php';
$sql= "SELECT nome, tipo FROM usuarios WHERE id= ? && tipo='admin' ";

echo "<h1 style='color: rgba(153, 16, 16, 1); '>Bem-vindo, " . $_SESSION['usuario_nome'] . "</h1>";
    echo "<br>";
if ($_SESSION['usuario_tipo'] === 'admin') {
    echo "<button><a href='CadastroAcad.php'>Cadastrar Novos Alunos</a></button>";
    echo "<button><a href='alunos.php'>Gerenciar Alunos</a></button>";
    echo "<button><a href='cadastrar_usuarios.php'>Cadastrar Usuários</a></button>";
    echo "<button><a href='usuarios.php'>Gerenciar Usuários</a></button>";
    } else {
       header("location:index.html");
    }
    echo "<br>";
    echo "<hr>";
    echo "<button><a class='btn btn-dark' href='logout.php'>Sair</a></button>";
?>
    
</body>
</html>