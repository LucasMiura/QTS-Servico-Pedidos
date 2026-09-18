from enum import Enum
from pydantic import BaseModel, Field, field_validator
import re


class StatusPedido(str, Enum):
    PENDENTE = "PENDENTE"
    PAGO = "PAGO"
    FALHA_PAGAMENTO = "FALHA_PAGAMENTO"
    CANCELADO = "CANCELADO"


class MetodoPagamento(str, Enum):
    PIX = "PIX"
    CARTAO_CREDITO = "CARTAO_CREDITO"
    BOLETO = "BOLETO"


class Cliente(BaseModel):
    nome: str = Field(..., min_length=2, max_length=100)
    email: str = Field(..., max_length=150)
    cpf: str = Field(..., min_length=11, max_length=14)

    @field_validator("email")
    @classmethod
    def validar_email(cls, v: str) -> str:
        padrao = r"^[\w\.-]+@[\w\.-]+\.\w+$"
        if not re.match(padrao, v.strip()):
            raise ValueError("Formato de e-mail invalido.")
        return v.strip().lower()

    @field_validator("cpf")
    @classmethod
    def validar_cpf(cls, v: str) -> str:
        digitos = "".join(filter(str.isdigit, v))
        if len(digitos) != 11:
            raise ValueError("CPF deve conter exatamente 11 digitos numericos.")
        return digitos


class ItemPedido(BaseModel):
    produto_id: str = Field(..., min_length=1)
    nome: str = Field(..., min_length=1, max_length=100)
    quantidade: int = Field(..., gt=0)
    preco_unitario: float = Field(..., gt=0.0)


class CriarPedidoRequest(BaseModel):
    cliente: Cliente
    itens: list[ItemPedido] = Field(..., min_length=1)
    metodo_pagamento: MetodoPagamento
    dados_pagamento: dict[str, str] = Field(default_factory=dict)


class RespostaProcessamento(BaseModel):
    pedido_id: str
    status: StatusPedido
    valor_total: float
    transacao_id: str | None = None
    mensagem: str


class Pedido(BaseModel):
    id: str
    cliente: Cliente
    itens: list[ItemPedido]
    valor_total: float
    status: StatusPedido
    metodo_pagamento: MetodoPagamento
    transacao_id: str | None = None
    criado_em: str