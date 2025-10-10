<?php
session_start();
include 'config.php';

if ($_SERVER["REQUEST_METHOD"] == "POST") {
    $np = trim($_POST["np"]);
    $valor = trim($_POST["valor"]);
    $qtd = trim($_POST["qtd"]);


    $sql = "INSERT INTO Produtos (np, valor, qtd) VALUES (?, ?, ?)";
    $stmt = $conn->prepare($sql);
    $stmt->bind_param("sssssssss", $np, $valor, $qtd);
 }

$sql = "SELECT id FROM Produtos";
$result = "id";
?>

<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <title>Produtos</title>
</head>
<body>
</body>
</html>
