<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Usuários</title>
    <link rel="stylesheet" href="styles.css">

</head>

<body style="background-color: #111;">

<?php
session_start();

include 'config.php';
include 'verifica_admin.php';

// Excluir usuário, se solicitado
if (isset($_GET["delete"])) {
    $id = $_GET["delete"];
    $sql = "DELETE FROM alunos WHERE id = ?";
    $stmt = $conn->prepare($sql);
    $stmt->bind_param("i", $id);
    $stmt->execute();
    header("Location: alunos.php");
    exit();
}

// Buscar todos os usuários
$sql = "SELECT id, nome, cpf, plano FROM alunos";
$result = $conn->query($sql);
?>

<?php 
if (!empty($_GET['cpf'])) {
if (isset($_GET['cpf'])) {

        $cpf = $_GET['cpf'];
        $cpf_like = "%" . $cpf . "%";

        $stmt = $conn->prepare("SELECT id, nome, cpf, plano FROM alunos WHERE cpf LIKE ?");
        $stmt->bind_param("s", $cpf_like);
        $stmt->execute();
        $result = $stmt->get_result();
}
} else {
    $sql = "SELECT id, nome, cpf, plano FROM alunos";
    $result = $conn->query($sql);
}
?>
    <section class="hero">
    <div class="hero-content">
<h1 style = "color: rgb(139, 41, 41);"><strong>Lista de Usuários</strong></h1>

    <table class="table table-dark table-striped">
        <tr>
            <th>Nome</th>
            <th>Cpf</th>
            <th>Plano</th>
            <th>Ações</th>
        </tr>
            <tr>
     <form method="GET" action="alunos.php">
    <td><label for="cpf">CPF:</label></td><td>
        <input class="button" type="text" name="cpf" id="cpf" placeholder="000.000.000-00" ></td><td>
        </td><td>
        <button class="button" type="submit">Buscar</button></td>
    </tr>
        <?php while ($row = $result->fetch_assoc()) { ?>
            <tr>
                <td><?php echo htmlspecialchars($row["nome"]); ?></td>
                <td><?php echo htmlspecialchars($row["cpf"]); ?></td>
                <td><?php echo htmlspecialchars($row["plano"]); ?></td>
                <td>
                    <a class='button-link' href="editar.php?id=<?php echo $row['id']; ?>">Editar</a>
                    <a class='button-link' href="alunos.php?delete=<?php echo $row['id']; ?>" onclick="return confirm('Tem certeza que deseja excluir?')">Excluir</a>
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

