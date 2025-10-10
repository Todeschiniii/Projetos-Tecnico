<?php
session_start();
include 'config.php';

if (isset($_GET["id"])) {
    $id = $_GET["id"];

    $sql = "DELETE FROM alunos WHERE id = ?";
    $stmt = $conn->prepare($sql);
    $stmt->bind_param("i", $id);

    if ($stmt->execute()) {
        header("Location: aluno.php");
        exit();
    } else {
        echo "Erro ao excluir aluno!";
    }
} else {
    header("Location: alunos.php");
    exit();
}
?>
