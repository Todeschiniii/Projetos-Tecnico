<?php
session_start();
require_once __DIR__ . "/../models/Produto.php";

class CarrinhoController {
    public static function index() {
        if (!isset($_SESSION["carrinho"])) {
            $_SESSION["carrinho"] = [];
        }
        include __DIR__ . "/../views/carrinho/index.php";
    }

    public static function adicionar() {
        $id = $_GET["id"];
        $produto = Produto::buscar($id);

        if ($produto) {
            if (!isset($_SESSION["carrinho"][$id])) {
                $_SESSION["carrinho"][$id] = [
                    "nome" => $produto["nome"],
                    "preco" => $produto["preco"],
                    "quantidade" => 1
                ];
            } else {
                $_SESSION["carrinho"][$id]["quantidade"]++;
            }
        }

        header("Location: index.php?controller=carrinho&action=index");
    }

    public static function remover() {
        $id = $_GET["id"];
        unset($_SESSION["carrinho"][$id]);
        header("Location: index.php?controller=carrinho&action=index");
    }

    public static function checkout() {
        include __DIR__ . "/../views/carrinho/checkout.php";
        $_SESSION["carrinho"] = []; // limpa carrinho após finalizar
    }
}
