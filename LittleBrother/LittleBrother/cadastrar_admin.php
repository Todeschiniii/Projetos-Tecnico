<?php
include 'config.php';

$nome = "Administrador";
$email = "admin@email.com";
$senha = "senha123";
$senha_hash = password_hash($senha, PASSWORD_DEFAULT);
$tipo = "admin";

$sql = "INSERT INTO usuarios (nome, email, senha, tipo) VALUES (?, ?, ?, ?)";
$stmt = $conn->prepare($sql);
$stmt->bind_param("ssss", $nome, $email, $senha_hash, $tipo);

if ($stmt->execute()) {
    echo "Administrador cadastrado com sucesso!";
} else {
    echo "Erro ao cadastrar: " . $conn->error;
}
?>
