<?php
require_once "myAPI/src/DAO/CategoriaDAO.php";
require_once "myAPI/src/http/Response.php";
Class CategoriaMiddleware
{
    public function IsValidId($idCategoria) : self
    {
        if(!isset($idCategoria))
        {
            (new Response(
                success: true,
                message:"",
                error: [
                    'code' => 'Categoria_validation_error',
                    'message'=> 'O Id fornecido nao é valido!'
                ],
                httpCode: 400
            ))->send();
            exit();
        }else if(!is_numeric(value: $idCategoria))
        {
             (new Response(
                success: true,
                message:"",
                error: [
                    'code' => 'Categoria_validation_error',
                    'message'=> 'O Id fornecido nao é um número!'
                ],
                httpCode: 400
            ))->send();
            exit();
        }else if($idCategoria <= 0)
        {
            (new Response(
                success: true,
                message:"",
                error: [
                    'code' => 'Categoria_validation_error',
                    'message'=> 'O Id fornecido deve ser maior que 0!'
                ],
                httpCode: 400
            ))->send();
            exit();
        }else{
            return $this;
        }
    }
    public function stringJsonToStdClass($requestBody): stdClass
    {
        // Decodifica o JSON para um objeto stdClass
        $stdCategoria = json_decode(json: $requestBody);

        // Verifica se houve erro na decodificação (JSON inválido)
        if (json_last_error() !== JSON_ERROR_NONE) {
            (new Response(
                success: false,
                message: 'Categoria inválido',
                error: [
                    'code' => 'validation_error',
                    'mesagem' => 'Json inválido'
                ],
                httpCode: 400
            ))->send();
            exit();
        } else if (!isset($stdCategoria->Categoria)) {  // Verifica se o objeto "Categoria" existe
            (new Response(
                success: false,
                message: 'Categoria inválido',
                error: [
                    'code' => 'validation_error',
                    'mesagem' => 'Não foi enviado o objeto Categoria'
                ],
                httpCode: 400
            ))->send();
            exit();
        } else if (!isset($stdCategoria->Categoria->nomeCategoria)) {  // Verifica se o atributo "nomeCategoria" existe
            (new Response(
                success: false,
                message: 'Categoria inválido',
                error: [
                    'code' => 'validation_error',
                    'mesagem' => 'Não foi eniado o atributo nomeCategoria do Categoria'
                ],
                httpCode: 400
            ))->send();
            exit();
        }
        return $stdCategoria;
    }
    public function IsValidNomeCategoria($nomeCategoria): self
    {
        if (!isset($nomeCategoria)) {  // Verifica se o atributo "nomeCategoria" existe
            (new Response(
                success: false,
                message: 'Categoria inválido',
                error: [
                    'code' => 'validation_error',
                    'mesagem' => 'Nome do cargo não enviado'
                ],
                httpCode: 400
            ))->send();
            exit();
        }else if(strlen(string: $nomeCategoria) < 4)
        {
            (new Response(
                success: false,
                message: 'Categoria inválido',
                error: [
                    'code' => 'validation_error',
                    'mesagem' => 'Nome do cargo deve ter mais de 3 letras'
                ],
                httpCode: 400
            ))->send();
            exit();
        }
        return $this;
    }
    public function hasNotCategoriaByName($nomeCategoria): self
    {
        $CategoriaDAO = new CategoriaDAO();
        $Categoria = $CategoriaDAO->readByName($nomeCategoria);
        if(isset($Categoria))
        {
            (new Response(
                success: false,
                message: 'Categoria inválido',
                error: [
                    'code' => 'validation_error',
                    'mesagem' => 'Já existe uma Categoria cadastrada com esse nome($nomeCategoria)'
                ],
                httpCode: 400
            ))->send();
            exit();
        }
        return $this;
    }
}