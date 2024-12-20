import random
import time

status = ['Em preparo', 'A caminho', 'Entregue']


def atualizar_status_pedido(id_pedido: str) -> dict:
    """
    Atualiza o status do pedido para um status aleatório da lista.
    Se o pedido não existir, atribui um status aleatório.
    """ 
    pedido_status = random.choice(status)
    print(f"Pedido {id_pedido} atualizado para o status: {pedido_status}")  
    return {"pedido": id_pedido, "status": pedido_status}


def gerar_cupom_desconto() -> str:
    """
    Gera um cupom de desconto
    """
    desconto = random.randint(5, 80)

    print(f"PROMO{desconto}")
    return f"Cupom de desconto gerado: PROMO{desconto}"


def registrar_reclamacao(id_pedido: str, descricao: str) -> str:
    """
    Registra uma reclamação para um pedido específico.
    """

    protocolo = f"{id_pedido}{random.randint(10, 999)}{int(time.time())}"
    print(f"A reclamação para o pedido {id_pedido} foi registrada com sucesso. Número do Protocólo: {protocolo}\nDescrição: {descricao}")
    return f"A reclamação para o pedido {id_pedido} foi registrada com sucesso. Número do Protocólo: {protocolo}\nDescrição: {descricao}"

__all__ = ["atualizar_status_pedido", "gerar_cupom_desconto", "registrar_reclamacao"]