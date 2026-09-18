import pytest
from starlette.testclient import TestClient
from app.main import app
from app.repository import repositorio_global


@pytest.fixture(autouse=True)
def resetar_estado_repositorio():
    """Garante isolamento entre testes limpando o repositorio em memoria."""
    repositorio_global.limpar()
    yield
    repositorio_global.limpar()


@pytest.fixture(scope="module")
def client() -> TestClient:
    """Fixture de cliente HTTP de teste reutilizavel."""
    return TestClient(app)


@pytest.fixture
def payload_pedido_valido() -> dict:
    """Fixture com payload padrao valido para criacao de pedido."""
    return {
        "cliente": {
            "nome": "Carlos Eduardo",
            "email": "carlos.eduardo@exemplo.com",
            "cpf": "12345678901"
        },
        "itens": [
            {
                "produto_id": "PROD-101",
                "nome": "Teclado Mecanico RGB",
                "quantidade": 1,
                "preco_unitario": 250.00
            },
            {
                "produto_id": "PROD-202",
                "nome": "Mouse Gamer 16000 DPI",
                "quantidade": 2,
                "preco_unitario": 125.00
            }
        ],
        "metodo_pagamento": "PIX",
        "dados_pagamento": {
            "chave_pix": "carlos.eduardo@exemplo.com"
        }
    }


@pytest.fixture
def resposta_gateway_sucesso() -> dict:
    """Fixture simulando retorno de pagamento aprovado da API externa."""
    return {
        "aprovado": True,
        "status": "AUTORIZADO",
        "transacao_id": "TX-99887766",
        "motivo": "Transacao autorizada com sucesso pela operadora."
    }


@pytest.fixture
def resposta_gateway_recusado() -> dict:
    """Fixture simulando retorno de pagamento recusado pela operadora."""
    return {
        "aprovado": False,
        "status": "RECUSADO",
        "transacao_id": None,
        "motivo": "Saldo ou limite insuficiente no meio de pagamento."
    }