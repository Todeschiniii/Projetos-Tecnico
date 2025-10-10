<!doctype html>
<html lang="pt-BR">
<head>
  <meta charset="utf-8">
  <title>Formulário</title>
      <link rel="stylesheet" href="style-image.css">
</head>
<body >
 <section class="hero">
        <div class="hero-content">
  <form action="salvar.php" method="post">
    <label>Produto:<br><input type="text" name="np" required></label><br>
    <label>Valor:<br><input type="number" name="valor" required></label><br>
    <label>Quantidade:<br><input type="number" name="qtd" required></label><br>
    <button type="submit">Enviar</button>
  </form>
</div>
</section>
<a href="index.html" class="button-link">Voltar</a>
</body>
</html>