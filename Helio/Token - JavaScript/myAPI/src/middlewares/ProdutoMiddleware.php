<?php
require_once "myAPI/src/DAO/ProdutoDAO.php";
require_once "myAPI/src/http/Response.php";
Class ProdutoMiddleware
{
    public function stringJsonToStdClass($requestBody): stdClass
{
    $stdProduto = json_decode($requestBody);

    // Verifica JSON inválido
    if (json_last_error() !== JSON_ERROR_NONE) {
        (new Response(
            success: false,
            message: 'Produto inválido',
            error: [
                'code' => 'validation_error',
                'mensagem' => 'JSON inválido'
            ],
            httpCode: 400
        ))->send();
        exit();
    }

    // Verifica objeto Produto
    if (!isset($stdProduto->Produto)) {
        (new Response(
            success: false,
            message: 'Produto inválido',
            error: [
                'code' => 'validation_error',
                'mensagem' => 'Não foi enviado o objeto Produto'
            ],
            httpCode: 400
        ))->send();
        exit();
    }

    // Campos obrigatórios para criação
    $requiredFields = [
        'nomeProduto' => 'Nome do Produto',
        'precoProduto' => 'Preço do Produto',
        'quantidade_estoqueProduto' => 'Quantidade em Estoque',
        'Categoria' => 'Categoria',
        'Fornecedor' => 'Fornecedor'
    ];

    foreach ($requiredFields as $field => $name) {
        if (!isset($stdProduto->Produto->$field)) {
            (new Response(
                success: false,
                message: 'Produto inválido',
                error: [
                    'code' => 'validation_error',
                    'mensagem' => "Campo obrigatório não enviado: {$name}"
                ],
                httpCode: 400
            ))->send();
            exit();
        }
    }

    // Verifica ID da categoria
    if (!isset($stdProduto->Produto->Categoria->idCategoria)) {
        (new Response(
            success: false,
            message: 'Produto inválido',
            error: [
                'code' => 'validation_error',
                'mensagem' => 'ID da Categoria não enviado'
            ],
            httpCode: 400
        ))->send();
        exit();
    }

    // Verifica ID do fornecedor
    if (!isset($stdProduto->Produto->Fornecedor->idFornecedor)) {
        (new Response(
            success: false,
            message: 'Produto inválido',
            error: [
                'code' => 'validation_error',
                'mensagem' => 'ID do Fornecedor não enviado'
            ],
            httpCode: 400
        ))->send();
        exit();
    }

    return $stdProduto;
}
    public function IsValidId($idProduto) : self
    {
        if(!isset($idProduto))
        {
            (new Response(
                success: true,
                message:"",
                error: [
                    'code' => 'Produto_validation_error',
                    'message'=> 'O Id fornecido nao é valido!'
                ],
                httpCode: 400
            ))->send();
            exit();
        }else if(!is_numeric(value: $idProduto))
        {
             (new Response(
                success: true,
                message:"",
                error: [
                    'code' => 'Produto_validation_error',
                    'message'=> 'O Id fornecido nao é um número!'
                ],
                httpCode: 400
            ))->send();
            exit();
        }else if($idProduto <= 0)
        {
            (new Response(
                success: true,
                message:"",
                error: [
                    'code' => 'Produto_validation_error',
                    'message'=> 'O Id fornecido deve ser maior que 0!'
                ],
                httpCode: 400
            ))->send();
            exit();
        }else{
            return $this;
        }
    }
    public function IsValidNomeProduto($nomeProduto): self
    {
        if (!isset($nomeProduto)) {  // Verifica se o atributo "nomeProduto" existe
            (new Response(
                success: false,
                message: 'Produto inválido',
                error: [
                    'code' => 'validation_error',
                    'mesagem' => 'Nome do cargo não enviado'
                ],
                httpCode: 400
            ))->send();
            exit();
        }else if(strlen(string: $nomeProduto) < 2)
        {
            (new Response(
                success: false,
                message: 'Produto inválido',
                error: [
                    'code' => 'validation_error',
                    'mesagem' => 'Nome do cargo deve ter mais de 1 letras'
                ],
                httpCode: 400
            ))->send();
            exit();
        }
        return $this;
    }
    public function IsValidprecoProduto($precoProduto): self
    {
        if (!isset($precoProduto)) {  // Verifica se o atributo "nomeProduto" existe
            (new Response(
                success: false,
                message: 'Produto inválido',
                error: [
                    'code' => 'validation_error',
                    'mesagem' => 'Preço do Produto não enviado'
                ],
                httpCode: 400
            ))->send();
            exit();
        }else if(!is_numeric(value: $precoProduto))
        {
             (new Response(
                success: true,
                message:"",
                error: [
                    'code' => 'Produto_validation_error',
                    'message'=> 'O Preço fornecido nao é um número!'
                ],
                httpCode: 400
            ))->send();
            exit();
        }
        return $this;
    }
   public function IsValidQuantidade_EstoqueProduto($quantidade_estoqueProduto): self
{
    if (!isset($quantidade_estoqueProduto)) {
        (new Response(
            success: false,
            message: 'Produto inválido',
            error: [
                'code' => 'validation_error',
                'mensagem' => 'Quantidade em estoque não enviada'
            ],
            httpCode: 400
        ))->send();
        exit();
    } else if(!is_numeric($quantidade_estoqueProduto)) {
        (new Response(
            success: false,
            message: 'Produto inválido',
            error: [
                'code' => 'validation_error',
                'mensagem' => 'A quantidade em estoque deve ser um número'
            ],
            httpCode: 400
        ))->send();
        exit();
    } else if($quantidade_estoqueProduto < 0) {
        (new Response(
            success: false,
            message: 'Produto inválido',
            error: [
                'code' => 'validation_error',
                'mensagem' => 'A quantidade em estoque não pode ser negativa'
            ],
            httpCode: 400
        ))->send();
        exit();
    }
    return $this;
}
    public function IsValidCategoria(Categoria $Categoria) : self
    {
        if (!isset($Categoria)) { 
            (new Response(
                success: false,
                message: 'Produto inválido',
                error: [
                    'code' => 'validation_error',
                    'mesagem' => 'quantidade_estoque de Produtos não enviado'
                ],
                httpCode: 400
            ))->send();
            exit();
        }
        return $this;
    }
    public function IsValidFornecedor(Fornecedor $Fornecedor) : self
    {
        if (!isset($Fornecedor)) { 
            (new Response(
                success: false,
                message: 'Produto inválido',
                error: [
                    'code' => 'validation_error',
                    'mesagem' => 'quantidade_estoque de Produtos não enviado'
                ],
                httpCode: 400
            ))->send();
            exit();
        }
        return $this;
    }
}