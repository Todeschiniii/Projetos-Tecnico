<?php
require_once __DIR__ . "/../config/database.php";

class Produto {
    public static function listar() {
        $conn = Database::getConnection();
        $sql = "SELECT * FROM produtos";
        $result = $conn->query($sql);

        return $result->fetch_all(MYSQLI_ASSOC);
    }

    public static function salvar($nome, $preco) {
        $conn = Database::getConnection();
        $stmt = $conn->prepare("INSERT INTO produtos (nome, preco) VALUES (?, ?)");
        $stmt->bind_param("sd", $nome, $preco);
        return $stmt->execute();
    }

    public static function buscar($id) {
        $conn = Database::getConnection();
        $stmt = $conn->prepare("SELECT * FROM produtos WHERE id = ?");
        $stmt->bind_param("i", $id);
        $stmt->execute();
        return $stmt->get_result()->fetch_assoc();
    }
}
