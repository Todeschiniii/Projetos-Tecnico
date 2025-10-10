<h2>Lista de Produtos</h2>
<a href="index.php?controller=produto&action=cadastro">Cadastrar Produto</a>
<table border="1" cellpadding="8">
    <tr><th>ID</th><th>Nome</th><th>Preço</th><th>Ação</th></tr>
    <?php foreach($produtos as $p): ?>
        <tr>
            <td><?= $p["id"] ?></td>
            <td><?= $p["nome"] ?></td>
            <td>R$ <?= number_format($p["preco"], 2, ',', '.') ?></td>
            <td><a href="index.php?controller=carrinho&action=adicionar&id=<?= $p["id"] ?>">Adicionar ao Carrinho</a></td>
        </tr>
    <?php endforeach; ?>
</table>
<a href="index.php?controller=carrinho&action=index">Ver Carrinho</a>
