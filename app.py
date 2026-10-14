import sys
from eleicao import Eleicao


def main():
    if len(sys.argv) != 4:
        print("Uso: python app.py Input/Partidos.txt Input/Eleitores.txt Input/Urnas.txt")
        return 2

    sistema = Eleicao()
    sistema.processar_arquivo(sys.argv[1], "partidos")
    sistema.processar_arquivo(sys.argv[2], "eleitores")
    sistema.processar_arquivo(sys.argv[3], "urnas")
    sistema.gerar_relatorios("output")
    print("Processamento concluído. Relatórios gerados na pasta output/.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
