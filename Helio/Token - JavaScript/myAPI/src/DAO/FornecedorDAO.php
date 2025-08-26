<?php
require_once "myAPI/src/models/Fornecedor.php";
require_once "myAPI/src/db/Database.php";

Class FornecedorDAO
{
    public function readAll() : array
    {
        $resultados = [];
        $query = 'SELECT
                    idFornecedor,
                    nomeFornecedor,
                    emailFornecedor,
                    telefoneFornecedor,
                    enderecoFornecedor
                    FROM Fornecedor
                    ORDER BY nomeFornecedor ASC;
                    ';
        $statament = Database::getConnection()->query(query:$query);
        $statament->execute();
        $resultados = $statament->fetchAll(mode: (PDO::FETCH_ASSOC));
        return $resultados;
    }
    public function readById(int $idFornecedor) : Categoria | array
     {
        $query = 'SELECT
                    idFornecedor,
                    nomeFornecedor,
                    emailFornecedor,
                    telefoneFornecedor,
                    enderecoFornecedor
                    FROM Fornecedor
                    WHERE idFornecedor = :idFornecedor
                    ORDER BY nomeFornecedor ASC';

        $statement = Database::getConnection()->prepare(query: $query);
        $statement->execute(params: [':idFornecedor' => $idFornecedor]);
        $resultados = $statement->fetchAll(mode: (PDO::FETCH_ASSOC));
        return $resultados;
     }
     public function readByName(string $nomeFornecedor) : Fornecedor|null
     {
         $query = 'SELECT
                    idFornecedor,
                    nomeFornecedor,
                    emailFornecedor,
                    telefoneFornecedor,
                    enderecoFornecedor
                    FROM Fornecedor
                    WHERE nomeFornecedor = :nomeFornecedor
                    ORDER BY nomeFornecedor ASC';

        $statement = Database::getConnection()->prepare(query: $query);
        $statement->execute(params: [':nomeFornecedor' => $nomeFornecedor]);
        $objStdFornecedor = $statement->fetch(mode: (PDO::FETCH_OBJ));
        if(!$objStdFornecedor)
        {
            return null;
        }
        return $Fornecedor = (new Fornecedor())
            ->setIdFornecedor(idFornecedor: $objStdFornecedor->idFornecedor)
            ->setNomeFornecedor(nomeFornecedor: $objStdFornecedor->nomeFornecedor);
     }
     public function readByEmail(string $emailFornecedor): array
    {
        $linha = [];
        $query = 'SELECT
                idFornecedor,
                nomeFornecedor,
                emailFornecedor,
                telefoneFornecedor,
                enderecoFornecedor,
              FROM funcionario
              WHERE emailFornecedor = :emailFornecedor
              LIMIT 1'; 
        $statement = Database::getConnection()->prepare($query);
        $statement->bindValue(
            param: ':emailFornecedor',
            value: $emailFornecedor,
            type: PDO::PARAM_STR
        );
        $statement->execute();
        $linha = $statement->fetch(mode: PDO::FETCH_OBJ);
        if (!$linha) {
            return []; // Retorna array vazio caso não encontre nenhum funcionário com esse e-mail
        }
        $funcionario = new Funcionario();
        $funcionario
            ->setIdFornecedor(idFornecedor: $linha->idFornecedor)                    // Define o ID do funcionário
            ->setNomeFuncionario(nomeFornecedor: $linha->nomeFornecedor)              // Define o nome
            ->setEmailFornecedor(emailFornecedor: $linha->emailFornecedor)      
            ->setTelefoneFornecedor(telefoneFornecedor: $linha->telefoneFornecedor)                                      // Define o e-mail
            ->setEnderecoFornecedor(enderecoFornecedor: $linha->enderecoFornecedor);
        return [$funcionario];
    }

    public function create(Fornecedor $Fornecedor): Fornecedor|null
{
    $query = 'INSERT INTO
             Fornecedor(nomeFornecedor, emailFornecedor, telefoneFornecedor, enderecoFornecedor)
             VALUES(:nomeFornecedor, :emailFornecedor, :telefoneFornecedor, :enderecoFornecedor)';
             
    $statement = Database::getConnection()->prepare($query);
    $statement->execute([
        ':nomeFornecedor' => $Fornecedor->getNomeFornecedor(),
        ':emailFornecedor' => $Fornecedor->getEmailFornecedor(),
        ':telefoneFornecedor' => $Fornecedor->getTelefoneFornecedor(),
        ':enderecoFornecedor' => $Fornecedor->getEnderecoFornecedor()
    ]);

    $Fornecedor->setIdFornecedor((int) Database::getConnection()->lastInsertId());
    return $Fornecedor;
}
      public function update(Fornecedor $Fornecedor): bool
    {
        $query = 'UPDATE Fornecedor
             SET nomeFornecedor = :nomeFornecedor,
                 telefoneFornecedor = :telefoneFornecedor,
                 emailFornecedor = :emailFornecedor,
                 enderecoFornecedor = :enderecoFornecedor
             WHERE idFornecedor = :idFornecedor';  // Removi o ; extra

    $statement = Database::getConnection()->prepare($query);

    return $statement->execute([
        ':nomeFornecedor' => $Fornecedor->getNomeFornecedor(),
        ':telefoneFornecedor' => $Fornecedor->getTelefoneFornecedor(),
        ':emailFornecedor' => $Fornecedor->getEmailFornecedor(),
        ':enderecoFornecedor' => $Fornecedor->getEnderecoFornecedor(),
        ':idFornecedor' => $Fornecedor->getIdFornecedor()
    ]);

    }

    public function delete(int $idFornecedor): bool
    {
        $query = 'DELETE FROM Fornecedor
                    WHERE idFornecedor = :idFornecedor;
                    ';
        $statement = Database::getConnection()->prepare(query: $query);
        $statement->execute(params: [
            'idFornecedor' => $idFornecedor
        ]);
        return $statement->rowCount() > 0;
    }
}