<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Login</title>
    <link rel="stylesheet" href="style-image2.css">

</head>
<body class="body">


<?php
session_start();
include 'config.php';

if ($_SERVER["REQUEST_METHOD"] == "POST") {
    $email = trim($_POST["email"]);
    $senha = trim($_POST["senha"]);

    $sql = "SELECT id, nome, senha , tipo  FROM usuarios WHERE email = ?";
    $stmt = $conn->prepare($sql);
    $stmt->bind_param("s", $email);
    $stmt->execute();
    $result = $stmt->get_result();
    $usuario = $result->fetch_assoc();

    if ($usuario && password_verify($senha, $usuario["senha"])) {
        $_SESSION["usuario_id"] = $usuario["id"];
        $_SESSION["usuario_nome"] = $usuario["nome"];        
        $_SESSION['usuario_tipo'] = $usuario['tipo']; // Certifique-se de salvar o tipo

        header("Location: dashboard.php");
        exit();
    } else {
        $erro = "E-mail ou senha inválidos!";
    }
}
?>
    <header class="header">
        <div class="logo">🏋️‍♀️ Little Brother</div>
        <nav class="navbar">
            <a href="index.html">Home</a>
        </nav>
    </header>

<section class="hero">
        <div class="hero-content">
    <h1>Login</h1>
    <form action="login.php" method="post">
        <?php if (isset($erro)) echo "<p class='erro'>$erro</p>"; ?>
        <input type="email" name="email" placeholder="E-mail" required>
        <input type="password" name="senha" placeholder="Senha" required>
        <button style= "width:100%" type="submit" >Entrar</button>
    </form>
    <br>
    <a href="cadastrar_usuarios.php">Não tem uma conta? Cadastre-se</a>

</div>
</section>
    
</body>
</html>
