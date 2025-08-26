<?php
require_once "myAPI/src/DAO/FornecedorDAO.php";
require_once "myAPI/src/http/Response.php";
class FornecedorControl
{
    public function index(): never
    {
        $FornecedorDAO = new FornecedorDAO();
        $resposta = $FornecedorDAO->readAll();
        (new Response(
            $success = true,
            $message = 'Dados de Fornecedores Selecionados com sucesso',
            data: [
                'Fornecedor' => $resposta
            ],
            httpCode:200
        ))->send();
        exit();
    }
     public function show(int $idFornecedor): never
{
    $fornecedorDAO = new FornecedorDAO();
    $fornecedorData = $fornecedorDAO->readById($idFornecedor);
    
    (new Response(
        success: true,
        message: 'Fornecedor encontrado',
        data: ['Fornecedor' => $fornecedorData],
        httpCode: 200
    ))->send();
    exit();
}
    public function store(stdClass $stdFornecedor): never
    {
        $Fornecedor = new Fornecedor();
        $Fornecedor->setIdFornecedor(idFornecedor: $stdFornecedor->Fornecedor->idFornecedor);
        $Fornecedor->setNomeFornecedor(nomeFornecedor: $stdFornecedor->Fornecedor->nomeFornecedor);
        $Fornecedor->setTelefoneFornecedor(telefoneFornecedor:$stdFornecedor->Fornecedor->telefoneFornecedor);
        $Fornecedor->setEmailFornecedor(emailFornecedor:$stdFornecedor->Fornecedor->emailFornecedor);
        $Fornecedor->setEnderecoFornecedor(enderecoFornecedor:$stdFornecedor->Fornecedor->enderecoFornecedor);
        $FornecedorDAO = new FornecedorDAO();
        $novoFornecedor = $FornecedorDAO->create(Fornecedor: $Fornecedor);
        (new Response(
            success: true,
            message: 'Fornecedor cadastrado com sucesso',
            data:[
                'Fornecedor' => $novoFornecedor
            ],
            httpCode: 200
        ))->send();
        exit();
    }
    public function edit(stdClass $stdFornecedor): never
    {
        $Fornecedor = new Fornecedor();
        $Fornecedor
            ->setIdFornecedor(idFornecedor:$stdFornecedor->Fornecedor->idFornecedor)
            ->setNomeFornecedor(nomeFornecedor:$stdFornecedor->Fornecedor->nomeFornecedor)
            ->setEmailFornecedor(emailFornecedor:$stdFornecedor->Fornecedor->emailFornecedor)
            ->setTelefoneFornecedor(telefoneFornecedor:$stdFornecedor->Fornecedor->telefoneFornecedor)
            ->setEnderecoFornecedor(enderecoFornecedor:$stdFornecedor->Fornecedor->enderecoFornecedor);
        $FornecedorDAO = new FornecedorDAO();
    if($FornecedorDAO->update(Fornecedor: $Fornecedor) == true)
    {
            (new Response(
            success: true,
            message: 'Fornecedor atualizada com sucesso',
            data:[
                'Fornecedores' => $Fornecedor
            ],
            httpCode: 200
        ))->send();
    }else{
        (new Response(
        success: false,
        message: 'Fornecedor não fui atualizada',
        error:[
            'code' => 'update_error',
            'message' => 'Não foi possível atualizar a Fornecedor'
        ],
        httpCode: 400
    ))->send();
    }
    exit();

    }
    public function destroy(int $idFornecedor): never
    {
        $FornecedorDAO = new FornecedorDAO();
        if($FornecedorDAO->delete(idFornecedor: $idFornecedor))
        {
            (new Response(
            success: true,
            message: 'Fornecedor excluído com sucesso',
            httpCode: 204
        ))->send();
        exit();
        }else{
            (new Response(
            success: false,
            message: 'Não foi possível excluir a Fornecedor',
            error: [
                'code' => 'delete_error',
                'message'=> 'A Fornecedor não pode ser atualizada'
            ],
            httpCode: 400
        ))->send();
        exit();
        }
    }

}