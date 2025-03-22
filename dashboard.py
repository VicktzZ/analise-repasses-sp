import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from utils.data_manager import *

st.set_page_config(
    page_title="Dashboard - Repasses Cotia",
    page_icon="📊",
    layout="wide"
)

def main():
    st.title("📊 Dashboard - Análise de Repasses Governamentais de Cotia")
    
    try:
        # Carregar dados uma única vez e salvar na sessão
        if 'df_cotia' not in st.session_state:
            df_cotia = carregar_dados_base()
            st.session_state['df_cotia'] = df_cotia
        else:
            df_cotia = st.session_state['df_cotia']
        
        # Métricas Principais
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total de Repasses", f"R$ {df_cotia['vl_pago'].sum():,.2f}")
        with col2:
            st.metric("Número de Entidades", df_cotia['razao_social'].nunique())
        with col3:
            st.metric("Total de Operações", len(df_cotia))
        with col4:
            st.metric("Média por Repasse", f"R$ {df_cotia['vl_pago'].mean():,.2f}")

        # Tabs para diferentes visualizações
        tab1, tab2, tab3, tab4 = st.tabs(["Evolução Temporal", "Distribuição por Função", "Top Entidades", "Estatísticas"])

        with tab1:
            st.subheader("Evolução dos Repasses ao Longo do Tempo")
            
            # Análise Temporal
            df_anual = df_cotia.groupby('exercicio').agg({
                'vl_pago': ['sum', 'mean']
            }).round(2)
            
            # Gráfico de evolução
            fig_temporal = go.Figure()
            fig_temporal.add_trace(go.Bar(
                x=df_anual.index,
                y=df_anual[('vl_pago', 'sum')],
                name='Total Anual'
            ))
            fig_temporal.add_trace(go.Scatter(
                x=df_anual.index,
                y=df_anual[('vl_pago', 'mean')],
                name='Média por Repasse',
                yaxis='y2'
            ))
            fig_temporal.update_layout(
                title='Evolução dos Repasses ao Longo dos Anos',
                yaxis=dict(title='Total de Repasses (R$)'),
                yaxis2=dict(title='Média por Repasse (R$)', overlaying='y', side='right')
            )
            st.plotly_chart(fig_temporal, use_container_width=True)

        with tab2:
            st.subheader("Distribuição por Função de Governo")
            
            # Gráfico de distribuição por função
            fig_funcao = px.treemap(
                df_cotia,
                path=['funcao_de_governo'],
                values='vl_pago',
                title='Distribuição dos Repasses por Função de Governo'
            )
            st.plotly_chart(fig_funcao, use_container_width=True)

        with tab3:
            st.subheader("Top Entidades Beneficiadas")
            
            # Análise das Entidades
            n_top = st.slider("Número de entidades:", 5, 20, 10)
            
            df_entidades = df_cotia.groupby('razao_social').agg({
                'vl_pago': 'sum',
                'funcao_de_governo': lambda x: ', '.join(set(x))
            }).sort_values('vl_pago', ascending=False).head(n_top)
            
            # Gráfico das top entidades
            fig_entidades = px.bar(
                df_entidades.reset_index(),
                x='razao_social',
                y='vl_pago',
                title=f'Top {n_top} Entidades por Valor Total de Repasses',
                labels={'razao_social': 'Entidade', 'vl_pago': 'Valor Total (R$)'}
            )
            fig_entidades.update_layout(xaxis_tickangle=45)
            st.plotly_chart(fig_entidades, use_container_width=True)

        with tab4:
            st.subheader("Estatísticas e Distribuição")
            
            # Box plot
            fig_dist = go.Figure()
            fig_dist.add_trace(go.Box(
                y=df_cotia['vl_pago'],
                name='Distribuição dos Valores'
            ))
            fig_dist.update_layout(
                title='Distribuição dos Valores dos Repasses',
                yaxis_title='Valor (R$)'
            )
            st.plotly_chart(fig_dist, use_container_width=True)

            # Estatísticas detalhadas
            stats = pd.DataFrame({
                'Estatística': [
                    'Total de Repasses',
                    'Média por Repasse',
                    'Mediana',
                    'Desvio Padrão',
                    'Mínimo',
                    'Máximo',
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
                    df_cotia['razao_social'].nunique(),
                    len(df_cotia)
                ]
            })
            
            st.dataframe(stats.style.format({
                'Valor': lambda x: f'R$ {x:,.2f}' if isinstance(x, (int, float)) and x > 100 else f'{x:,}'
            }))

    except Exception as e:
        st.error(f"Erro ao processar os dados: {str(e)}")
        st.exception(e)

if __name__ == '__main__':
    main()
