from datetime import datetime, timezone
import uuid
from app.gateway_pagamento import (
    GatewayPagamentoClient,
    GatewayPagamentoError,
    GatewayTimeoutError,
    GatewayIndisponivelError
)

from app.repository import PedidoRepository, repositorio_global
from app.schemas import (
    CriarPedidoRequest,
    Pedido,
    RespostaProcessamento,
    StatusPedido
)

class PedidoService:
    """Orquestrador do ciclo de vida de pedidos e integração de pagamentos."""

    def __init__ (
            self,
            repository: PedidoRepository = repositorio_global,
            gateway: GatewayPagamentoClient | None = None
    ):
        self.repository = repository
        self.gateway = gateway or GatewayPagamentoClient()

    def calcular_total(self, itens) -> float:
        total = sum(item.quantidade * item.preco_unitario for item in itens)
        return round(total, 2)

    def processar_novo_pedido(self, request: CriarPedidoRequest) -> RespostaProcessamento:
        valor_total = self.calcular_total(request.itens)
        if valor_total <= 0:
            raise ValueError("O valor total do pedido deve ser maior que zero.")

        pedido_id = str(uuid.uuid4())
        agora = datetime.now(timezone.utc).isoformat()

        # Chama o gateway externo
        resultado_gateway = self.gateway.processar_transacao(
            valor=valor_total,
            metodo=request.metodo_pagamento.value,
            client_cpf=request.cliente.cpf,
            dados_pagamento=request.dados_pagamento
        )

        aprovado = resultado_gateway.get("aprovado", False)
        status = StatusPedido.PAGO if aprovado else StatusPedido.FALHA_PAGAMENTO
        transacao_id = resultado_gateway.get("transacao_id")
        motivo = resultado_gateway.get("motivo", "Pagamento processado com sucesso." if aprovado else "Recusado.")

        pedido = Pedido(
            id=pedido_id,
            cliente=request.cliente,
            itens=request.itens,
            valor_total=valor_total,
            status=status,
            metodo_pagamento=request.metodo_pagamento,
            transacao_id=transacao_id,
            criado_em=agora
        )

        self.repository.salvar(pedido)

        return RespostaProcessamento(
            pedido_id=pedido_id,
            status=status,
            valor_total=valor_total,
            transacao_id=transacao_id,
            mensagem=motivo
        )

    def obter_pedido(self, pedido_id: str) -> Pedido | None:
        return self.repository.buscar_por_id(pedido_id)