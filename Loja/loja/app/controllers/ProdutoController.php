<?php
require_once __DIR__ . "/../models/Produto.php";

class ProdutoController {
    public static function index() {
        $produtos = Produto::listar();
        include __DIR__ . "/../views/produtos/index.php";
    }

    public static function cadastro() {
        include __DIR__ . "/../views/produtos/cadastro.php";
    }

    public static function salvar() {
        $nome = $_POST["nome"];
        $preco = $_POST["preco"];
        Produto::salvar($nome, $preco);
        header("Location: index.php?controller=produto&action=index");
    }
}
