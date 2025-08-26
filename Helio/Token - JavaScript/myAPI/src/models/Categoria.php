<?php
    class Categoria implements JsonSerializable
    {
        public function __construct(
            private ?int $idCategoria = null,
            private string $nomeCategoria = ""
        )
        {  
        }
        public function jsonSerialize(): array
        {
            return [
                'idCategoria' => $this->idCategoria,
                'nomeCategoria' => $this->nomeCategoria
            ];
        }
        public function getIdCategoria() : ?int
        {
            return $this->idCategoria;
        }
        public function setIdCategoria(int $idCategoria) : self
        {
            $this->idCategoria = $idCategoria;
            return $this;
        }
        public function getNomeCategoria() : string
        {
            return $this->nomeCategoria;
        }
        public function setNomeCategoria(string $nomeCategoria): self
        {
            $this->nomeCategoria = $nomeCategoria;
            return $this;
        }
    }
?>