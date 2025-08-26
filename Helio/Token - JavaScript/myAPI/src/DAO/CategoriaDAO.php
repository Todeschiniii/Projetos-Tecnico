<?php
require_once "myAPI/src/db/Database.php";
require_once "myAPI/src/models/Categoria.php";
class CategoriaDAO
{
     public function readAll(): array
     {
        $resultados = [];
        $query = 'SELECT
                    idCategoria,
                    nomeCategoria
                    FROM Categoria
                    ORDER BY nomeCategoria ASC;
                ';
        $statement = Database::getConnection()->query(query: $query);
        $statement->execute();
        $resultados = $statement->fetchAll(mode: (PDO::FETCH_ASSOC));
        return $resultados;
     }
     public function readById(int $idCategoria) : Categoria | array
     {
        $query = 'SELECT
                    idCategoria,
                    nomeCategoria
                    FROM Categoria
                    WHERE idCategoria = :idCategoria;
                    ORDER BY nomeCategoria ASC';

        $statement = Database::getConnection()->prepare(query: $query);
        $statement->execute(params: [':idCategoria' => $idCategoria]);
        $resultados = $statement->fetchAll(mode: (PDO::FETCH_ASSOC));
        return $resultados;
     }
     public function readByName(string $nomeCategoria) : Categoria|null
     {
         $query = 'SELECT
                    idCategoria,
                    nomeCategoria
                    FROM Categoria
                    WHERE nomeCategoria = :nomeCategoria;
                    ORDER BY nomeCategoria ASC';

        $statement = Database::getConnection()->prepare(query: $query);
        $statement->execute(params: [':nomeCategoria' => $nomeCategoria]);
        $objStdCategoria = $statement->fetch(mode: (PDO::FETCH_OBJ));
        if(!$objStdCategoria)
        {
            return null;
        }
        return $Categoria = (new Categoria())
            ->setIdCategoria(idCategoria: $objStdCategoria->idCategoria)
            ->setNomeCategoria(nomeCategoria: $objStdCategoria->nomeCategoria);
     }
     public function create(Categoria $Categoria): Categoria|null
     {
         $query = 'INSERT INTO
                  Categoria(nomeCategoria)
                  VALUES(:nomeCategoria)';

        $statement = Database::getConnection()->prepare(query: $query);
        $statement->execute(params: [':nomeCategoria' => $Categoria->getNomeCategoria()]);

        $Categoria->setIdCategoria(idCategoria: (int) Database::getConnection()->lastInsertId());
        return $Categoria;
     }
     public function update(Categoria $Categoria): bool
    {
        $query = 'UPDATE Categoria
                SET nomeCategoria = :novoNomeCategoria 
                WHERE idCategoria = :idCategoria;
                ';

        $statement = Database::getConnection()->prepare(query: $query);

        $statement->execute(params: [
            ':novoNomeCategoria' => $Categoria->getNomeCategoria(),
            ':idCategoria' => $Categoria->getIdCategoria()
        ]);

    return $statement->rowCount() > 0;
    }
    public function delete(int $idCategoria): bool
    {
        $query = 'DELETE FROM Categoria
                    WHERE idCategoria = :idCategoria;
                    ';
        $statement = Database::getConnection()->prepare(query: $query);
        $statement->execute(params: [
            'idCategoria' => $idCategoria
        ]);
        return $statement->rowCount() > 0;
    }
}
   