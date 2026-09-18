from app.schemas import Pedido

class PedidoRepository:
    """Repositório em memória para persistência de pedidos."""

    def __init__(self):
        self._pedidos: dict[str, Pedido] = {}

    def salvar(self, pedido: Pedido) -> Pedido:
        self._pedidos[pedido.id] = pedido
        return pedido

    def buscar_por_id(self, pedido_id: str) -> Pedido | None:
        return self._pedidos.get(pedido_id)

    def listar_todos(self) -> list[Pedido]:
        return list(self._pedidos.values())

    def limpar(self) -> None:
        self._pedidos.clear()

repositorio_global = PedidoRepository()