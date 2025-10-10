<?php
session_start();
include 'config.php';

if ($_SERVER["REQUEST_METHOD"] == "POST") {
    $nome = trim($_POST["nome"]);
    $email = trim($_POST["email"]);
    $senha = password_hash($_POST["senha"], PASSWORD_DEFAULT);

    $sql = "INSERT INTO usuarios (nome, email, senha) VALUES (?, ?, ?)";
    $stmt = $conn->prepare($sql);
    $stmt->bind_param("sss", $nome, $email, $senha);

    if ($stmt->execute()) {
        header("Location: login.php");
        exit();
    } else {
        $erro = "Erro ao cadastrar. Tente outro e-mail!";
    }
}
?>

<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <title>Cadastrar Usuário</title>
</head>

<body class="body">
        <section class="hero">
    <div class="hero-content">
        <link rel="stylesheet" href="style-image.css">

    <h1 class="titulo">Cadastrar Novo Usuário</h1>
    <?php if (isset($erro)) echo "<p style='color:red;'>$erro</p>"; ?>
    <form action="cadastrar_usuarios.php" method="post">
        <input type="text" name="nome" placeholder="Nome" required>
        <input type="email" name="email" placeholder="E-mail" required>
        <input type="password" name="senha" placeholder="Senha" required>
        <button style='width: 100%' type="submit">Cadastrar</button>
    </form>
    <br>
    <a class="button-link" href="dashboard.php">Voltar</a>
</div>
</section>
</body>
</html>
