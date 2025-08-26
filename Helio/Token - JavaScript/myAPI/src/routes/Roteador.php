<?php
require_once "myAPI/src/utils/Logger.php";

require_once "myAPI/src/routes/Router.php";
require_once "myAPI/src/http/Response.php";

require_once "myAPI/src/controllers/CategoriaControl.php";
require_once "myAPI/src/models/Categoria.php";
require_once "myAPI/src/middlewares/CategoriaMiddleware.php";

require_once "myAPI/src/controllers/FornecedorControl.php";
require_once "myAPI/src/middlewares/FornecedorMiddleware.php";
require_once "myAPI/src/models/Fornecedor.php";

require_once "myAPI/src/middlewares/ProdutoMiddleware.php";
require_once "myAPI/src/models/Produto.php";
require_once "myAPI/src/controllers/ProdutoController.php";    
class Roteador
{
    public function __construct(private Router $router = new Router())
    {
        $this->setupHeaders();
        $this->setupCategoriaRoutes();
        $this->setupProdutoRoutes();
        $this->setupFornecedorRoutes();
        // $this->setupBackupRoutes();
        $this->setup404Route();
    }

    private function setup404Route(): void
    {
        $this->router->set404(match_fn: function (): void {
            header(header: 'Content-Type: application/json');
            (new Response(
                success: false,
                message: "Rota não encontrada",
                error: [
                    'code' => 'routing_error',
                    'message' => 'Rota não mapeada'
                ],
                httpCode: 404 
            ))->send();

        });
    }
    private function setupHeaders(): void
    {
        header(header: 'Access-Control-Allow-Methods: GET, POST, PUT, DELETE');
        header(header: 'Access-Control-Allow-Origin: *');
        header(header: 'Access-Control-Allow-Headers: Content-Type, Authorization');
    }
    private function sendErrorResponse(Throwable $throwable, string $message): never
    {
        Logger::Log(throwable: $throwable);
        (new Response(
            success: false,
            message: $message,
            error: [
                'code' => $throwable->getCode(),
                'message' => $throwable->getMessage()
            ],
            httpCode: 500 
        ))->send();

        exit();
    }
    private function setupCategoriaRoutes(): void
    {
        $this->router->get(pattern: '/categorias', fn: function (): never {
            try {
                (new CategoriaControl())->index();

            } catch (Throwable $throwable) {
                $this->sendErrorResponse(
                    throwable: $throwable,
                    message: 'Erro na seleção de dados da Categoria'
                );
            }
            exit();
        });
        $this->router->get(pattern: '/categorias/(\d+)', fn: function ($idCategoria): never {
    try {
        // Validação do ID
        (new CategoriaMiddleware())->IsValidId(idCategoria: $idCategoria);
        
        // Tenta buscar a categoria
        $categoriaDAO = new CategoriaDAO();
        $categoriaData = $categoriaDAO->readById(idCategoria: $idCategoria);
        
        if (empty($categoriaData)) {
            (new Response(
                success: false,
                message: 'Categoria não encontrada',
                error: [
                    'code' => 'not_found',
                    'message' => 'Nenhuma categoria encontrada com o ID fornecido'
                ],
                httpCode: 404
            ))->send();
            exit();
        }
        
        // Se encontrou, chama o controller normalmente
        (new CategoriaControl())->show(idCategoria: $idCategoria);
        
    } catch (Throwable $throwable) {
        $this->sendErrorResponse(
            throwable: $throwable,
            message: 'Erro ao buscar categoria',
            httpCode: 500
        );
    }
    exit();
});
        $this->router->post(pattern: '/categorias', fn: function (): never
        {
            try{
                $requestBody = file_get_contents(filename: "php://input");
                $CategoriaMiddleware = new CategoriaMiddleware();
                $objStd = $CategoriaMiddleware->stringJsonToStdClass(requestBody: $requestBody);
                $CategoriaMiddleware
                            ->IsValidNomeCategoria(nomeCategoria: $objStd->Categoria->nomeCategoria);
                $CategoriaControl = new CategoriaControl();
                $CategoriaControl->store(stdCategoria: $objStd);            
            }catch(Throwable $throwable){
                $this->sendErrorResponse(throwable: $throwable, message: 'Erro na seleção de Categorias');
            }
            exit();
        });
        $this->router->put(pattern: '/categorias/(\d+)', fn: function ($idProdutoCategoria):never
        {
            try{
                $requestBody = file_get_contents(filename: 'php://input');
                $CategoriaMiddleware = new CategoriaMiddleware();
                $stdCategoria = $CategoriaMiddleware->stringJsonToStdClass(requestBody: $requestBody);
                $stdCategoria->Categoria->idCategoria = $idProdutoCategoria;
                $CategoriaMiddleware
                    ->IsValidId(idCategoria: $idProdutoCategoria)
                    ->hasNotCategoriaByName(nomeCategoria: $stdCategoria->Categoria->nomeCategoria);
                $CategoriaControl = new CategoriaControl();
                $CategoriaControl->edit(stdCategoria: $stdCategoria);
            }catch(Throwable $throwable){
                $this->sendErrorResponse(throwable: $throwable, message: 'Erro na atualização de Categorias');
            }
            exit();
        });
        $this->router->delete(pattern: '/categorias/(\d+)', fn: function ($idProdutoCategoria):never
        {
            try{
                $CategoriaMiddleware = new CategoriaMiddleware();
                $CategoriaMiddleware->IsValidId(idCategoria: $idProdutoCategoria);
                $CategoriaControl = new CategoriaControl();
                $CategoriaControl->destroy(idCategoria: $idProdutoCategoria);

            }catch(Throwable $throwable)
            {
                $this->sendErrorResponse(throwable: $throwable,message:'Erro ao deletar "Categorias"');
            }
            exit();
        });
    }
    private function setupFornecedorRoutes(): void
    {
        $this->router->get(pattern: '/fornecedores', fn: function (): never
        {
            try{
                (new FornecedorControl())->index();

            } catch (Throwable $throwable){
                $this->sendErrorResponse(
                    throwable: $throwable,
                    message: 'Erro na seleção de dados do Fornecedor'
                );
            }
            exit();
        });
        $this->router->get(pattern: '/fornecedores/(\d+)', fn: function ($idFornecedor): never {
    try {
        // Validação do ID
        (new FornecedorMiddleware())->IsValidId(idFornecedor: $idFornecedor);
        
        // Tenta buscar o fornecedor
        $fornecedorDAO = new FornecedorDAO();
        $fornecedorData = $fornecedorDAO->readById(idFornecedor: $idFornecedor);
        
        if (empty($fornecedorData)) {
            (new Response(
                success: false,
                message: 'Fornecedor não encontrado',
                error: [
                    'code' => 'not_found',
                    'message' => 'Nenhum fornecedor encontrado com o ID fornecido'
                ],
                httpCode: 404
            ))->send();
            exit();
        }
        
        // Se encontrou, chama o controller normalmente
        (new FornecedorControl())->show(idFornecedor: $idFornecedor);
        
    } catch (Throwable $throwable) {
        $this->sendErrorResponse(
            throwable: $throwable,
            message: 'Erro ao buscar fornecedor',
            httpCode: 500
        );
    }
    exit();
});
        $this->router->post(pattern: '/fornecedores', fn: function (): never
        {
            try{
                $requestBody = file_get_contents(filename: "php://input");
                $FornecedorMiddleware = new FornecedorMiddleware();
                $objStd = $FornecedorMiddleware->stringJsonToStdClass(requestBody: $requestBody);
                $FornecedorMiddleware
                            ->IsValidNomeFornecedor(nomeFornecedor:$objStd->Fornecedor->nomeFornecedor)
                            ->IsValidEmailFornecedor(emailFornecedor:$objStd->Fornecedor->emailFornecedor)
                            ->IsValidEnderecoFornecedor(enderecoFornecedor:$objStd->Fornecedor->enderecoFornecedor)
                            ->IsValidTelefoneFornecedor(telefoneFornecedor:$objStd->Fornecedor->telefoneFornecedor)
                            ->hasNotFornecedorByName(nomeFornecedor: $objStd->Fornecedor->nomeFornecedor);
                $FornecedorControl = new FornecedorControl();
                $FornecedorControl->store(stdFornecedor: $objStd);            
            }catch(Throwable $throwable){
                $this->sendErrorResponse(throwable: $throwable, message: 'Erro na seleção de Fornecedores');
            }
            exit();
        });
        $this->router->put(pattern: '/fornecedores/(\d+)', fn: function ($idFornecedor):never
        {
            try{
                $requestBody = file_get_contents(filename: 'php://input');
                $FornecedorMiddleware = new FornecedorMiddleware();
                $stdFornecedor = $FornecedorMiddleware->stringJsonToStdClass(requestBody: $requestBody);
                $FornecedorMiddleware
                    ->IsValidNomeFornecedor(nomeFornecedor: $stdFornecedor->Fornecedor->nomeFornecedor)
                    ->IsValidEmailFornecedor(emailFornecedor: $stdFornecedor->Fornecedor->emailFornecedor)
                    ->IsValidTelefoneFornecedor(telefoneFornecedor: $stdFornecedor->Fornecedor->telefoneFornecedor)
                    ->IsValidEnderecoFornecedor(enderecoFornecedor: $stdFornecedor->Fornecedor->enderecoFornecedor);
                $FornecedorControl = new FornecedorControl();
                $FornecedorControl->edit(stdFornecedor: $stdFornecedor);

            }catch(Throwable $throwable){
                $this->sendErrorResponse(throwable: $throwable, message: 'Erro na seleção de Fornecedores');
            }
            exit();
        });
        $this->router->delete(pattern: '/fornecedores/(\d+)', fn: function ($idFornecedor):never
        {
            try{
                $FornecedorMiddleware = new FornecedorMiddleware();
                $FornecedorMiddleware->IsValidId(idFornecedor: $idFornecedor);
                $FornecedorControl = new FornecedorControl();
                $FornecedorControl->destroy(idFornecedor: $idFornecedor);

            }catch(Throwable $throwable)
            {
                $this->sendErrorResponse(throwable: $throwable,message:'Erro ao deletar "Fornecedores"');
            }
            exit();
        });
        /*"Fornecedor": {
                    "nomeFornecedor": "higiene",
                    "telefoneFornecedor": "400244922",
                    "emailFornecedor": "daviDancuart@email.com",
                    "enderecoFornecedor": "Rua Paraibuna 811"
                }*/
    }
    private function setupProdutoRoutes(): void
    {
        $this->router->get(pattern: '/produtos',fn: function(): never 
        {
            try{
                (new ProdutoController())->index();

            } catch (Throwable $throwable){
                $this->sendErrorResponse(
                    throwable: $throwable,
                    message: 'Erro na seleção de dados do Fornecedor'
                );
            }
            exit();
        });
        $this->router->get(pattern: '/produtos/(\d+)',fn: function($idProduto): never 
        {
           try {
        // Validação do ID
        (new ProdutoMiddleware())->IsValidId(idProduto: $idProduto);
        
        // Tenta buscar o produto
        $produto = (new ProdutoDAO())->readById(idProduto: $idProduto);
        
        if (empty($produto)) {
            (new Response(
                success: false,
                message: 'Produto não encontrado',
                error: [
                    'code' => 'not_found',
                    'message' => 'Nenhum produto encontrado com o ID fornecido'
                ],
                httpCode: 404
            ))->send();
            exit();
        }
        
        // Se encontrou, chama o controller normalmente
        (new ProdutoController())->show(idProduto: $idProduto);
        
    } catch (Throwable $throwable) {
        $this->sendErrorResponse(
            throwable: $throwable,
            message: 'Erro ao buscar produto',
            httpCode: 500
        );
    }
    exit();
        });
        $this->router->post(pattern: '/produtos', fn: function(): never 
{
    try {
        $requestBody = file_get_contents('php://input');
        $ProdutoMiddleware = new ProdutoMiddleware();
        $stdProduto = $ProdutoMiddleware->stringJsonToStdClass($requestBody);
        
        $ProdutoMiddleware
            ->IsValidNomeProduto($stdProduto->Produto->nomeProduto)
            ->IsValidprecoProduto($stdProduto->Produto->precoProduto)
            ->IsValidQuantidade_EstoqueProduto($stdProduto->Produto->quantidade_estoqueProduto);
        
        $CategoriaMiddleware = new CategoriaMiddleware();
        $CategoriaMiddleware->IsValidId($stdProduto->Produto->Categoria->idCategoria);
        
        $FornecedorMiddleware = new FornecedorMiddleware();
        $FornecedorMiddleware->IsValidId($stdProduto->Produto->Fornecedor->idFornecedor);
        
        // Adicione esta parte para processar o produto
        $ProdutoController = new ProdutoController();
        $ProdutoController->store($stdProduto);
        
        exit(); // Garante que a execução termine aqui
    } catch (Throwable $throwable) {
        $this->sendErrorResponse($throwable, 'Erro na criação de Produto');
        exit();
    }
});
        
        $this->router->put(pattern: '/produtos/(\d+)', fn: function ($idProduto): never {
    try {
        $requestBody = file_get_contents('php://input');
        $ProdutoMiddleware = new ProdutoMiddleware();
        $stdProduto = $ProdutoMiddleware->stringJsonToStdClass($requestBody);

        // Verifica e corrige nomes de campos
        if (isset($stdProduto->Produto->homeProduto)) {
            $stdProduto->Produto->nomeProduto = $stdProduto->Produto->homeProduto;
        }
        if (isset($stdProduto->Produto->precorroduto)) {
            $stdProduto->Produto->precoProduto = $stdProduto->Produto->precorroduto;
        }

        // Validações
        $ProdutoMiddleware
            ->IsValidId($idProduto)
            ->IsValidNomeProduto($stdProduto->Produto->nomeProduto)
            ->IsValidPrecoProduto($stdProduto->Produto->precoProduto)
            ->IsValidQuantidade_EstoqueProduto($stdProduto->Produto->quantidade_estoqueProduto);

        // Normaliza nomes de campos relacionados
        if (isset($stdProduto->Produto->categoria)) {
            $stdProduto->Produto->Categoria = $stdProduto->Produto->categoria;
            if (isset($stdProduto->Produto->Categoria->idcategoria)) {
                $stdProduto->Produto->Categoria->idCategoria = $stdProduto->Produto->Categoria->idcategoria;
            }
        }

        if (isset($stdProduto->Produto->Fornecedor->idfornecedor)) {
            $stdProduto->Produto->Fornecedor->idFornecedor = $stdProduto->Produto->Fornecedor->idfornecedor;
        }

        // Valida relacionamentos
        if (!isset($stdProduto->Produto->Categoria->idCategoria)) {
            throw new Exception('ID da Categoria não informado');
        }
        $CategoriaMiddleware = new CategoriaMiddleware();
        $CategoriaMiddleware->IsValidId($stdProduto->Produto->Categoria->idCategoria);

        if (!isset($stdProduto->Produto->Fornecedor->idFornecedor)) {
            throw new Exception('ID do Fornecedor não informado');
        }
        $FornecedorMiddleware = new FornecedorMiddleware();
        $FornecedorMiddleware->IsValidId($stdProduto->Produto->Fornecedor->idFornecedor);

        $stdProduto->Produto->idProduto = $idProduto;
        
        (new ProdutoController())->edit($stdProduto);
        
    } catch (Throwable $throwable) {
        $this->sendErrorResponse(
            throwable: $throwable, 
            message: 'Erro na atualização do Produto',
            httpCode: 400
        );
    }
    exit();
});
         $this->router->delete(pattern: '/produtos/(\d+)', fn: function ($idProduto): never {
            try {
                (new ProdutoMiddleware())->IsValidId(idProduto: $idProduto);
                (new ProdutoController())->destroy($idProduto);
            } catch (Throwable $throwable) {
                $this->sendErrorResponse(throwable: $throwable, message: 'Erro na exclusão de dados');
            }
            exit();
        });
    }
    public function start(): void
    {
        $this->router->run();
    }
}
?>