<?php
session_start();
include 'config.php';

if ($_SERVER["REQUEST_METHOD"] == "POST") {
    $nome = trim($_POST["nome"]);
    $dtnasc = trim($_POST["dtnasc"]);
    $genero = trim($_POST["genero"]);
    $cpf = trim($_POST["cpf"]);
    $cep = trim($_POST["cep"]);
    $endereco = trim($_POST["endereco"]);
    $telefone = trim($_POST["telefone"]);
    $email = trim($_POST["email"]);
    $plano = trim($_POST["plano"]);

    $sql = "INSERT INTO alunos (nome, dtnasc, genero, cpf, cep, endereco, telefone, email, plano) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)";
    $stmt = $conn->prepare($sql);
    $stmt->bind_param("sssssssss", $nome, $dtnasc, $genero, $cpf, $cep, $endereco, $telefone, $email, $plano);

    if ($stmt->execute()) {
        header("Location: usuarios.php");
        exit();
    } else {
        $erro = "Erro ao cadastrar. Tente outro cpf!";
    }
}
$sql = "SELECT id FROM alunos";
$result = "id";
?>

<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <title>Cadastrar Usuário</title>
</head>
<body>
</body>
</html>
