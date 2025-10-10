<?php
$servidor = "localhost"; // Alterar se necessário
$usuario = "root"; // Alterar conforme seu banco de dados
$senha = ""; // Coloque sua senha do banco de dados
$banco = "academia";

$conn = new mysqli($servidor, $usuario, $senha, $banco);

if ($conn->connect_error) {
    die("Erro na conexão: " . $conn->connect_error);
}
?>
