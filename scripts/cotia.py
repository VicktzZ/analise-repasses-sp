import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import os
import xlwings as xw

arquivo_excel = 'data/repasses.xlsx'

def repasses_cotia():
    print(f"Tentando ler o arquivo: {os.path.abspath(arquivo_excel)}")
    try:
        app = xw.App(visible=False)
        wb = app.books.open(os.path.abspath(arquivo_excel))
        sht = wb.sheets[0]
        
        df = sht.used_range.options(pd.DataFrame, index=False, header=True).value

        wb.close()
        app.quit()
        
        print(f"Arquivo carregado com sucesso. Shape: {df.shape}")
        
        df_cotia = df[df['municipio'].str.lower() == 'cotia'].copy()
        print(f"\nDados filtrados para Cotia. Shape: {df_cotia.shape}")

        if df_cotia.empty:
            print("ATENÇÃO: Nenhum dado encontrado para o município de Cotia!")
        else:
            # 1. Análise Temporal
            repasses_por_ano = df_cotia.groupby('exercicio')['vl_pago'].agg(['sum', 'count', 'mean']).round(2)
            repasses_por_ano.columns = ['Total', 'Quantidade', 'Média']
            print("\n1. Análise Temporal dos Repasses:")
            print(repasses_por_ano)

            # Gráfico de evolução temporal
            fig_temporal = go.Figure()
            fig_temporal.add_trace(go.Bar(
                x=repasses_por_ano.index,
                y=repasses_por_ano['Total'],
                name='Total Anual'
            ))
            fig_temporal.add_trace(go.Scatter(
                x=repasses_por_ano.index,
                y=repasses_por_ano['Média'],
                name='Média por Repasse',
                yaxis='y2'
            ))
            fig_temporal.update_layout(
                title='Evolução dos Repasses ao Longo dos Anos',
                yaxis=dict(title='Total de Repasses (R$)'),
                yaxis2=dict(title='Média por Repasse (R$)', overlaying='y', side='right')
            )
            fig_temporal.show()

            # 2. Análise por Função de Governo
            analise_funcao = df_cotia.groupby('funcao_de_governo').agg({
                'vl_pago': ['sum', 'count', 'mean', 'std'],
                'razao_social': 'nunique'
            }).round(2)
            analise_funcao.columns = ['Total', 'Quantidade', 'Média', 'Desvio Padrão', 'Entidades Únicas']
            print("\n2. Análise por Função de Governo:")
            print(analise_funcao)

            # Gráfico de distribuição por função
            fig_funcao = px.treemap(
                df_cotia,
                path=['funcao_de_governo'],
                values='vl_pago',
                title='Distribuição dos Repasses por Função de Governo'
            )
            fig_funcao.show()

            # 3. Análise das Entidades Beneficiadas
            top_entidades = df_cotia.groupby('razao_social').agg({
                'vl_pago': 'sum',
                'funcao_de_governo': 'unique'
            }).sort_values('vl_pago', ascending=False).head(10)
            
            print("\n3. Top 10 Entidades que Receberam Repasses:")
            for idx, row in top_entidades.iterrows():
                print(f"\n{idx}")
                print(f"Total Recebido: R$ {row['vl_pago']:,.2f}")
                print(f"Áreas de Atuação: {', '.join(row['funcao_de_governo'])}")

            # Gráfico das top entidades
            fig_entidades = px.bar(
                top_entidades.reset_index(),
                x='razao_social',
                y='vl_pago',
                title='Top 10 Entidades por Valor Total de Repasses',
                labels={'razao_social': 'Entidade', 'vl_pago': 'Valor Total (R$)'}
            )
            fig_entidades.update_layout(xaxis_tickangle=45)
            fig_entidades.show()

            # 4. Estatísticas Gerais
            print("\n4. Estatísticas Gerais:")
            print(f"Total de Repasses: R$ {df_cotia['vl_pago'].sum():,.2f}")
            print(f"Média por Repasse: R$ {df_cotia['vl_pago'].mean():,.2f}")
            print(f"Mediana dos Repasses: R$ {df_cotia['vl_pago'].median():,.2f}")
            print(f"Desvio Padrão: R$ {df_cotia['vl_pago'].std():,.2f}")
            print(f"Menor Repasse: R$ {df_cotia['vl_pago'].min():,.2f}")
            print(f"Maior Repasse: R$ {df_cotia['vl_pago'].max():,.2f}")
            print(f"Total de Entidades Beneficiadas: {df_cotia['razao_social'].nunique()}")
            print(f"Total de Repasses Realizados: {len(df_cotia)}")

            # 5. Análise de Distribuição dos Valores
            fig_dist = go.Figure()
            fig_dist.add_trace(go.Box(
                y=df_cotia['vl_pago'],
                name='Distribuição dos Valores'
            ))
            fig_dist.update_layout(
                title='Distribuição dos Valores dos Repasses',
                yaxis_title='Valor (R$)'
            )
            fig_dist.show()

    except Exception as e:
        print(f"Erro ao processar os dados: {str(e)}")
        print(f"Tipo do erro: {type(e)}")
        import traceback
        traceback.print_exc()
        raise
    finally:
        try:
            app.quit()
        except:
            pass