<?php
class Database {
    private static $host = "localhost";
    private static $user = "root";
    private static $pass = "";
    private static $db   = "loja";
    private static $conn;

    public static function getConnection() {
        if (!self::$conn) {
            self::$conn = new mysqli(self::$host, self::$user, self::$pass, self::$db);

            if (self::$conn->connect_error) {
                die("Erro de conexão: " . self::$conn->connect_error);
            }
        }
        return self::$conn;
    }
}
