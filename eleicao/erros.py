class ErroCadastro(Exception):
    """Erro de validação com informação sobre objeto, campo e valor."""

    def __init__(self, tipo_objeto: str, campo: str, valor: object, motivo: str = "valor inválido"):
        self.tipo_objeto = tipo_objeto
        self.campo = campo
        self.valor = valor
        self.motivo = motivo
        super().__init__(
            f"{tipo_objeto}: campo '{campo}' com valor {valor!r} — {motivo}."
        )
