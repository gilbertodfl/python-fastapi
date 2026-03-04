from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session
from dependencies import pegar_sessao, verificar_token
from schemas import PedidoSchema, ItemPedidoSchema, AdicionarItemPedidoSchema, ResponsePedidosSchema
from models import Pedido, Usuario, ItemPedido 
from typing import List 


order_router = APIRouter(prefix="/pedidos", tags=["pedidos"], dependencies=[Depends(verificar_token)])

@order_router.get("/")
async def pedidos():
    """
    Essa é a rota padrão de pedidos do nosso sistema. Todas as rotas dos pedidos precisam de autenticação
    """
    return {"mensagem": "Você acessou a rota de pedidos"}

@order_router.post("/pedido")
async def criar_pedido(pedido_schema: PedidoSchema, session: Session = Depends(pegar_sessao)):
    """
        Aqui é onde criamos o pedido. Lembre-se de logar primeiro para obter o token. 
    """
    novo_pedido = Pedido(usuario=pedido_schema.id_usuario)
    session.add(novo_pedido)
    session.commit()
    return {"mensagem": f"Pedido criado com sucesso. ID do pedido: {novo_pedido.id}"}

@order_router.post("/pedido/cancelar/{id_pedido}")
async def cancelar_pedido(id_pedido: int, session: Session = Depends(pegar_sessao), usuario: Usuario = Depends(verificar_token)):
    """
        Aqui é onde cancelamos o pedido. Lembre-se de logar primeiro para obter o token. 
    """

    pedido = session.query(Pedido).filter(Pedido.id == id_pedido).first()
    
    if not pedido:
        raise HTTPException(status_code=404, detail="Pedido não encontrado")
    if pedido.usuario != usuario.id:
        raise HTTPException(status_code=403, detail="Você não tem permissão para cancelar este pedido")
    pedido.status = "CANCELADO"
    session.commit()
    return JSONResponse(
        status_code=200,
        content={
            "mensagem": f"Pedido cancelado com sucesso.",
            "pedido": {
                "id": pedido.id,
                "status": pedido.status,
                "usuario": pedido.usuario,
                # adicione os demais campos do seu modelo aqui
            }
        }
    )

@order_router.get("/listar-pedidos")
async def listar_pedidos(session: Session = Depends(pegar_sessao), usuario: Usuario = Depends(verificar_token)):
   """
        listar todos os pedidos. Lembre-se de logar primeiro para obter o token. 
        Se o usuário for admin, ele pode listar todos os pedidos. Caso contrário, ele só pode listar os pedidos que ele criou.
   """

   if not usuario.admin:
      raise HTTPException(status_code=403, detail="Você não tem permissão para listar pedidos")
   else:   
      pedidos = session.query(Pedido).filter(Pedido.usuario == usuario.id).all()
      ## observe que este return: O FastAPI usa o jsonable_encoder internamente,
      #  que converte automaticamente objetos SQLAlchemy, datas, UUIDs, etc. para tipos JSON compatíveis.
      return {"mensagem": "Você acessou a rota de listagem de pedidos", "pedidos": pedidos}

      ## Outra maneira de return seria o jsonable_encoder:
      ## CASO QUEIRA RETORNAR UM JSON, não esqueça o import: from fastapi.encoders import jsonable_encoder
      # return JSONResponse(
      #    status_code=200,
      #   content=jsonable_encoder({"pedidos": pedidos})
      # )
      
@order_router.post("/pedido/adicionar-item/{id_pedido}")
async def adicionar_item(id_pedido: int, 
                         item_schema: AdicionarItemPedidoSchema, 
                         session: Session = Depends(pegar_sessao), 
                         usuario: Usuario = Depends(verificar_token)):
    """
        Adicionar items a um pedido. Primeiro crie o pedido. Lembre-se de logar primeiro para obter o token. 
        Aqui ainda não implementamos se o pedido está cancelado ou finalizado, mas seria interessante implementar isso 
        para não permitir adicionar itens a pedidos cancelados ou finalizados.
    """

    pedido = session.query(Pedido).filter(Pedido.id == id_pedido).first()
    if not pedido:
        raise HTTPException(status_code=404, detail="Pedido não encontrado")
    if not usuario.admin and pedido.usuario != usuario.id:
        raise HTTPException(status_code=403, detail="Você não tem permissão para adicionar itens a este pedido")
    novo_item = ItemPedido(
        quantidade=item_schema.quantidade,
        sabor=item_schema.sabor,
        tamanho=item_schema.tamanho,
        preco_unitario=item_schema.preco_unitario,
        pedido=id_pedido,
    )
  
    ## Aqui salvamos os itens do pedido: tabela itens_pedido
    session.add(novo_item)
    ## Aqui após calcular, podemos executar o commit para salvar o item do pedido e o preço atualizado do pedido na tabela pedidos
    pedido.calcular_preco()    
    session.commit()

    return {"mensagem": f"Item adicionado com sucesso. ID do item: {novo_item.id}",
            "item_id": novo_item.id,
            "preco_pedido": pedido.preco
            }
@order_router.post("/pedido/remover-item/{id_item_pedido}")
async def remover_item(id_item_pedido: int, 
                         session: Session = Depends(pegar_sessao), 
                         usuario: Usuario = Depends(verificar_token)):
    """
        Remover items a um pedido. Primeiro crie o pedido. Lembre-se de logar primeiro para obter o token. 
        Aqui ainda não implementamos se o pedido está cancelado ou finalizado, mas seria interessante implementar isso 
        para não permitir adicionar itens a pedidos cancelados ou finalizados.
    """

    item_pedido = session.query(ItemPedido).filter(ItemPedido.id == id_item_pedido).first()
    if not item_pedido:
        raise HTTPException(status_code=404, detail="Item do pedido não encontrado")
    if not usuario.admin and item_pedido.pedido != usuario.id:
        raise HTTPException(status_code=403, detail="Você não tem permissão para remover este item do pedido")  

    
    pedido = session.query(Pedido).filter(Pedido.id == item_pedido.pedido).first()
    if not usuario.admin and pedido.usuario != usuario.id:
        raise HTTPException(status_code=403, detail="Você não tem permissão para remover itens deste pedido")
    session.delete(item_pedido)
    pedido.calcular_preco()    
    session.commit()
    return {"mensagem": f"Item removido com sucesso. ID do item: {item_pedido.id}",
             "preco_pedido": pedido.preco,
             "pedido": item_pedido
           }

@order_router.post("/pedido/finalizar/{id_pedido}")
async def finalizar_pedido(id_pedido: int, session: Session = Depends(pegar_sessao), usuario: Usuario = Depends(verificar_token)):
    """
        Finalizar um pedido. Primeiro crie o pedido. Lembre-se de logar primeiro para obter o token. 
        Aqui ainda não implementamos se o pedido está cancelado ou finalizado, mas seria interessante implementar isso.
        
    """

    pedido = session.query(Pedido).filter(Pedido.id == id_pedido).first()
    
    if not pedido:
        raise HTTPException(status_code=404, detail="Pedido não encontrado")
    if pedido.usuario != usuario.id:
        raise HTTPException(status_code=403, detail="Você não tem permissão para finalizar este pedido")
    pedido.status = "FINALIZADO"
    session.commit()
    return JSONResponse(
        status_code=200,
        content={
            "mensagem": f"Pedido FINALIZADO com sucesso.",
            "pedido": {
                "id": pedido.id,
                "status": pedido.status,
                "usuario": pedido.usuario,
                # adicione os demais campos do seu modelo aqui
            }
        }
    )
@order_router.get("/consultar/{id_pedido}")
async def visualizar_pedido(id_pedido: int, session: Session = Depends(pegar_sessao), usuario: Usuario = Depends(verificar_token)):
    pedido = session.query(Pedido).filter(Pedido.id == id_pedido).first()
    
    if not pedido:
        raise HTTPException(status_code=404, detail="Pedido não encontrado")
    if not usuario.admin and pedido.usuario != usuario.id:
        raise HTTPException(status_code=403, detail="Você não tem permissão para visualizar este pedido")
    
    ## veja que consiguimos usar um for para pegar todos os itens do pedido e retornar um JSON
    # com as informações do pedido e dos itens do pedido.
    return JSONResponse(
        status_code=200,
        content={
            "pedido": {
                "id": pedido.id,
                "status": pedido.status,
                "usuario": pedido.usuario,
                "preco": pedido.preco,
                "itens": [
                    {
                        "id": item.id,
                        "quantidade": item.quantidade,
                        "sabor": item.sabor,
                        "tamanho": item.tamanho,
                        "preco_unitario": item.preco_unitario
                    }
                    for item in pedido.itens
                ]
            }
        }
    )
@order_router.get("/listar-pedidos-usuario")
async def listar_pedidos_usuario(session: Session = Depends(pegar_sessao), usuario: Usuario = Depends(verificar_token)):
 
    pedidos = session.query(Pedido).filter(Pedido.usuario == usuario.id).all()
    if not pedidos:
        raise HTTPException(status_code=404, detail="Pedidos não encontrado {}".format(usuario.id))
    return JSONResponse(
        status_code=200,
        content={
            "mensagem": "Pedidos do usuário",
            "pedidos": jsonable_encoder(pedidos)
        }
    )
@order_router.get("/listar-pedidos-usuario-via-schemma", response_model=List[ResponsePedidosSchema])
async def listar_pedidos_usuario(session: Session = Depends(pegar_sessao), usuario: Usuario = Depends(verificar_token)):
    """
      Diferente de /listar-pedidos-usuario, aqui vamos usar o schema definido em schemas.py para retornar os pedidos do usuário.
      veja na função que temos response_model=List[ResponsePedidosSchema]
      Nao esqueça de importar  em schemas o ResponsePedidosSchema e from typing import List 
    """
    pedidos = session.query(Pedido).filter(Pedido.usuario == usuario.id).all()

    if not pedidos:
        raise HTTPException(status_code=404, detail="Pedidos não encontrado {}".format(usuario.id))
    # Aqui o FastAPI usa o response_model=List[ResponsePedidosSchema] para serializar a lista de objetos Pedido.
    # Basta retornar a lista de objetos do SQLAlchemy.
    return pedidos