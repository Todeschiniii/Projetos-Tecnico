<!DOCTYPE html>
<html lang="en">
<head>
    <title>Crud</title>
  <link rel="icon" type="image/x-icon" href="https://static.thenounproject.com/png/79156-200.png">
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Document</title>
    <link rel="stylesheet" href="style2.css">
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
<body style="background-color:#111;">
 <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.7/dist/css/bootstrap.min.css" rel="stylesheet" integrity="sha384-LN+7fdVzj6u52u30Kp6M/trliBMCMKTyK833zpbD+pXdCLuTusPj697FH4R/5mcr" crossorigin="anonymous">
 <header class="header">
        <div class="logo">🏋️‍♀️ Little Brother</div>
        <nav class="navbar">
            <a href="index.html">Home</a>
        </nav>
    </header>
        <section class="hero">
      <div class="hero-content">
 <form method="POST" action="cadastrar_aluno.php">
    <h1 style="color:rgb(139, 41, 41);"><strong>Little Brother</strong></h1>
    <table class="table table-dark table-striped">
        <tr>
        <td>
        <label>Nome</label ></td><td>
        <input type="text" name="nome" required>
        </tr>
        <tr>
        <td>
        <label>Data de Nascimento</label></td><td>
        <input type="date" name="dtnasc" required></td>
        </tr>
        <tr>
        <td>
        <label>Gênero</label></td><td>
        <select name="genero" id="genero" required>
        <option value="Masculino">Masculino</option>
        <option value="Feminino">Feminino</option>
        <option value="Outro">Outro</option>
        <option value="Prefiro Não Responder">Prefiro Não Responder</option>
        </select></td>
        </tr>
        <tr>
        <td>
        <label>CPF</label></td><td>
        <input type="number" name="cpf" required></td>
        </tr>
        <tr>
        <td>
        <label>CEP</label></td><td>
        <input type="number" name="cep" required></td>
        </tr>
        <tr>
        <td>
        <label>Endereço</label></td><td>
        <input type="text" name="endereco" required></td>
        </tr>
        <tr>
        <td>
        <label>Telefone-Celular</label></td><td>
        <input type="number" name="telefone" required></td>
        </tr>
        <tr>
        <td>
        <label>Email</label></td><td>
        <input type="Email" name="email" required></td>
        </tr>
        <tr>
        <td>
        <label>Plano</label></td><td>
        <select name="plano" id="plano" >
        <option value="Mensal">Mensal</option>
        <option value="Bimestral">Bimestral</option>
        <option value="Trimestral">Trimestral</option>
        <option value="Semestral">Semestral</option>
        <option value="Anual">Anual</option>
        </select></td></tr>

        </table>
        <input class="button-link" type="submit">
        <a class="button-link" href="dashboard.php">Voltar</a>
      </div>
    </form>
      </section>
</body>
</html>