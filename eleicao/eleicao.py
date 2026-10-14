from collections import defaultdict
from .modelos import Partido, Eleitor, Prefeito, Vereador, Urna
from .erros import ErroCadastro


class Eleicao:
    def __init__(self):
        self.eleitores = []
        self.partidos = []
        self.prefeitos = []
        self.vereadores = []
        self.urnas = []
        self.erros = []

    def adicionar_partido(self, partido):
        if self.buscar_partido(partido.numero) is None:
            self.partidos.append(partido)
        else:
            raise ErroCadastro("Partido", "número", partido.numero, "número de partido duplicado")

    def buscar_partido(self, numero):
        for partido in self.partidos:
            if str(partido.numero) == str(numero).strip():
                return partido
        return None

    def adicionar_eleitor(self, eleitor):
        self.eleitores.append(eleitor)
        if isinstance(eleitor, Prefeito):
            self.prefeitos.append(eleitor)
        elif isinstance(eleitor, Vereador):
            self.vereadores.append(eleitor)

    def buscar_candidato(self, cargo, numero):
        lista = self.prefeitos if cargo == "prefeito" else self.vereadores
        for candidato in lista:
            if candidato.numero == str(numero).strip():
                return candidato
        return None

    def obter_urna(self, zona, secao):
        for urna in self.urnas:
            if str(urna.zona) == str(zona) and str(urna.secao) == str(secao):
                return urna
        urna = Urna(str(zona), str(secao))
        self.urnas.append(urna)
        return urna

    def processar_arquivo(self, caminho, tipo):
        """Lê CSV simples separado por ponto e vírgula, com ou sem cabeçalho."""
        try:
            with open(caminho, "r", encoding="utf-8-sig") as arquivo:
                linhas = arquivo.readlines()
        except OSError as exc:
            self.erros.append(f"Não foi possível abrir {caminho}: {exc}")
            return

        for numero_linha, linha in enumerate(linhas, 1):
            linha = linha.strip()
            if not linha or linha.startswith("#"):
                continue
            campos = [c.strip() for c in linha.split(";")]
            if numero_linha == 1 and campos and campos[0].lower() in {
                "numero", "nome", "zona", "tipo", "cargo"
            }:
                continue
            try:
                if tipo == "partidos":
                    # numero;sigla;nome;cnpj
                    self.adicionar_partido(Partido(*campos[:4]))
                elif tipo == "eleitores":
                    self._ler_pessoa(campos)
                elif tipo == "urnas":
                    # zona;secao;cargo;voto — uma linha por voto.
                    self._ler_voto(campos)
            except (ErroCadastro, ValueError, TypeError, IndexError) as exc:
                self.erros.append(f"{caminho}, linha {numero_linha}: {exc}")

    def _ler_pessoa(self, c):
        # Formato:
        # ELEITOR;nome;cpf;nascimento;titulo;zona;secao
        # PREFEITO;nome;cpf;nascimento;titulo;zona;secao;numero;partido;cpf_vice;plano
        # VEREADOR;nome;cpf;nascimento;titulo;zona;secao;numero;partido;bairro;projeto
        tipo = c[0].upper()
        if tipo == "ELEITOR":
            obj = Eleitor(*c[1:7])
        elif tipo == "PREFEITO":
            partido = self.buscar_partido(c[8])
            if partido is None:
                raise ErroCadastro("Prefeito", "partido", c[8], "partido não cadastrado")
            obj = Prefeito(*c[1:8], partido, *c[9:11])
        elif tipo == "VEREADOR":
            partido = self.buscar_partido(c[8])
            if partido is None:
                raise ErroCadastro("Vereador", "partido", c[8], "partido não cadastrado")
            obj = Vereador(*c[1:8], partido, *c[9:11])
        else:
            raise ErroCadastro("Linha de eleitor", "tipo", tipo, "use ELEITOR, PREFEITO ou VEREADOR")
        self.adicionar_eleitor(obj)

    def _ler_voto(self, c):
        # zona;secao;cargo;numero — campo número vazio significa voto branco.
        zona, secao, cargo, numero = (c + [""] * 4)[:4]
        cargo = cargo.lower()
        if cargo not in ("prefeito", "vereador"):
            raise ErroCadastro("Voto", "cargo", cargo, "use prefeito ou vereador")
        urna = self.obter_urna(zona, secao)
        numero = numero.strip()
        if not numero:
            chave = "BRANCO"
        else:
            candidato = self.buscar_candidato(cargo, numero)
            chave = numero if candidato is not None else "NULO"
        urna.registrar_voto(cargo, chave)

    def _contagem(self, cargo):
        total = {}
        votos_brancos = votos_nulos = votos_validos = 0
        for urna in self.urnas:
            votos = urna.votos_prefeito if cargo == "prefeito" else urna.votos_vereador
            for numero, quantidade in votos.items():
                if numero == "BRANCO":
                    votos_brancos += quantidade
                elif numero == "NULO":
                    votos_nulos += quantidade
                else:
                    votos_validos += quantidade
                    total[numero] = total.get(numero, 0) + quantidade
        return total, votos_validos, votos_brancos, votos_nulos

    def relatorio_eleitores(self):
        linhas = [
            "RELATÓRIO DE ELEITORES",
            f"Total de eleitores (incluindo candidatos): {len(self.eleitores)}",
            f"Total de candidatos a prefeito: {len(self.prefeitos)}",
            f"Total de candidatos a vereador: {len(self.vereadores)}",
        ]
        zonas = defaultdict(lambda: defaultdict(int))
        for e in self.eleitores:
            zonas[e.zona][e.secao] += 1
        for zona in sorted(zonas):
            linhas.append(f"Zona {zona}:")
            for secao in sorted(zonas[zona]):
                linhas.append(f"  Seção {secao}: {zonas[zona][secao]} eleitor(es)")
        return "\n".join(linhas)

    def relatorio_partidos(self):
        linhas = ["RELATÓRIO DE PARTIDOS", f"Total de partidos: {len(self.partidos)}"]
        for p in sorted(self.partidos, key=lambda x: x.numero):
            np = sum(c.partido is p for c in self.prefeitos)
            nv = sum(c.partido is p for c in self.vereadores)
            linhas.append(f"{p.nome} ({p.sigla}, nº {p.numero}): {np} candidato(s) a prefeito; {nv} a vereador")
        return "\n".join(linhas)

    def relatorio_urnas(self):
        linhas = ["RELATÓRIO DE URNAS"]
        for urna in self.urnas:
            linhas.append(f"Urna — zona {urna.zona}, seção {urna.secao}")
            for cargo in ("prefeito", "vereador"):
                _, validos, brancos, nulos = self._contagem_urna(urna, cargo)
                linhas.append(f"  {cargo.title()}: válidos={validos}, brancos={brancos}, nulos={nulos}")
        return "\n".join(linhas)

    @staticmethod
    def _contagem_urna(urna, cargo):
        votos = urna.votos_prefeito if cargo == "prefeito" else urna.votos_vereador
        validos = sum(q for n, q in votos.items() if n not in ("BRANCO", "NULO"))
        brancos = votos.get("BRANCO", 0)
        nulos = votos.get("NULO", 0)
        return {}, validos, brancos, nulos

    def relatorio_resultado(self):
        linhas = ["RELATÓRIO DE RESULTADO GERAL"]
        votos_pref, validos_pref, _, _ = self._contagem("prefeito")
        vencedor = None
        if validos_pref:
            ordenados = sorted(votos_pref.items(), key=lambda item: (-item[1], item[0]))
            if ordenados and ordenados[0][1] > validos_pref / 2:
                vencedor = self.buscar_candidato("prefeito", ordenados[0][0])
        linhas.append(f"Prefeito eleito: {vencedor.nome if vencedor else 'Segundo Turno'}")
        votos_ver, _, _, _ = self._contagem("vereador")
        linhas.append("10 vereadores mais votados:")
        ranking = sorted(votos_ver.items(), key=lambda item: (-item[1], item[0]))[:10]
        if not ranking:
            linhas.append("  Nenhum voto válido para vereador.")
        for posicao, (numero, votos) in enumerate(ranking, 1):
            candidato = self.buscar_candidato("vereador", numero)
            linhas.append(f"  {posicao}. {candidato.nome if candidato else 'Desconhecido'} (nº {numero}): {votos} voto(s)")
        return "\n".join(linhas)

    def relatorio_erros(self):
        linhas = ["RELATÓRIO DE ERROS E EXCEÇÕES"]
        linhas.extend(self.erros or ["Nenhum erro registrado."])
        linhas.append(f"Erros de validação de Partido: {Partido.erros_validacao}")
        linhas.append(f"Erros de validação de Prefeito: {Prefeito.erros_validacao}")
        linhas.append(f"Erros de validação de Vereador: {Vereador.erros_validacao}")
        return "\n".join(linhas)

    def gerar_relatorios(self, pasta="output"):
        import os
        os.makedirs(pasta, exist_ok=True)
        relatorios = {
            "eleitores.txt": self.relatorio_eleitores(),
            "partidos.txt": self.relatorio_partidos(),
            "urnas.txt": self.relatorio_urnas(),
            "resultado_geral.txt": self.relatorio_resultado(),
            "erros.txt": self.relatorio_erros(),
        }
        for nome, conteudo in relatorios.items():
            with open(os.path.join(pasta, nome), "w", encoding="utf-8") as arquivo:
                arquivo.write(conteudo + "\n")
