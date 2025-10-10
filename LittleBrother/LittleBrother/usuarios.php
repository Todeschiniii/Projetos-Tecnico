<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Usuários</title>
    <link rel="stylesheet" href="styles.css">
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.8/dist/css/bootstrap.min.css" rel="stylesheet" integrity="sha384-sRIl4kxILFvY47J16cr9ZwB07vP4J8+LH7qKQnuqkuIAvNWLzeN8tE5YBujZqJLB" crossorigin="anonymous">

</head>

<body style="background-color: #111;">

<?php
session_start();

include 'config.php';
include 'verifica_admin.php';

// Excluir usuário, se solicitado
if (isset($_GET["delete"])) {
    $id = $_GET["delete"];
    $sql = "DELETE FROM usuarios WHERE id = ?";
    $stmt = $conn->prepare($sql);
    $stmt->bind_param("i", $id);
    $stmt->execute();
    header("Location: usuarios.php");
    exit();
}

// Buscar todos os usuários
$sql = "SELECT id, nome, email FROM usuarios";
$result = $conn->query($sql);
?>

<?php 
if (!empty($_GET['email'])) {
if (isset($_GET['email'])) {

        $email = $_GET['email'];
        $email_like = "%" . $email . "%";

        $stmt = $conn->prepare("SELECT id, nome, email FROM usuarios WHERE email LIKE ?");
        $stmt->bind_param("s", $email_like);
        $stmt->execute();
        $result = $stmt->get_result();
}
} else {
    $sql = "SELECT id, nome, email FROM usuarios";
    $result = $conn->query($sql);
}
?>
    <section class="hero">
    <div class="hero-content">
<h1 style = "color: rgb(139, 41, 41);"><strong>Lista de Usuários</strong></h1>

    <table class="table table-dark table-striped">
        <tr>
            <th>Nome</th>
            <th>Email</th>
            <th>Ações</th>
        </tr>
            <tr>
     <form method="GET" action="usuarios.php">
    <td><label for="email">Email:</label></td><td>
        <input class="button" type="text" name="email" id="email" placeholder="teste@email.com" ></td><td>
        <button class="button" type="submit">Buscar</button></td>
    </tr>
        <?php while ($row = $result->fetch_assoc()) { ?>
            <tr>
                <td><?php echo htmlspecialchars($row["nome"]); ?></td>
                <td><?php echo htmlspecialchars($row["email"]); ?></td>
                <td>
                    <a class='button-link' href="editar_usuario.php?id=<?php echo $row['id']; ?>">Editar</a>
                    <a class='button-link' href="usuarios.php?delete=<?php echo $row['id']; ?>" onclick="return confirm('Tem certeza que deseja excluir?')">Excluir</a>
                </td>
            </tr>
        <?php } ?>
        </form>
        </table>
    <a href= "dashboard.php"class='button-link'>Voltar ao Dashboard</a>
    </div>
    </section>
</body>
</html>

