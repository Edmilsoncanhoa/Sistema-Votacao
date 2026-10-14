from abc import ABC, abstractmethod
from .erros import ErroCadastro
from .controle import CampoProtegido


def texto_obrigatorio(valor, tipo, campo, maximo=None):
    if not isinstance(valor, str) or not valor.strip():
        raise ErroCadastro(tipo, campo, valor, "deve ser um texto não vazio")
    valor = valor.strip()
    if maximo is not None and len(valor) > maximo:
        raise ErroCadastro(tipo, campo, valor, f"deve ter no máximo {maximo} caracteres")
    return valor


def digitos(valor, tipo, campo, tamanho):
    valor = str(valor).strip()
    if len(valor) != tamanho or not valor.isdigit():
        raise ErroCadastro(tipo, campo, valor, f"deve conter exatamente {tamanho} dígitos numéricos")
    return valor


class Partido:
    numero = CampoProtegido("numero")
    sigla = CampoProtegido("sigla")
    nome = CampoProtegido("nome")
    cnpj = CampoProtegido("cnpj")
    erros_validacao = 0

    def __init__(self, numero, sigla, nome, cnpj):
        try:
            self.numero = int(numero)
            self.sigla = texto_obrigatorio(sigla, "Partido", "sigla", 20)
            self.nome = texto_obrigatorio(nome, "Partido", "nome", 50)
            self.cnpj = digitos(cnpj, "Partido", "CNPJ", 14)
        except (ErroCadastro, ValueError, TypeError) as exc:
            self.registrar_erro()
            if isinstance(exc, ErroCadastro):
                raise
            raise ErroCadastro("Partido", "número", numero, "deve ser um inteiro") from exc

    @classmethod
    def registrar_erro(cls):
        cls.erros_validacao += 1

    def __repr__(self):
        return f"Partido({self.numero}, {self.sigla!r}, {self.nome!r})"


class Eleitor:
    def __init__(self, nome, cpf, nascimento, titulo, zona, secao):
        self.nome = texto_obrigatorio(nome, "Eleitor", "nome", 50)
        self.cpf = digitos(cpf, "Eleitor", "CPF", 11)
        self.nascimento = str(nascimento).strip()
        self.titulo = str(titulo).strip()
        self.zona = str(zona).strip()
        self.secao = str(secao).strip()
        if not self.zona or not self.secao:
            raise ErroCadastro("Eleitor", "zona/seção", (zona, secao), "não podem estar vazias")

    def __repr__(self):
        return f"Eleitor({self.nome!r}, CPF={self.cpf})"


class Candidato(Eleitor, ABC):
    def __init__(self, nome, cpf, nascimento, titulo, zona, secao, numero, partido):
        super().__init__(nome, cpf, nascimento, titulo, zona, secao)
        self.numero = str(numero).strip()
        if not isinstance(partido, Partido):
            raise ErroCadastro("Candidato", "partido", partido, "deve ser um objeto Partido")
        self.partido = partido
        self.validar_numero()

    @abstractmethod
    def validar_numero(self):
        """Cada tipo concreto valida o tamanho do número do candidato."""
        raise NotImplementedError


class Prefeito(Candidato):
    erros_validacao = 0

    def __init__(self, nome, cpf, nascimento, titulo, zona, secao, numero,
                 partido, cpf_vice, plano_governo):
        try:
            super().__init__(nome, cpf, nascimento, titulo, zona, secao, numero, partido)
            self.cpf_vice = digitos(cpf_vice, "Prefeito", "CPF do vice-prefeito", 11)
            self.plano_governo = str(plano_governo).strip()
        except ErroCadastro as exc:
            # Contabiliza apenas erro relacionado ao número do candidato nesta classe.
            if exc.campo == "número":
                type(self).registrar_erro()
            raise

    def validar_numero(self):
        if len(self.numero) != 2 or not self.numero.isdigit():
            raise ErroCadastro("Prefeito", "número", self.numero, "deve conter exatamente 2 dígitos")

    @classmethod
    def registrar_erro(cls):
        cls.erros_validacao += 1


class Vereador(Candidato):
    erros_validacao = 0

    def __init__(self, nome, cpf, nascimento, titulo, zona, secao, numero,
                 partido, bairro, projeto_lei):
        try:
            super().__init__(nome, cpf, nascimento, titulo, zona, secao, numero, partido)
            self.bairro = str(bairro).strip()
            self.projeto_lei = str(projeto_lei).strip()
        except ErroCadastro as exc:
            if exc.campo == "número":
                type(self).registrar_erro()
            raise

    def validar_numero(self):
        if len(self.numero) != 5 or not self.numero.isdigit():
            raise ErroCadastro("Vereador", "número", self.numero, "deve conter exatamente 5 dígitos")

    @classmethod
    def registrar_erro(cls):
        cls.erros_validacao += 1


class Urna:
    def __init__(self, zona=None, secao=None):
        self.zona = zona
        self.secao = secao
        # Dicionários: número do candidato -> quantidade de votos.
        self.votos_prefeito = {}
        self.votos_vereador = {}

    def registrar_voto(self, cargo, numero):
        if cargo == "prefeito":
            votos = self.votos_prefeito
        elif cargo == "vereador":
            votos = self.votos_vereador
        else:
            raise ValueError("Cargo deve ser 'prefeito' ou 'vereador'.")
        votos[numero] = votos.get(numero, 0) + 1

    def __add__(self, outra):
        if not isinstance(outra, Urna):
            return NotImplemented
        resultado = Urna(None, None)
        resultado.votos_prefeito = self._somar(self.votos_prefeito, outra.votos_prefeito)
        resultado.votos_vereador = self._somar(self.votos_vereador, outra.votos_vereador)
        return resultado

    @staticmethod
    def _somar(a, b):
        soma = dict(a)
        for chave, quantidade in b.items():
            soma[chave] = soma.get(chave, 0) + quantidade
        return soma

    def __repr__(self):
        return f"Urna(zona={self.zona}, secao={self.secao})"
