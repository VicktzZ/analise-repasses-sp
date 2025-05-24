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
    if valor is None:
        return "R$ 0,00"
        
    try:
        if abs(valor) >= 1_000_000_000:  # Bilhões
            return f"R$ {valor/1_000_000_000:,.2f}B"
        elif abs(valor) >= 1_000_000:  # Milhões
            return f"R$ {valor/1_000_000:,.2f}M"
        else:  # Valores normais
            return f"R$ {valor:,.2f}"
    except:
        return "R$ 0,00"

@st.cache_data
def carregar_dados_base(municipio='cotia'):
    """
    Carrega os dados base do município especificado.
    Args:
        municipio (str): Nome do município (cotia, itapevi ou vargem_grande_paulista)
    Returns:
        DataFrame: Dados do município
    """
    try:
        # Carregar dados do Excel
        df = pd.read_excel('data/repasses.xlsx')
        
        # Converter para minúsculas
        df['municipio'] = df['municipio'].str.lower()
        
        # Padronizar o nome de Vargem Grande Paulista (caso haja variações)
        df.loc[df['municipio'].str.contains('vargem'), 'municipio'] = 'vargem_grande_paulista'
        
        # Filtrar pelo município
        df = df[df['municipio'] == municipio.lower()]
        
        # Otimizar tipos de dados
        df['exercicio'] = df['exercicio'].astype('int32')
        df['vl_pago'] = df['vl_pago'].astype('float64')
        
        return df
    except Exception as e:
        st.error(f"Erro ao carregar dados: {str(e)}")
        return None

@st.cache_data
def carregar_dados_comparacao():
    """
    Carrega os dados para comparação entre Cotia, Itapevi, Barueri, Jandira e Taboão da Serra.
    Returns:
        DataFrame: Dados combinados dos cinco municípios
    """
    try:
        # Carregar dados do Excel
        df = pd.read_excel('data/repasses.xlsx')
        
        # Converter para minúsculas
        df['municipio'] = df['municipio'].str.lower()
        
        # Filtrar apenas os municípios de interesse
        municipios = ['cotia', 'itapevi', 'barueri', 'jandira', 'taboão da serra']
        df = df[df['municipio'].isin(municipios)]
        
        # Otimizar tipos de dados
        df['exercicio'] = df['exercicio'].astype('int32')
        df['vl_pago'] = df['vl_pago'].astype('float64')
        
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
