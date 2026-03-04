from pydantic import BaseModel
from typing import Optional, List

## o que é o schema no fastapi?
## é uma classe que define o modelo de dados que será usado na API
## é usado para validar os dados recebidos e enviados na API
## é usado para definir o modelo de dados que será usado na API
## quem vai muito usar este arquivo é o auth_routes.py e o order_routes.py

class UsuarioSchema(BaseModel):
    nome: str
    email: str
    senha: str
    ativo: Optional[bool]
    admin: Optional[bool]

    class Config:
        from_attributes = True

class PedidoSchema(BaseModel):
    id_usuario: int

    class Config:
        from_attributes = True

class LoginSchema(BaseModel):
    email: str
    senha: str

    class Config:
        from_attributes = True
class ItemPedidoSchema(BaseModel):
    quantidade: int
    sabor: str
    tamanho: str
    preco_unitario: float
    pedido: int
    class Config:
        from_attributes = True


class AdicionarItemPedidoSchema(BaseModel):
    """Body para POST /pedido/adicionar-item/{id_pedido}. O pedido vem na URL."""
    quantidade: int
    sabor: str
    tamanho: str
    preco_unitario: float
    class Config:
        from_attributes = True

class ResponsePedidosSchema(BaseModel):
    id: int
    status: str
    preco: float
    itens: List[ItemPedidoSchema]

    class Config:
        from_attributes = True

"""
Para que server o Config?
class Config:
        from_attributes = True

Na prática, isso permite que você retorne direto um objeto SQLAlchemy (Pedido) da query, e o FastAPI consiga converter automaticamente esse objeto para 
ResponsePedidosSchema usando os atributos (pedido.id, pedido.status, etc.), sem você ter que fazer dict manualmente.

Sem esse Config, ao tentar validar a partir de um objeto ORM, o Pydantic reclamaria que não sabe ler os campos a partir de atributos.
"""
