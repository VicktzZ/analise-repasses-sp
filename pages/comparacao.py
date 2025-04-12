import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from utils.data_manager import carregar_dados_comparacao, formatar_valor_reais

st.set_page_config(
    page_title="Comparação - Municípios SP",
    page_icon="",
    layout="wide"
)

def main():
    st.title(" Comparação: Cotia, Itapevi e Vargem Grande Paulista")
    
    try:
        # Carregar dados de comparação
        df = carregar_dados_comparacao()
        
        if df is None or df.empty:
            st.error("Erro ao carregar os dados para comparação. Verifique se o arquivo de dados existe e está acessível.")
            return
        
        # Verificar se temos dados para todos os municípios
        municipios = df['municipio'].unique()
        municipios_esperados = ['cotia', 'itapevi', 'vargem_grande_paulista']
        municipios_faltando = [m for m in municipios_esperados if m not in municipios]
        
        if municipios_faltando:
            st.warning(f"Dados incompletos: não foram encontrados dados para {', '.join(municipios_faltando)}.")
        
        # Métricas Gerais por Município
        st.header("Métricas Gerais")
        
        # Calcular métricas por município
        metricas = df.groupby('municipio').agg({
            'vl_pago': ['sum', 'mean', 'count'],
            'razao_social': 'nunique'
        }).round(2)
        
        # Organizar métricas em colunas
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.subheader("Cotia")
            if 'cotia' in municipios:
                st.metric("Total de Repasses", formatar_valor_reais(metricas.loc['cotia', ('vl_pago', 'sum')]))
                st.metric("Média por Repasse", formatar_valor_reais(metricas.loc['cotia', ('vl_pago', 'mean')]))
                st.metric("Número de Operações", f"{metricas.loc['cotia', ('vl_pago', 'count')]:,}")
                st.metric("Número de Entidades", f"{metricas.loc['cotia', ('razao_social', 'nunique')]:,}")
            else:
                st.info("Dados não disponíveis para Cotia")
        
        with col2:
            st.subheader("Itapevi")
            if 'itapevi' in municipios:
                st.metric("Total de Repasses", formatar_valor_reais(metricas.loc['itapevi', ('vl_pago', 'sum')]))
                st.metric("Média por Repasse", formatar_valor_reais(metricas.loc['itapevi', ('vl_pago', 'mean')]))
                st.metric("Número de Operações", f"{metricas.loc['itapevi', ('vl_pago', 'count')]:,}")
                st.metric("Número de Entidades", f"{metricas.loc['itapevi', ('razao_social', 'nunique')]:,}")
            else:
                st.info("Dados não disponíveis para Itapevi")
        
        with col3:
            st.subheader("Vargem Grande Paulista")
            if 'vargem_grande_paulista' in municipios:
                st.metric("Total de Repasses", formatar_valor_reais(metricas.loc['vargem_grande_paulista', ('vl_pago', 'sum')]))
                st.metric("Média por Repasse", formatar_valor_reais(metricas.loc['vargem_grande_paulista', ('vl_pago', 'mean')]))
                st.metric("Número de Operações", f"{metricas.loc['vargem_grande_paulista', ('vl_pago', 'count')]:,}")
                st.metric("Número de Entidades", f"{metricas.loc['vargem_grande_paulista', ('razao_social', 'nunique')]:,}")
            else:
                st.info("Dados não disponíveis para Vargem Grande Paulista")
        
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
            
            cores = {
                'cotia': 'blue',
                'itapevi': 'red',
                'vargem_grande_paulista': 'green'
            }
            
            for cidade in municipios:
                dados_cidade = df_temporal[df_temporal['municipio'] == cidade]
                nome_cidade = 'Vargem Grande P.' if cidade == 'vargem_grande_paulista' else cidade.title()
                
                fig_temporal.add_trace(go.Scatter(
                    x=dados_cidade['exercicio'],
                    y=dados_cidade['sum'],
                    name=f'{nome_cidade} - Total',
                    mode='lines+markers',
                    marker_color=cores.get(cidade, 'purple'),
                    hovertemplate=f"{nome_cidade}<br>Ano: %{{x}}<br>Total: %{{y:,.2f}}<extra></extra>"
                ))
            
            fig_temporal.update_layout(
                title='Evolução dos Repasses ao Longo dos Anos',
                xaxis_title='Ano',
                yaxis=dict(
                    title='Total de Repasses (R$)',
                    tickformat=',.2f',
                    tickprefix='R$ '
                ),
                hovermode='x unified',
                legend_title="Município"
            )
            st.plotly_chart(fig_temporal, use_container_width=True)
            
            # Gráfico de linha para média anual
            fig_media = go.Figure()
            
            for cidade in municipios:
                dados_cidade = df_temporal[df_temporal['municipio'] == cidade]
                nome_cidade = 'Vargem Grande P.' if cidade == 'vargem_grande_paulista' else cidade.title()
                
                fig_media.add_trace(go.Scatter(
                    x=dados_cidade['exercicio'],
                    y=dados_cidade['mean'],
                    name=f'{nome_cidade} - Média',
                    mode='lines+markers',
                    marker_color=cores.get(cidade, 'purple'),
                    hovertemplate=f"{nome_cidade}<br>Ano: %{{x}}<br>Média: %{{y:,.2f}}<extra></extra>"
                ))
            
            fig_media.update_layout(
                title='Evolução da Média de Repasses ao Longo dos Anos',
                xaxis_title='Ano',
                yaxis=dict(
                    title='Média de Repasses (R$)',
                    tickformat=',.2f',
                    tickprefix='R$ '
                ),
                hovermode='x unified',
                legend_title="Município"
            )
            st.plotly_chart(fig_media, use_container_width=True)
        
        with tab2:
            # Comparação por função de governo
            df_funcao = df.groupby(['municipio', 'funcao_de_governo'])['vl_pago'].sum().reset_index()
            
            # Mapa de nomes de município para exibição
            nomes_municipios = {
                'cotia': 'Cotia',
                'itapevi': 'Itapevi',
                'vargem_grande_paulista': 'Vargem Grande P.'
            }
            
            df_funcao['municipio_exibicao'] = df_funcao['municipio'].map(nomes_municipios)
            
            # Gráfico de barras lado a lado
            fig_funcao = px.bar(
                df_funcao,
                x='funcao_de_governo',
                y='vl_pago',
                color='municipio_exibicao',
                barmode='group',
                title='Distribuição dos Repasses por Função de Governo',
                labels={
                    'funcao_de_governo': 'Função de Governo',
                    'vl_pago': 'Total de Repasses (R$)',
                    'municipio_exibicao': 'Município'
                },
                color_discrete_map={
                    'Cotia': 'blue',
                    'Itapevi': 'red',
                    'Vargem Grande P.': 'green'
                }
            )
            fig_funcao.update_layout(
                xaxis_tickangle=45,
                yaxis=dict(tickformat=',.2f', tickprefix='R$ '),
                legend_title="Município"
            )
            fig_funcao.update_traces(
                hovertemplate="Município: %{customdata}<br>Função: %{x}<br>Total: R$ %{y:,.2f}<extra></extra>",
                customdata=df_funcao['municipio_exibicao']
            )
            st.plotly_chart(fig_funcao, use_container_width=True)
            
            # Tabela comparativa
            st.subheader("Tabela Comparativa por Função")
            df_funcao_pivot = df_funcao.pivot(
                index='funcao_de_governo',
                columns='municipio_exibicao',
                values='vl_pago'
            ).round(2)
            
            # Renomear colunas para exibição
            st.dataframe(
                df_funcao_pivot.style.format({
                    col: lambda x: formatar_valor_reais(x) if pd.notna(x) else "-" 
                    for col in df_funcao_pivot.columns
                })
            )
        
        with tab3:
            # Top entidades por município
            st.subheader("Top 10 Entidades por Município")
            
            # Calcular top entidades para cada município
            df_entidades = df.groupby(['municipio', 'razao_social'])['vl_pago'].sum().reset_index()
            
            # Criar três colunas para mostrar os tops lado a lado
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.subheader("Cotia")
                if 'cotia' in municipios:
                    top_cotia = df_entidades[df_entidades['municipio'] == 'cotia'].nlargest(10, 'vl_pago')
                    st.dataframe(
                        top_cotia[['razao_social', 'vl_pago']].style.format({
                            'vl_pago': lambda x: formatar_valor_reais(x)
                        })
                    )
                else:
                    st.info("Dados não disponíveis para Cotia")
            
            with col2:
                st.subheader("Itapevi")
                if 'itapevi' in municipios:
                    top_itapevi = df_entidades[df_entidades['municipio'] == 'itapevi'].nlargest(10, 'vl_pago')
                    st.dataframe(
                        top_itapevi[['razao_social', 'vl_pago']].style.format({
                            'vl_pago': lambda x: formatar_valor_reais(x)
                        })
                    )
                else:
                    st.info("Dados não disponíveis para Itapevi")
            
            with col3:
                st.subheader("Vargem Grande Paulista")
                if 'vargem_grande_paulista' in municipios:
                    top_vgp = df_entidades[df_entidades['municipio'] == 'vargem_grande_paulista'].nlargest(10, 'vl_pago')
                    st.dataframe(
                        top_vgp[['razao_social', 'vl_pago']].style.format({
                            'vl_pago': lambda x: formatar_valor_reais(x)
                        })
                    )
                else:
                    st.info("Dados não disponíveis para Vargem Grande Paulista")

    except Exception as e:
        st.error(f"Erro ao processar os dados: {str(e)}")
        st.exception(e)

if __name__ == '__main__':
    main()
