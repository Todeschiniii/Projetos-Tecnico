<?php
session_start();

include 'config.php';

if (isset($_GET["id"])) {
    $id = $_GET["id"];
    
    $sql = "SELECT nome, dtnasc, genero, cpf, cep, endereco, telefone, email, plano FROM alunos WHERE id = ?";
    $stmt = $conn->prepare($sql);
    $stmt->bind_param("i", $id);
    $stmt->execute();
    $result = $stmt->get_result();
    $usuario = $result->fetch_assoc();
}

if ($_SERVER["REQUEST_METHOD"] == "POST") {
    $id = $_POST["id"];
    $nome = trim($_POST["nome"]);
    $datanasc = trim($_POST["dtnasc"]);
    $genero = trim($_POST["genero"]);
    $cpf = trim($_POST["cpf"]);
    $cep = trim($_POST["cep"]);
    $endereco = trim($_POST["endereco"]);
    $telefone = trim($_POST["telefone"]);
    $email = trim($_POST["email"]);
    $plano = trim($_POST["plano"]);

    $sql = "UPDATE alunos SET nome = ?, dtnasc = ?, genero = ?, cpf = ?, cep = ?, endereco = ?, telefone = ?, email = ?, plano = ? WHERE id = ?";
    $stmt = $conn->prepare($sql);
    $stmt->bind_param("ssssssssss", $nome, $datanasc, $genero, $cpf, $cep, $endereco, $telefone, $email, $plano, $id);
    
    if ($stmt->execute()) {
        header("Location: alunos.php");
        exit();
    } else {
        echo "Erro ao atualizar.";
    }
}
?>

<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Editar Usuário</title>
    <link rel="stylesheet" href="css/styles.css">
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.8/dist/css/bootstrap.min.css" rel="stylesheet" integrity="sha384-sRIl4kxILFvY47J16cr9ZwB07vP4J8+LH7qKQnuqkuIAvNWLzeN8tE5YBujZqJLB" crossorigin="anonymous">

    <style>
        
            body{
      text-align:center;
      height:100vh;
      margin:0;
        }
         form {
      text-align:center;
      border-radius: 8px;
        }
        table, tr, td {
        text-align:justify;
        }
        
        </style>
</head>
<body>
                <body style="background-color:powderblue;">

    <h1>Editar Usuário</h1>
    <form action="editar.php" method="post">
        <table class="table table-dark table-striped">
        <tr>
        <td>   
        <input type="hidden" name="id" value="<?php echo $id; ?>">
        <label>Nome:</label></td><td>
        <input type="text" name="nome" value="<?php echo htmlspecialchars($usuario['nome']); ?>" required></td>
        </tr>
        <tr>
        <td>
        <label>Data de Nascimento:</label></td><td>
        <input type="date" name="dtnasc" value="<?php echo htmlspecialchars($usuario['dtnasc']); ?>" required></td>
        </tr>
        <tr>
        <td>
        <label>Gênero:</label></td><td>
        <input type="text" name="genero" value="<?php echo htmlspecialchars($usuario['genero']); ?>" required></td>
        </tr>
        <tr>
        <td>
        <label>Cpf:</label></td><td>
        <input type="number" name="cpf" value="<?php echo htmlspecialchars($usuario['cpf']); ?>" required></td>
        </tr>
        <tr>
        <td>
        <label>Cep:</label></td><td>
        <input type="number" name="cep" value="<?php echo htmlspecialchars($usuario['cep']); ?>" required></td>
        </tr>
        <tr>
        <td>
        <label>Endereço:</label></td><td>
        <input type="text" name="endereco" value="<?php echo htmlspecialchars($usuario['endereco']); ?>" required></td>
        </tr>
        <tr>
        <td>
        <label>Telefone:</label></td><td>
        <input type="number" name="telefone" value="<?php echo htmlspecialchars($usuario['telefone']); ?>" required></td>
        </tr>
        <tr>
        <td>
        <label>Email:</label></td><td>
        <input type="text" name="email" value="<?php echo htmlspecialchars($usuario['email']); ?>" required></td>
        </tr>
        <tr>
        <td>
        <label>Plano:</label></td><td>
        <input type="text" name="plano" value="<?php echo htmlspecialchars($usuario['plano']); ?>" required></td>
        </tr>
        <br>
    </table>
        <button class="btn btn-dark" type="submit">Salvar Alterações</button>
    </form>

    <br>
    <a class="btn btn-dark" href="alunos.php">Voltar</a>
</body>
</html>
