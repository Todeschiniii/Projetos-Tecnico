<?php
require_once "myAPI/src/models/Produto.php";
require_once "myAPI/src/models/Categoria.php";
require_once "myAPI/src/models/Fornecedor.php";
require_once "myAPI/src/controllers/ProdutoController.php";
Class ProdutoController
{
    
    public function index(): never
    {
        $ProdutoDAO = new ProdutoDAO();
        $resposta = $ProdutoDAO->readAll();
        (new Response(
            $success = true,
            $message = 'Dados de Produtos Selecionados com sucesso',
            data: [
                'Produto' => $resposta
            ],
            httpCode:200
        ))->send();
        exit();
    }
    public function show(int $idProduto):never
    {
        $ProdutoDAO = new ProdutoDAO();
        $resposta = $ProdutoDAO->readById(idProduto: $idProduto);
        (new Response(
            success: true,
            message: 'Dados de Produto selecionados com sucesso',
            data:[
                'Produto'=> $resposta
            ],
            httpCode:200
        ))->send();
        exit();
    }
    public function store(stdClass $stdProduto): never
    {
        $Produto = new Produto();
        $Produto
            ->setNomeProduto($stdProduto->Produto->nomeProduto)
            ->setPrecoProduto($stdProduto->Produto->precoProduto)
            ->setQuantidade_EstoqueProduto($stdProduto->Produto->quantidade_estoqueProduto)
            ->setCategoriaById($stdProduto->Produto->Categoria->idCategoria)  // Novo método
            ->setFornecedorById($stdProduto->Produto->Fornecedor->idFornecedor); // Novo método
        
        $ProdutoDAO = new ProdutoDAO();
        $novoProduto = $ProdutoDAO->create($Produto);
        
        (new Response(
            success: true,
            message: 'Produto cadastrado com sucesso',
            data: [
                'Produtos' => [
                    'idProduto' => $novoProduto->getIdProduto(),
                    'nomeProduto' => $novoProduto->getNomeProduto(),
                    'precoProduto' => $novoProduto->getPrecoProduto(),
                    'quantidade_estoqueProduto' => $novoProduto->getQuantidade_EstoqueProduto(),
                    'idCategoria' => $novoProduto->getCategoria()->getIdCategoria(),
                    'idFornecedor' => $novoProduto->getFornecedor()->getIdFornecedor()
                ]
            ],
            httpCode: 200
        ))->send();
        exit();
    }

    public function edit(stdClass $stdProduto): never
{
    try {
        $ProdutoDAO = new ProdutoDAO();
        
        // Cria o objeto Produto com os dados básicos
        $Produto = (new Produto())
            ->setIdProduto($stdProduto->Produto->idProduto)
            ->setNomeProduto($stdProduto->Produto->nomeProduto)
            ->setPrecoProduto((float)$stdProduto->Produto->precoProduto)
            ->setQuantidade_EstoqueProduto((int)$stdProduto->Produto->quantidade_estoqueProduto);
        
        // Configura a Categoria (usando o método setCategoriaById que criamos anteriormente)
        if (isset($stdProduto->Produto->Categoria->idCategoria)) {
            $Produto->setCategoriaById($stdProduto->Produto->Categoria->idCategoria);
        }
        
        // Configura o Fornecedor (usando o método setFornecedorById que criamos anteriormente)
        if (isset($stdProduto->Produto->Fornecedor->idFornecedor)) {
            $Produto->setFornecedorById($stdProduto->Produto->Fornecedor->idFornecedor);
        }
        
        // Atualiza o produto
        if ($ProdutoDAO->update($Produto)) {
            (new Response(
                success: true,
                message: "Produto atualizado com sucesso",
                data: [
                    'Produtos' => [
                        'idProduto' => $Produto->getIdProduto(),
                        'nomeProduto' => $Produto->getNomeProduto(),
                        'precoProduto' => $Produto->getPrecoProduto(),
                        'quantidade_estoqueProduto' => $Produto->getQuantidade_EstoqueProduto(),
                        'idCategoria' => $Produto->getCategoria()->getIdCategoria(),
                        'idFornecedor' => $Produto->getFornecedor()->getIdFornecedor()
                    ]
                ],
                httpCode: 200
            ))->send();
        } else {
            (new Response(
                success: false,
                message: "Não foi possível atualizar o Produto",
                error: [
                    'code' => 'update_error',
                    'message' => 'Erro ao atualizar o produto no banco de dados'
                ],
                httpCode: 400
            ))->send();
        }
    } catch (Throwable $e) {
        (new Response(
            success: false,
            message: "Erro na atualização do Produto",
            error: [
                'code' => 'internal_error',
                'message' => $e->getMessage()
            ],
            httpCode: 500
        ))->send();
    }
    
    exit();
}

   public function destroy(int $idProduto): never
{
    try {
        $ProdutoDAO = new ProdutoDAO();
        
        if ($ProdutoDAO->delete($idProduto)) {
            (new Response(httpCode: 204))->send();
        } else {
            (new Response(
                success: false,
                message: 'Não foi possível excluir o Produto',
                error: [
                    'code' => 'delete_error',
                    'message' => 'Produto não encontrado ou já removido'
                ],
                httpCode: 404
            ))->send();
        }
    } catch (Throwable $e) {
        (new Response(
            success: false,
            message: 'Erro na exclusão do Produto',
            error: [
                'code' => 'database_error',
                'message' => $e->getMessage()
            ],
            httpCode: 500
        ))->send();
    }
    exit();
}
}
?>