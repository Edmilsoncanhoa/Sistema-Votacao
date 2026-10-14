# TG1 POD — Sistema de Votação

Implementação de referência em Python, organizada como pacote, com classes de POO, exceção personalizada, descritor de controle de acesso, sobrecarga do operador `+`, leitura de arquivos e cinco relatórios.

## Requisitos

- Python 3.10 ou superior (não são necessárias bibliotecas externas).
- Arquivos de entrada separados por ponto e vírgula (`;`).

## Executar

Na raiz do projeto:

```bash
python app.py Input/Partidos.txt Input/Eleitores.txt Input/Urnas.txt
```

Os relatórios serão escritos em `output/`.

## Formatos dos arquivos

### Partidos.txt
Uma linha por partido:

```text
numero;sigla;nome;cnpj
```

O CNPJ deve ter 14 dígitos. O número é inteiro.

### Eleitores.txt
Cada linha começa pelo tipo de registo:

```text
ELEITOR;nome;cpf;nascimento;titulo;zona;secao
PREFEITO;nome;cpf;nascimento;titulo;zona;secao;numero;numero_partido;cpf_vice;plano_governo
VEREADOR;nome;cpf;nascimento;titulo;zona;secao;numero;numero_partido;bairro;projeto_lei
```

CPF deve ter 11 dígitos. O número de prefeito deve ter 2 dígitos e o de vereador 5. O campo `numero_partido` referencia o número de um partido já carregado.

### Urnas.txt

Uma linha por voto:

```text
zona;secao;cargo;numero
```

`cargo` deve ser `prefeito` ou `vereador`. Campo `numero` vazio representa voto branco; número que não corresponda a candidato do cargo representa voto nulo.

## Relatórios

- `output/eleitores.txt`
- `output/partidos.txt`
- `output/urnas.txt`
- `output/resultado_geral.txt`
- `output/erros.txt`

## Observações importantes
1. A aplicação conta cada linha do arquivo de urnas como um voto. Se os arquivos oficiais representarem vários votos numa linha ou usarem outro layout, adapte o leitor.
2. O descritor `CampoProtegido` impede alterações diretas de campos protegidos após a primeira atribuição. É uma implementação simples de controle de acesso para demonstrar o conceito.
3. Em produção, seria importante validar também datas, título de eleitor, zona/seção e regras adicionais de duplicidade.
4. Confirme com o professor os pacotes/módulos permitidos e as convenções de saída exigidas.

## Estrutura

```text
tg1_sistema_votacao/
├── app.py
├── eleicao/
│   ├── __init__.py
│   ├── controle.py
│   ├── eleicao.py
│   ├── erros.py
│   └── modelos.py
├── Input/
│   ├── Partidos.txt
│   ├── Eleitores.txt
│   └── Urnas.txt
├── output/
└── README.md
```
