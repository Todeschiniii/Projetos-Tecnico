<h2>Cadastrar Produto</h2>
<form method="post" action="index.php?controller=produto&action=salvar">
    Nome: <input type="text" name="nome" required><br>
    Preço: <input type="number" step="0.01" name="preco" required><br>
    <button type="submit">Salvar</button>
</form>
