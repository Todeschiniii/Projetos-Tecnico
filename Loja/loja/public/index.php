<?php

$controller = $_GET["controller"] ?? "produto";
$action = $_GET["action"] ?? "index";

$controllerClass = ucfirst($controller) . "Controller";
require_once __DIR__ . "/../app/controllers/" . $controllerClass . ".php";

$controllerClass::$action();
