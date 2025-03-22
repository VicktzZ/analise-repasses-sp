import streamlit as st
import pandas as pd
import plotly.express as px
from utils.data_manager import formatar_valor_reais as fvr

st.set_page_config(
    page_title="Tabelas - Repasses Cotia",
    page_icon="",
    layout="wide"
)

def main():
    st.title("Visualização Detalhada das Tabelas")
    
    try:
        # Carregar dados do dashboard principal
        df_cotia = st.session_state['df_cotia'] if 'df_cotia' in st.session_state else None
        
        if df_cotia is None:
            st.error("Por favor, acesse primeiro a página principal do dashboard.")
            return
        
        # Seletor de visualização
        visualizacao = st.selectbox(
            "Escolha a visualização:",
            ["Dados Brutos", "Por Ano", "Por Função", "Por Entidade", "Estatísticas Avançadas"]
        )
        
        if visualizacao == "Dados Brutos":
            st.subheader("Dados Brutos dos Repasses")
            
            # Filtros
            col1, col2, col3 = st.columns(3)
            with col1:
                anos = sorted(df_cotia['exercicio'].unique())
                ano_selecionado = st.multiselect("Filtrar por Ano:", anos, default=anos)
            
            with col2:
                funcoes = sorted(df_cotia['funcao_de_governo'].unique())
                funcao_selecionada = st.multiselect("Filtrar por Função:", funcoes, default=funcoes)
            
            with col3:
                valor_min = float(df_cotia['vl_pago'].min())
                valor_max = float(df_cotia['vl_pago'].max())
                faixa_valor = st.slider(
                    "Faixa de Valor (R$):",
                    valor_min,
                    valor_max,
                    (valor_min, valor_max),
                    format="R$ %.2f"
                )
            
            # Aplicar filtros
            df_filtrado = df_cotia[
                (df_cotia['exercicio'].isin(ano_selecionado)) &
                (df_cotia['funcao_de_governo'].isin(funcao_selecionada)) &
                (df_cotia['vl_pago'].between(faixa_valor[0], faixa_valor[1]))
            ]
            
            # Mostrar dados filtrados
            st.dataframe(
                df_filtrado.style.format({
                    'vl_pago': lambda x: fvr(x)
                }),
                height=400
            )
            
            # Estatísticas básicas dos dados filtrados
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Total de Registros", f"{len(df_filtrado):,}")
            with col2:
                st.metric("Valor Total", fvr(df_filtrado['vl_pago'].sum()))
            with col3:
                st.metric("Média por Repasse", fvr(df_filtrado['vl_pago'].mean()))
        
        elif visualizacao == "Por Ano":
            st.subheader("Análise Anual dos Repasses")
            
            # Agregação por ano
            df_anual = df_cotia.groupby('exercicio').agg({
                'vl_pago': ['count', 'sum', 'mean', 'std'],
                'razao_social': 'nunique'
            }).round(2)
            
            # Renomear colunas
            df_anual.columns = ['Quantidade', 'Total', 'Média', 'Desvio Padrão', 'Entidades']
            
            # Gráfico de evolução
            fig = px.line(
                df_anual.reset_index(),
                x='exercicio',
                y=['Total', 'Média'],
                title='Evolução Anual dos Repasses'
            )
            fig.update_layout(
                yaxis=dict(tickformat=',.2f', tickprefix='R$ '),
                hovermode='x unified'
            )
            fig.update_traces(
                hovertemplate="Ano: %{x}<br>Valor: R$ %{y:,.2f}<extra></extra>"
            )
            st.plotly_chart(fig, use_container_width=True)
            
            # Tabela detalhada
            st.dataframe(
                df_anual.style.format({
                    'Total': lambda x: fvr(x),
                    'Média': lambda x: fvr(x),
                    'Desvio Padrão': lambda x: fvr(x),
                    'Quantidade': '{:,}',
                    'Entidades': '{:,}'
                })
            )
        
        elif visualizacao == "Por Função":
            st.subheader("Análise por Função de Governo")
            
            # Agregação por função
            df_funcao = df_cotia.groupby('funcao_de_governo').agg({
                'vl_pago': ['count', 'sum', 'mean', 'std'],
                'razao_social': 'nunique'
            }).round(2)
            
            # Renomear colunas
            df_funcao.columns = ['Quantidade', 'Total', 'Média', 'Desvio Padrão', 'Entidades']
            
            # Gráfico de pizza
            fig = px.pie(
                df_funcao.reset_index(),
                values='Total',
                names='funcao_de_governo',
                title='Distribuição dos Repasses por Função'
            )
            fig.update_traces(
                texttemplate="%{label}<br>R$ %{value:,.2f}",
                hovertemplate="Função: %{label}<br>Total: R$ %{value:,.2f}<extra></extra>"
            )
            st.plotly_chart(fig, use_container_width=True)
            
            # Tabela detalhada
            st.dataframe(
                df_funcao.style.format({
                    'Total': lambda x: fvr(x),
                    'Média': lambda x: fvr(x),
                    'Desvio Padrão': lambda x: fvr(x),
                    'Quantidade': '{:,}',
                    'Entidades': '{:,}'
                })
            )
        
        elif visualizacao == "Por Entidade":
            st.subheader("Análise por Entidade")
            
            # Número de entidades para mostrar
            n_entidades = st.slider("Número de entidades:", 5, 50, 10)
            
            # Agregação por entidade
            df_entidade = df_cotia.groupby('razao_social').agg({
                'vl_pago': ['count', 'sum', 'mean'],
                'funcao_de_governo': lambda x: ', '.join(set(x))
            }).round(2)
            
            # Renomear colunas
            df_entidade.columns = ['Quantidade', 'Total', 'Média', 'Áreas']
            df_entidade = df_entidade.sort_values('Total', ascending=False).head(n_entidades)
            
            # Gráfico de barras
            fig = px.bar(
                df_entidade.reset_index(),
                x='razao_social',
                y='Total',
                title=f'Top {n_entidades} Entidades por Valor Total'
            )
            fig.update_layout(
                xaxis_tickangle=45,
                yaxis=dict(tickformat=',.2f', tickprefix='R$ ')
            )
            fig.update_traces(
                hovertemplate="Entidade: %{x}<br>Total: R$ %{y:,.2f}<extra></extra>"
            )
            st.plotly_chart(fig, use_container_width=True)
            
            # Tabela detalhada
            st.dataframe(
                df_entidade.style.format({
                    'Total': lambda x: fvr(x),
                    'Média': lambda x: fvr(x),
                    'Quantidade': '{:,}'
                })
            )
        
        else:  # Estatísticas Avançadas
            st.subheader("Estatísticas Avançadas")
            
            # Box plot
            fig = px.box(
                df_cotia,
                y='vl_pago',
                title='Distribuição dos Valores dos Repasses'
            )
            fig.update_layout(
                yaxis=dict(
                    title='Valor (R$)',
                    tickformat=',.2f',
                    tickprefix='R$ '
                )
            )
            fig.update_traces(
                hovertemplate="Valor: R$ %{y:,.2f}<extra></extra>"
            )
            st.plotly_chart(fig, use_container_width=True)
            
            # Estatísticas detalhadas
            stats = pd.DataFrame({
                'Estatística': [
                    'Total de Repasses',
                    'Média por Repasse',
                    'Mediana',
                    'Desvio Padrão',
                    'Mínimo',
                    'Máximo',
                    'Assimetria',
                    'Curtose',
                    'Número de Entidades',
                    'Número de Operações'
                ],
                'Valor': [
                    df_cotia['vl_pago'].sum(),
                    df_cotia['vl_pago'].mean(),
                    df_cotia['vl_pago'].median(),
                    df_cotia['vl_pago'].std(),
                    df_cotia['vl_pago'].min(),
                    df_cotia['vl_pago'].max(),
                    df_cotia['vl_pago'].skew(),
                    df_cotia['vl_pago'].kurtosis(),
                    df_cotia['razao_social'].nunique(),
                    len(df_cotia)
                ]
            })
            
            st.dataframe(
                stats.style.format({
                    'Valor': lambda x: fvr(x) if isinstance(x, (int, float)) and x > 100 else f"{x:,.4f}"
                })
            )

    except Exception as e:
        st.error(f"Erro ao carregar os dados: {str(e)}")
        st.exception(e)

if __name__ == '__main__':
    main()
