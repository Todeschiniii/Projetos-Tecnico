<?php
require_once "myAPI/src/DAO/FornecedorDAO.php";
require_once "myAPI/src/http/Response.php";
Class FornecedorMiddleware
{
    public function IsValidId($idFornecedor) : self
    {
        if(!isset($idFornecedor))
        {
            (new Response(
                success: true,
                message:"",
                error: [
                    'code' => 'Fornecedor_validation_error',
                    'message'=> 'O Id fornecido nao é valido!'
                ],
                httpCode: 400
            ))->send();
            exit();
        }else if(!is_numeric(value: $idFornecedor))
        {
             (new Response(
                success: true,
                message:"",
                error: [
                    'code' => 'Fornecedor_validation_error',
                    'message'=> 'O Id fornecido nao é um número!'
                ],
                httpCode: 400
            ))->send();
            exit();
        }else if($idFornecedor <= 0)
        {
            (new Response(
                success: true,
                message:"",
                error: [
                    'code' => 'Fornecedor_validation_error',
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
    $stdFornecedor = json_decode($requestBody);
    
    if (json_last_error() !== JSON_ERROR_NONE) {
        // ... (mantenha o mesmo erro de JSON inválido)
    }
    
    if (!isset($stdFornecedor->Fornecedor)) {
        // ... (mantenha o mesmo erro de objeto Fornecedor)
    }
    
    $requiredFields = ['nomeFornecedor', 'emailFornecedor', 'telefoneFornecedor', 'enderecoFornecedor'];
    foreach ($requiredFields as $field) {
        if (!isset($stdFornecedor->Fornecedor->$field)) {
            (new Response(
                success: false,
                message: 'Fornecedor inválido',
                error: [
                    'code' => 'validation_error',
                    'mensagem' => "O campo {$field} não foi enviado"
                ],
                httpCode: 400
            ))->send();
            exit();
        }
    }
    
    return $stdFornecedor;
}
 public function IsValidNomeFornecedor($nomeFornecedor): self
    {
        if (!isset($nomeFornecedor)) {  // Verifica se o atributo "nomeProduto" existe
            (new Response(
                success: false,
                message: 'Fornecedor inválido',
                error: [
                    'code' => 'validation_error',
                    'mesagem' => 'Nome do Fornecedor não enviado'
                ],
                httpCode: 400
            ))->send();
            exit();
        }else if(strlen(string: $nomeFornecedor) < 2)
        {
            (new Response(
                success: false,
                message: 'Produto inválido',
                error: [
                    'code' => 'validation_error',
                    'mesagem' => 'Nome do Fornecedor deve ter mais de 1 letras'
                ],
                httpCode: 400
            ))->send();
            exit();
        }
        return $this;
    }
   public function IsValidEmailFornecedor($emailFornecedor): self
{
    if (!isset($emailFornecedor)) {
        (new Response(
            success: false,
            message: 'Fornecedor inválido',
            error: [
                'code' => 'validation_error',
                'mensagem' => 'Email do Fornecedor não enviado'
            ],
            httpCode: 400
        ))->send();
        exit();
    }
    else if(!filter_var($emailFornecedor, FILTER_VALIDATE_EMAIL)) {
        (new Response(
            success: false,
            message: 'Fornecedor inválido',
            error: [
                'code' => 'validation_error',
                'mensagem' => 'Email do Fornecedor inválido'
            ],
            httpCode: 400
        ))->send();
        exit();
    }
    return $this;
}
    public function IsValidTelefoneFornecedor($telefoneFornecedor): self
    {
        if (!isset($telefoneFornecedor)) {  // Verifica se o atributo "nomeFornecedor" existe
            (new Response(
                success: false,
                message: 'Fornecedor inválido',
                error: [
                    'code' => 'validation_error',
                    'mesagem' => 'Nome do Fornecedor não enviado'
                ],
                httpCode: 400
            ))->send();
            exit();
        }else if(strlen(string: $telefoneFornecedor) < 11)
        {
            (new Response(
                success: false,
                message: 'Fornecedor inválido',
                error: [
                    'code' => 'validation_error',
                    'mesagem' => 'Nome do Fornecedor deve ter mais de 3 letras'
                ],
                httpCode: 400
            ))->send();
            exit();
        }
        return $this;
    }


    public function IsValidEnderecoFornecedor($enderecoFornecedor): self
    {
        if (!isset($enderecoFornecedor)) {  // Verifica se o atributo "nomeFornecedor" existe
            (new Response(
                success: false,
                message: 'Fornecedor inválido',
                error: [
                    'code' => 'validation_error',
                    'mensagem' => 'Endereço do Fornecedor não enviado'
                ],
                httpCode: 400
            ))->send();
            exit();
        }else if(strlen(string: $enderecoFornecedor) < 5)
        {
            (new Response(
                success: false,
                message: 'Fornecedor inválido',
                error: [
                    'code' => 'validation_error',
                    'mensagem' => 'Endereco do Fornecedor deve ter mais de 3 letras'
                ],
                httpCode: 400
            ))->send();
            exit();
        }
        return $this;
    }
    public function hasNotFornecedorByName($nomeFornecedor): self
    {
        $FornecedorDAO = new FornecedorDAO();
        $Fornecedor = $FornecedorDAO->readByName($nomeFornecedor);
        if(isset($Fornecedor))
        {
            (new Response(
                success: false,
                message: 'Fornecedor inválido',
                error: [
                    'code' => 'validation_error',
                    'mesagem' => 'Já existe uma Fornecedor cadastrada com esse nome($nomeFornecedor)'
                ],
                httpCode: 400
            ))->send();
            exit();
        }
        return $this;
    }

    public function hasNotFornecedorByEmail($emailFornecedor): self
    {
        $FornecedorDAO = new FuncionarioDAO();
        $FornecedorDAO = $FornecedorDAO->readByEmail(emailFornecedor: $emailFornecedor);

        if (!empty($FornecedorDAO)) {
            (new Response(
                success: false,
                message: 'Cargo inválido',
                error: [
                    'code' => 'validation_error',
                    'message' => "Já existe um Funcionario cadastrado com esse email [$emailFornecedor]"
                ],
                httpCode: 400
            ))->send();
            exit();
        }

        return $this;
    }
}
