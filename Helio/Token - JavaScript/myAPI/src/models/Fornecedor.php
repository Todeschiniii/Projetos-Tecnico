<?php
    Class Fornecedor implements JsonSerializable
    {
        public function __construct(
            public ?int $idFornecedor = null,
            public string $nomeFornecedor = "",
            public string $telefoneFornecedor = "",
            public string $emailFornecedor = "",
            public string $enderecoFornecedor = "",
        )
        {
        }
        public function jsonSerialize(): array
        {
            return[
                'idFornecedor' => $this->getIdFornecedor(),
                'nomeFornecedor' => $this->getNomeFornecedor(),
                'telefoneFornecedor' => $this->getTelefoneFornecedor(),
                'emailFornecedor' => $this->getEmailFornecedor(),
                'enderecoFornecedor' => $this->getEnderecoFornecedor()
            ];
        }
        public function getIdFornecedor(): ?int
        {
            return $this->idFornecedor;
        }
        public function setIdFornecedor(int $idFornecedor): self
        {
            $this->idFornecedor = $idFornecedor;
            return $this;
        }
        public function getNomeFornecedor(): string
        {
            return $this->nomeFornecedor;
        }
        public function setNomeFornecedor(string $nomeFornecedor): self
        {
            $this->nomeFornecedor = $nomeFornecedor;
            return $this;
        }
        public function getTelefoneFornecedor(): string
        {
            return $this->telefoneFornecedor;
        }
        public function setTelefoneFornecedor(string $telefoneFornecedor): self
        {
            $this->telefoneFornecedor = $telefoneFornecedor;
            return $this;
        }
        public function getEmailFornecedor(): string
        {
            return $this->emailFornecedor;
        }
        public function setEmailFornecedor(string $emailFornecedor): self
        {
            $this->emailFornecedor = $emailFornecedor;
            return $this;
        }
        public function getEnderecoFornecedor(): string
        {
            return $this->enderecoFornecedor;
        }
        public function setEnderecoFornecedor(string $enderecoFornecedor): self
        {
            $this->enderecoFornecedor = $enderecoFornecedor;
            return $this;
        }
    }
?>