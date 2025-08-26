<?php
require_once "myAPI/src/db/Database.php";

require_once "myAPI/src/models/Produto.php";
require_once "myAPI/src/models/Fornecedor.php";
Class ProdutoDAO
{
    public function readAll() : array
    {
        $resultados = [];
        $query = 'SELECT
                    idProduto,
                    nomeProduto,
                    precoProduto,
                    quantidade_estoqueProduto,
                    Fornecedor_idFornecedor,
                    categoria_idCategoria
                    FROM Produto
                    ORDER BY nomeProduto ASC;
                    ';
        $statament = Database::getConnection()->query(query:$query);
        $statament->execute();
        $resultados = $statament->fetchAll(mode: (PDO::FETCH_ASSOC));
        return $resultados;
    }
     public function readById(int $idProduto) : Categoria | array
     {
        $query = 'SELECT
                    idProduto,
                    nomeProduto,
                    precoProduto,
                    quantidade_estoqueProduto,
                    Fornecedor_idFornecedor,
                    categoria_idCategoria
                    FROM Produto
                    WHERE idProduto = :idProduto
                    ORDER BY nomeProduto ASC';

        $statement = Database::getConnection()->prepare(query: $query);
        $statement->execute(params: [':idProduto' => $idProduto]);
        $resultados = $statement->fetchAll(mode: (PDO::FETCH_ASSOC));
        return $resultados;
     }
     public function readByName(string $nomeProduto) : Produto|null
     {
         $query = 'SELECT
                    idProduto,
                    nomeProduto,
                    precoProduto,
                    quantidade_estoqueProduto,
                    Fornecedor_idFornecedor,
                    categoria_idCategoria
                    FROM Produto
                    WHERE idProduto = :idProduto
                    ORDER BY nomeProduto ASC';

        $statement = Database::getConnection()->prepare(query: $query);
        $statement->execute(params: [':nomeProduto' => $nomeProduto]);
        $objStdProduto = $statement->fetch(mode: (PDO::FETCH_OBJ));
        if(!$objStdProduto)
        {
            return null;
        }
        return $Produto = (new Produto())
            ->setIdProduto(idProduto: $objStdProduto->idProduto)
            ->setNomeProduto(nomeProduto: $objStdProduto->nomeProduto);
     }
   public function update(Produto $Produto): bool
{
    $query = 'UPDATE Produto
              SET 
                nomeProduto = :nomeProduto,     
                precoProduto = :precoProduto,
                quantidade_estoqueProduto = :quantidade_estoqueProduto,
                categoria_idCategoria = :categoria_idCategoria,
                Fornecedor_idFornecedor = :Fornecedor_idFornecedor
              WHERE 
                idProduto = :idProduto';

    $statement = Database::getConnection()->prepare($query);
    
    $statement->bindValue(':nomeProduto', $Produto->getNomeProduto(), PDO::PARAM_STR);
    
    // Alteração principal aqui - use PARAM_STR e formate o número corretamente
    $statement->bindValue(
        ':precoProduto', 
        number_format((float)$Produto->getPrecoProduto(), 2, '.', ''), 
        PDO::PARAM_STR
    );
    
    $statement->bindValue(':quantidade_estoqueProduto', $Produto->getQuantidade_EstoqueProduto(), PDO::PARAM_INT);
    $statement->bindValue(':categoria_idCategoria', $Produto->getCategoria()->getIdCategoria(), PDO::PARAM_INT);
    $statement->bindValue(':Fornecedor_idFornecedor', $Produto->getFornecedor()->getIdFornecedor(), PDO::PARAM_INT);
    $statement->bindValue(':idProduto', $Produto->getIdProduto(), PDO::PARAM_INT);

    return $statement->execute() && $statement->rowCount() > 0;
}
    public function create(Produto $Produto): ?Produto
    {
        $query = 'INSERT INTO Produto (
            nomeProduto,
            precoProduto,
            quantidade_estoqueProduto,
            Fornecedor_idFornecedor,
            categoria_idCategoria
        ) VALUES (
            :nomeProduto,
            :precoProduto,
            :quantidade_estoqueProduto,
            :Fornecedor_idFornecedor,
            :categoria_idCategoria
        )';

        $statement = Database::getConnection()->prepare(query: $query);

        $statement->bindValue(param: ':nomeProduto', value: $Produto->getNomeProduto(), type: PDO::PARAM_STR);
        $statement->bindValue(param: ':precoProduto', value: $Produto->getPrecoProduto(), type: PDO::PARAM_STR);
        $statement->bindValue(param: ':quantidade_estoqueProduto', value: $Produto->getQuantidade_EstoqueProduto(), type: PDO::PARAM_INT);
        $statement->bindValue(param: ':categoria_idCategoria', value: $Produto->getCategoria()->getIdCategoria(), type: PDO::PARAM_STR);
        $statement->bindValue(param: ':Fornecedor_idFornecedor', value: $Produto->getFornecedor()->getIdFornecedor(), type: PDO::PARAM_STR);

        $success = $statement->execute();

        if (!$success) {
            return null;
        }

        $Produto->setIdProduto(idProduto: (int) Database::getConnection()->lastInsertId());

        return $Produto;
    }
 public function delete(int $idProduto): bool
{
    try {
        $query = 'DELETE FROM Produto WHERE idProduto = :idProduto';
        $statement = Database::getConnection()->prepare($query);
        
        $statement->bindValue(':idProduto', $idProduto, PDO::PARAM_INT);
        $statement->execute();
        
        return $statement->rowCount() > 0;
    } catch (PDOException $e) {
        error_log('Erro ao excluir produto: ' . $e->getMessage());
        return false;
    }
}
}