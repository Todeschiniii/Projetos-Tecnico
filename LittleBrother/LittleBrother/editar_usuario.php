<?php
session_start();
include 'config.php';

if (!isset($_GET["id"])) {
    header("Location: usuarios.php");
    exit();
}

$id = $_GET["usuario_id"];
$sql = "SELECT * FROM usuarios WHERE id = ?";
$stmt = $conn->prepare($sql);
$stmt->bind_param("i", $id);
$stmt->execute();
$result = $stmt->get_result();
$usuario = $result->fetch_assoc();

if ($_SERVER["REQUEST_METHOD"] == "POST") {
    $nome = trim($_POST["nome"]);
    $email = trim($_POST["email"]);

    $sql = "UPDATE usuarios SET nome = ?, email = ? senha = ? WHERE id = ?";
    $stmt = $conn->prepare($sql);
    $stmt->bind_param("ssi", $nome, $email, $id);

    if ($stmt->execute()) {
        header("Location: usuarios.php");
        exit();
    } else {
        $erro = "Erro ao atualizar!";
    }
}
?>

<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <title>Editar Usuário</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.8/dist/css/bootstrap.min.css" rel="stylesheet" integrity="sha384-sRIl4kxILFvY47J16cr9ZwB07vP4J8+LH7qKQnuqkuIAvNWLzeN8tE5YBujZqJLB" crossorigin="anonymous">
</head>
<body>

    <h1>Editar Usuário</h1>
    <?php if (isset($erro)) echo "<p style='color:red;'>$erro</p>"; ?>
    <form action="editar_usuario.php?id=<?= $id ?>" method="post">
        <input type="text" name="nome" value="<?= htmlspecialchars($usuario["nome"]) ?>" required>
        <input type="email" name="email" value="<?= htmlspecialchars($usuario["email"]) ?>" required>
        <input type="text" name="senha" value="<?= htmlspecialchars($usuario["senha"]) ?>" required>
        <button type="submit">Salvar</button>
    </form>
    <a href="usuarios.php">Voltar</a>
</body>
</html>
