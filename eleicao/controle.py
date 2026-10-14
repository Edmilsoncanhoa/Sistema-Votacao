"""Mecanismos simples de controle de acesso a atributos."""

class CampoProtegido:
    """Descritor: impede que um atributo seja alterado depois da primeira definição."""
    def __init__(self, nome: str):
        self.nome = nome
        self.nome_interno = f"_{nome}"

    def __get__(self, instancia, proprietario):
        if instancia is None:
            return self
        return getattr(instancia, self.nome_interno)

    def __set__(self, instancia, valor):
        if hasattr(instancia, self.nome_interno):
            raise AttributeError(f"O campo '{self.nome}' não pode ser alterado diretamente.")
        setattr(instancia, self.nome_interno, valor)
