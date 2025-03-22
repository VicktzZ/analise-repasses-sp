import pandas as pd
import streamlit as st

def formatar_valor_reais(valor):
    """
    Formata um valor numérico para o formato de moeda brasileira.
    Exemplos:
    1234.56 -> R$ 1.234,56
    1234567.89 -> R$ 1,23M
    1234567890.12 -> R$ 1,23B
    """
    if abs(valor) >= 1_000_000_000:  # Bilhões
        return f"R$ {valor/1_000_000_000:,.2f}B"
    elif abs(valor) >= 1_000_000:  # Milhões
        return f"R$ {valor/1_000_000:,.2f}M"
    else:  # Valores normais
        return f"R$ {valor:,.2f}"

@st.cache_data
def carregar_dados_base(municipio='cotia'):
    """
    Carrega e prepara os dados base do dashboard.
    Utiliza cache do Streamlit para otimizar o carregamento.
    """
    try:
        # Carregar dados do Excel
        df = pd.read_excel('data/repasses.xlsx')
        
        # Filtrar apenas dados do município especificado
        df = df[df['municipio'].str.lower() == municipio.lower()].copy()
        
        # Converter colunas para tipos apropriados
        df['exercicio'] = pd.to_numeric(df['exercicio'], errors='coerce')
        df['vl_pago'] = pd.to_numeric(df['vl_pago'], errors='coerce')
        
        # Limpar e padronizar nomes de colunas
        df['razao_social'] = df['razao_social'].str.strip().fillna('Não Informado')
        df['funcao_de_governo'] = df['funcao_de_governo'].str.strip().fillna('Não Informado')
        
        # Remover linhas com valores nulos em colunas críticas
        df = df.dropna(subset=['vl_pago', 'exercicio'])
        
        # Otimizar tipos de dados para memória
        df['funcao_de_governo'] = df['funcao_de_governo'].astype('category')
        df['razao_social'] = df['razao_social'].astype('category')
        df['exercicio'] = df['exercicio'].astype('int32')
        
        return df
        
    except Exception as e:
        st.error(f"Erro ao carregar dados: {str(e)}")
        return None

@st.cache_data
def carregar_dados_comparacao():
    """
    Carrega dados de Cotia e Itapevi para comparação.
    """
    try:
        # Carregar dados do Excel
        df = pd.read_excel('data/repasses.xlsx')
        
        # Filtrar apenas dados de Cotia e Itapevi
        df = df[df['municipio'].str.lower().isin(['cotia', 'itapevi'])].copy()
        
        # Converter colunas para tipos apropriados
        df['exercicio'] = pd.to_numeric(df['exercicio'], errors='coerce')
        df['vl_pago'] = pd.to_numeric(df['vl_pago'], errors='coerce')
        
        # Limpar e padronizar nomes de colunas
        df['razao_social'] = df['razao_social'].str.strip().fillna('Não Informado')
        df['funcao_de_governo'] = df['funcao_de_governo'].str.strip().fillna('Não Informado')
        df['municipio'] = df['municipio'].str.lower()
        
        # Remover linhas com valores nulos em colunas críticas
        df = df.dropna(subset=['vl_pago', 'exercicio'])
        
        # Otimizar tipos de dados para memória
        df['funcao_de_governo'] = df['funcao_de_governo'].astype('category')
        df['razao_social'] = df['razao_social'].astype('category')
        df['municipio'] = df['municipio'].astype('category')
        df['exercicio'] = df['exercicio'].astype('int32')
        
        return df
        
    except Exception as e:
        st.error(f"Erro ao carregar dados: {str(e)}")
        return None

@st.cache_data
def get_agregacoes_principais(_df):
    """Pré-calcula as principais agregações utilizadas."""
    return {
        'total_geral': _df['vl_pago'].sum(),
        'media_geral': _df['vl_pago'].mean(),
        'mediana_geral': _df['vl_pago'].median(),
        'desvio_padrao': _df['vl_pago'].std(),
        'contagem_total': len(_df),
        'entidades_unicas': _df['razao_social'].nunique(),
        'anos_unicos': sorted(_df['exercicio'].unique()),
        'funcoes_unicas': sorted(_df['funcao_de_governo'].unique())
    }

@st.cache_data
def get_dados_anuais(_df):
    """Calcula agregações por ano."""
    return _df.groupby('exercicio').agg({
        'vl_pago': ['count', 'sum', 'mean', 'median', 'std'],
        'razao_social': 'nunique'
    }).round(2)

@st.cache_data
def get_dados_funcao(_df):
    """Calcula agregações por função de governo."""
    return _df.groupby('funcao_de_governo').agg({
        'vl_pago': ['count', 'sum', 'mean', 'median', 'std'],
        'razao_social': 'nunique'
    }).round(2)

@st.cache_data
def get_dados_entidade(_df, top_n=10):
    """Calcula agregações por entidade."""
    return _df.groupby('razao_social').agg({
        'vl_pago': ['count', 'sum', 'mean'],
        'funcao_de_governo': lambda x: ', '.join(set(x))
    }).round(2).sort_values(('vl_pago', 'sum'), ascending=False).head(top_n)

@st.cache_data
def filtrar_dados(_df, anos=None, funcoes=None, valor_min=None, valor_max=None):
    """Aplica filtros aos dados."""
    df_filtrado = _df.copy()
    
    if anos is not None and len(anos) > 0:
        df_filtrado = df_filtrado[df_filtrado['exercicio'].isin(anos)]
    
    if funcoes is not None and len(funcoes) > 0:
        df_filtrado = df_filtrado[df_filtrado['funcao_de_governo'].isin(funcoes)]
    
    if valor_min is not None and valor_max is not None:
        df_filtrado = df_filtrado[df_filtrado['vl_pago'].between(valor_min, valor_max)]
    
    return df_filtrado
