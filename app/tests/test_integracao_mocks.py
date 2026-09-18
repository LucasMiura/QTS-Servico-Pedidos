import httpx
import pytest
from starlette.testclient import TestClient
from app.gateway_pagamento import(
    GatewayIndisponivelError,
    GatewayPagamentoError,
    GatewayPagamentoClient,
    GatewayTimeoutError
)

@pytest.mark.integration
@pytest.mark.mocks
def test_criar_pedido_aprovado_com_sucesso(
    client: TestClient,
    payload_pedido_valido: dict,
    resposta_gateway_sucesso: dict,
    mocker
):
    """ Testa o fluxo completo de criação de pedido com pagamento aprovado no gateway. """

    # Arrange: Mock de chamada externa ao gateway
    mock_gateway = mocker.patch(
        "app.service.GatewayPagamentoClient.processar_transacao",
        return_value=resposta_gateway_sucesso
    )

    # Act: Disparar requisição HTTP POST
    response = client.post("/pedidos", json=payload_pedido_valido)

    # Assert: Validar contrato e persistencia
    assert response.status_code == 201
    dados = response.json()
    assert dados ["status"] == "PAGO"
    assert dados ["transacao_id"] == "TX-99887766"
    assert dados ["valor_total"] == 500.00
    assert "autorizada com sucesso" in dados["mensagem"]

    # Verificação do comportamento do Mock (spy)
    mock_gateway.assert_called_once_with(
        valor=500.00,
        metodo="PIX",
        cliente_cpf="12345678901",
        dados_pagamento={"chave_pix": "carlos.eduardo@exemplo.com"}
    )

    # Validação de persistencia no repositório via endpoint GET
    pedido_id = dados["pedido_id"]
    get_response = client.get(f"/pedidos/{pedido_id}")
    assert get_response.status_code == 200
    pedido_salvo = get_response.json()
    assert pedido_salvo["id"] == pedido_id
    assert pedido_salvo["status"] == "PAGO"
    assert pedido_salvo["cliente"]["cpf"] == "12345678901"