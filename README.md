# Análise de Repasses Governamentais - Cotia

Este projeto realiza uma análise detalhada dos repasses financeiros realizados pela Prefeitura de Cotia para entidades do Terceiro Setor. O sistema processa dados oficiais, gerando visualizações e análises estatísticas para melhor compreensão da distribuição desses recursos.

## 🔍 Funcionalidades

- Análise temporal dos repasses (2019-2024)
- Distribuição por função de governo (Saúde, Educação, etc.)
- Ranking das principais entidades beneficiadas
- Estatísticas gerais e visualizações gráficas
- Análise de distribuição dos valores

## 📊 Visualizações

O projeto gera quatro tipos de gráficos interativos:

1. Evolução temporal dos repasses
2. Distribuição por função de governo (Treemap)
3. Top 10 entidades beneficiadas
4. Distribuição estatística dos valores (Box Plot)

## 🚀 Como Instalar

### Pré-requisitos

- Python 3.8 ou superior
- pip (gerenciador de pacotes Python)
- Microsoft Excel instalado (necessário para o xlwings)

### Instalação

1. Clone o repositório:

```bash
git clone https://github.com/VicktzZ/analise-repasses-sp
cd projeto-integrador
```

2. Crie um ambiente virtual (recomendado):

```bash
python -m venv venv
venv\Scripts\activate
```

3. Instale as dependências:

```bash
pip install -r requirements.txt
```

## 💻 Como Usar

1. Certifique-se de que o arquivo de dados (`repasses.xlsx`) está na pasta `data/`
2. Execute o programa:

```bash
python main.py
```

3. Os gráficos serão exibidos automaticamente e as análises serão mostradas no terminal

## 📁 Estrutura do Projeto

```
projeto-integrador/
│
├── data/
│   └── repasses.xlsx
│
├── scripts/
│   └── cotia.py
│
├── main.py
├── requirements.txt
└── README.md
```

## 📊 Exemplo de Saída

O programa gera análises como:

- Total de repasses por ano
- Distribuição por área governamental
- Ranking das entidades que mais receberam recursos
- Estatísticas gerais (média, mediana, desvio padrão)

## 🤝 Contribuindo

Sinta-se à vontade para contribuir com o projeto. Você pode:

1. Abrir issues para reportar problemas
2. Enviar pull requests com melhorias
3. Adicionar novas análises ou visualizações

## 📝 Notas

- Os dados devem estar no formato `.xlsx`
- É necessário ter o Excel instalado para o funcionamento do xlwings
- Os gráficos são interativos e podem ser explorados na interface

## 📫 Contato

[Vitor Hugo Rodrigues dos Santos/vhrdsantos.contato@gmail.com]
