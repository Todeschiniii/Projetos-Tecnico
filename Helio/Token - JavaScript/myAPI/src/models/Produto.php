<?php
require_once "myAPI/src/models/Categoria.php";
require_once "myAPI/src/models/Fornecedor.php";
Class Produto implements JsonSerializable
{
    public function __construct(
        private ?int $idProduto = null,
        private ?int $quantidade_estoqueProduto = null,
        private string $nomeProduto = "",
        private string $precoProduto = "",
        private Categoria $Categoria = new Categoria(),
        private Fornecedor $Fornecedor = new Fornecedor()
    )
    {  
    }
    public function jsonSerialize(): array
        {
            return [
                'idProduto' => $this->getIdProduto(),
                'nomeProduto' => $this->getNomeProduto(),
                'precoProduto'=> $this->getPrecoProduto(),
                'quantidade_estoqueProduto' => $this->getQuantidade_EstoqueProduto(),
                'Categoria'=>[
                    'idCategoria'=> $this->getCategoria()->getIdCategoria(),
                    'nomeCategoria'=> $this->getCategoria()->getNomeCategoria()
                ],
                'Fornecedor'=>[
                    'idFornecedor'=> $this->getFornecedor()->getIdFornecedor(),
                    'nomeFornecedor'=> $this->getFornecedor()->getNomeFornecedor(),
                    'telefoneFornecedor'=> $this->getFornecedor()->getTelefoneFornecedor(),
                    'emailFornecedor' => $this->getFornecedor()->getemailFornecedor(),
                'enderecoFornecedor' => $this->getFornecedor()->getenderecoFornecedor()
                ]
            ];
        }
        public function getIdProduto() : ?int
        {
            return $this->idProduto;
        }
        public function setIdProduto(int $idProduto) : self
        {
            $this->idProduto = $idProduto;
            return $this;
        }
        public function getNomeProduto() : string
        {
            return $this->nomeProduto;
        }
        public function setNomeProduto(string $nomeProduto): self
        {
            $this->nomeProduto = $nomeProduto;
            return $this;
        }
        public function getPrecoProduto() : string
        {
            return $this->precoProduto;
        }
        public function setPrecoProduto(float $precoProduto): self
{
    $this->precoProduto = $precoProduto;
    return $this;
}
        public function getQuantidade_EstoqueProduto() : ?int
        {
            return $this->quantidade_estoqueProduto;
        }
        public function setQuantidade_EstoqueProduto(int $quantidade_estoqueProduto): self
        {
            $this->quantidade_estoqueProduto = $quantidade_estoqueProduto;
            return $this;
        }
        public function getCategoria() : Categoria
        {
            return $this->Categoria;
        }
        public function setCategoria(Categoria $Categoria): self
        {
            $this->Categoria = $Categoria;
            return $this;
        }
        public function getFornecedor() : Fornecedor
        {
            return $this->Fornecedor;
        }
        public function setFornecedor(Fornecedor $Fornecedor): self
        {
            $this->Fornecedor = $Fornecedor;
            return $this;
        }
        public function setCategoriaById(int $idCategoria): self
{
    $this->Categoria = (new Categoria())->setIdCategoria($idCategoria);
    return $this;
}

public function setFornecedorById(int $idFornecedor): self
{
    $this->Fornecedor = (new Fornecedor())->setIdFornecedor($idFornecedor);
    return $this;
}

}
?>