<?php
require_once "myAPI/src/DAO/CategoriaDAO.php";
require_once "myAPI/src/http/Response.php";

class CategoriaControl
{
    public function index(): never
    {
        $CategoriaDAO = new CategoriaDAO();
        $resposta = $CategoriaDAO->readAll();
        (new Response(
            success: true,
            message: 'Dados de Categorias Selecionados com sucesso',
            data: [
                'Categorias' => $resposta
            ],
            httpCode: 200
        ))->send();
        exit();
    }
    public function show(int $idCategoria): never
{
    $categoriaDAO = new CategoriaDAO();
    $categoriaData = $categoriaDAO->readById($idCategoria);
    
    (new Response(
        success: true,
        message: 'Categoria encontrada',
        data: ['Categoria' => $categoriaData],
        httpCode: 200
    ))->send();
    exit();
}
    public function store(stdClass $stdCategoria): never
    {
        $Categoria = new Categoria();
        $Categoria->setNomeCategoria(nomeCategoria: $stdCategoria->Categoria->nomeCategoria);
        
        $CategoriaDAO = new CategoriaDAO();
        $novoCategoria = $CategoriaDAO->create(Categoria: $Categoria);
        (new Response(
            success: true,
            message: 'Categoria cadastrada com sucesso',
            data:[
                'Categorias' => $novoCategoria
            ],
            httpCode: 200
        ))->send();
        exit();
    }
    public function edit(stdClass $stdCategoria): never
    {
        $CategoriaDAO = new CategoriaDAO();
        $Categoria = new Categoria();
        $Categoria
            ->setIdCategoria(idCategoria: $stdCategoria->Categoria->idCategoria)
            ->setNomeCategoria(nomeCategoria: $stdCategoria->Categoria->nomeCategoria);
        if($CategoriaDAO->update(Categoria: $Categoria) == true)
        {
            (new Response(
            success: true,
            message: 'Categoria atualizada com sucesso',
            data:[
                'Categorias' => $Categoria
            ],
            httpCode: 200
        ))->send();
        }else{
            (new Response(
            success: false,
            message: 'Categoria não fui atualizada',
            error:[
                'code' => 'update_error',
                'message' => 'Não foi possível atualizar a Categoria'
            ],
            httpCode: 400
        ))->send();
        }
        exit();

    }
    public function destroy(int $idCategoria): never
    {
        $CategoriaDAO = new CategoriaDAO();
        if($CategoriaDAO->delete(idCategoria: $idCategoria))
        {
            (new Response(
            success: true,
            message: 'Cargo excluído com sucesso',
            httpCode: 204
        ))->send();
        exit();
        }else{
            (new Response(
            success: false,
            message: 'Não foi possível excluir a Categoria',
            error: [
                'code' => 'delete_error',
                'message'=> 'A Categoria não pode ser atualizada'
            ],
            httpCode: 400
        ))->send();
        exit();
        }
    }
}