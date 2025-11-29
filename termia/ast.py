"""
Estruturas simples de AST para o TermIA (parcial).
Cada nó será um dicionário com campo "type" e demais atributos.
Isso facilita a integração futura (execução de comandos e IA).
"""
def node(node_type: str, **kwargs):
    d = {"type": node_type}
    d.update(kwargs)
    return d
