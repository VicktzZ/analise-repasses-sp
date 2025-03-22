import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from utils.data_manager import carregar_dados_comparacao
from utils.formatacao import formatar_valor_reais

st.set_page_config(
    page_title="Comparação - Cotia vs Itapevi",
    page_icon="",
    layout="wide"
)

def main():
    st.title(" Comparação: Cotia vs Itapevi")
    
    try:
        # Carregar dados de comparação
        df = carregar_dados_comparacao()
        
        if df is None or df.empty:
            st.error("Erro ao carregar os dados para comparação. Verifique se o arquivo de dados existe e está acessível.")
            return
        
        # Verificar se temos dados para ambos os municípios
        municipios = df['municipio'].unique()
        if 'cotia' not in municipios or 'itapevi' not in municipios:
            st.error("Dados incompletos: não foram encontrados dados para ambos os municípios.")
            return
        
        # Métricas Gerais por Município
        st.header("Métricas Gerais")
        
        # Calcular métricas por município
        metricas = df.groupby('municipio').agg({
            'vl_pago': ['sum', 'mean', 'count'],
            'razao_social': 'nunique'
        }).round(2)
        
        # Organizar métricas em colunas
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Cotia")
            st.metric("Total de Repasses", formatar_valor_reais(metricas.loc['cotia', ('vl_pago', 'sum')]))
            st.metric("Média por Repasse", formatar_valor_reais(metricas.loc['cotia', ('vl_pago', 'mean')]))
            st.metric("Número de Operações", f"{metricas.loc['cotia', ('vl_pago', 'count')]:,}")
            st.metric("Número de Entidades", f"{metricas.loc['cotia', ('razao_social', 'nunique')]:,}")
        
        with col2:
            st.subheader("Itapevi")
            st.metric("Total de Repasses", formatar_valor_reais(metricas.loc['itapevi', ('vl_pago', 'sum')]))
            st.metric("Média por Repasse", formatar_valor_reais(metricas.loc['itapevi', ('vl_pago', 'mean')]))
            st.metric("Número de Operações", f"{metricas.loc['itapevi', ('vl_pago', 'count')]:,}")
            st.metric("Número de Entidades", f"{metricas.loc['itapevi', ('razao_social', 'nunique')]:,}")
        
        # Análises Comparativas
        st.header("Análises Comparativas")
        
        tab1, tab2, tab3 = st.tabs([
            "Evolução Temporal",
            "Distribuição por Função",
            "Top Entidades"
        ])
        
        with tab1:
            # Evolução temporal dos repasses
            df_temporal = df.groupby(['municipio', 'exercicio'])['vl_pago'].agg(['sum', 'mean']).reset_index()
            
            # Gráfico de linha para total anual
            fig_temporal = go.Figure()
            
            for cidade in ['cotia', 'itapevi']:
                dados_cidade = df_temporal[df_temporal['municipio'] == cidade]
                fig_temporal.add_trace(go.Scatter(
                    x=dados_cidade['exercicio'],
                    y=dados_cidade['sum'],
                    name=f'{cidade.title()} - Total',
                    mode='lines+markers',
                    hovertemplate=f"{cidade.title()}<br>Ano: %{{x}}<br>Total: R$ %{{y:,.2f}}<extra></extra>"
                ))
            
            fig_temporal.update_layout(
                title='Evolução dos Repasses ao Longo dos Anos',
                xaxis_title='Ano',
                yaxis=dict(
                    title='Total de Repasses (R$)',
                    tickformat=',.2f',
                    tickprefix='R$ '
                ),
                hovermode='x unified'
            )
            st.plotly_chart(fig_temporal, use_container_width=True)
        
        with tab2:
            # Comparação por função de governo
            df_funcao = df.groupby(['municipio', 'funcao_de_governo'])['vl_pago'].sum().reset_index()
            
            # Gráfico de barras lado a lado
            fig_funcao = px.bar(
                df_funcao,
                x='funcao_de_governo',
                y='vl_pago',
                color='municipio',
                barmode='group',
                title='Distribuição dos Repasses por Função de Governo',
                labels={
                    'funcao_de_governo': 'Função de Governo',
                    'vl_pago': 'Total de Repasses (R$)',
                    'municipio': 'Município'
                }
            )
            fig_funcao.update_layout(
                xaxis_tickangle=45,
                yaxis=dict(tickformat=',.2f', tickprefix='R$ ')
            )
            fig_funcao.update_traces(
                hovertemplate="Município: %{customdata}<br>Função: %{x}<br>Total: R$ %{y:,.2f}<extra></extra>",
                customdata=df_funcao['municipio'].str.title()
            )
            st.plotly_chart(fig_funcao, use_container_width=True)
            
            # Tabela comparativa
            st.subheader("Tabela Comparativa por Função")
            df_funcao_pivot = df_funcao.pivot(
                index='funcao_de_governo',
                columns='municipio',
                values='vl_pago'
            ).round(2)
            
            st.dataframe(
                df_funcao_pivot.style.format({
                    'cotia': lambda x: formatar_valor_reais(x),
                    'itapevi': lambda x: formatar_valor_reais(x)
                })
            )
        
        with tab3:
            # Top entidades por município
            st.subheader("Top 10 Entidades por Município")
            
            # Calcular top entidades para cada município
            df_entidades = df.groupby(['municipio', 'razao_social'])['vl_pago'].sum().reset_index()
            
            # Criar duas colunas para mostrar os tops lado a lado
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("Cotia")
                top_cotia = df_entidades[df_entidades['municipio'] == 'cotia'].nlargest(10, 'vl_pago')
                st.dataframe(
                    top_cotia[['razao_social', 'vl_pago']].style.format({
                        'vl_pago': lambda x: formatar_valor_reais(x)
                    })
                )
            
            with col2:
                st.subheader("Itapevi")
                top_itapevi = df_entidades[df_entidades['municipio'] == 'itapevi'].nlargest(10, 'vl_pago')
                st.dataframe(
                    top_itapevi[['razao_social', 'vl_pago']].style.format({
                        'vl_pago': lambda x: formatar_valor_reais(x)
                    })
                )

    except Exception as e:
        st.error(f"Erro ao processar os dados: {str(e)}")
        st.exception(e)

if __name__ == '__main__':
    main()
