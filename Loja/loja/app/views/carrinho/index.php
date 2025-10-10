<h2>Carrinho de Compras</h2>
<?php if (empty($_SESSION["carrinho"])): ?>
    <p>Carrinho vazio!</p>
<?php else: ?>
    <table border="1" cellpadding="8">
        <tr><th>Produto</th><th>Preço</th><th>Qtd</th><th>Subtotal</th><th>Ação</th></tr>
        <?php $total = 0; ?>
        <?php foreach($_SESSION["carrinho"] as $id => $item): ?>
            <tr>
                <td><?= $item["nome"] ?></td>
                <td>R$ <?= number_format($item["preco"], 2, ',', '.') ?></td>
                <td><?= $item["quantidade"] ?></td>
                <td>R$ <?= number_format($item["preco"] * $item["quantidade"], 2, ',', '.') ?></td>
                <td><a href="index.php?controller=carrinho&action=remover&id=<?= $id ?>">Remover</a></td>
            </tr>
            <?php $total += $item["preco"] * $item["quantidade"]; ?>
        <?php endforeach; ?>
        <tr>
            <td colspan="3"><b>Total</b></td>
            <td colspan="2">R$ <?= number_format($total, 2, ',', '.') ?></td>
        </tr>
    </table>
    <a href="index.php?controller=carrinho&action=checkout">Finalizar Compra</a>
<?php endif; ?>
