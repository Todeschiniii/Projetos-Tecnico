<?php
$senha_hash = password_hash('senha123', PASSWORD_DEFAULT);
echo "Senha Hash: " . $senha_hash;
?>
