from flask import Flask, render_template
import os
import pandas as pd
from glob import glob
import locale

app = Flask(__name__)

DIRETORIO_ARQUIVOS = 'planilhas'

# Define localidade para português do Brasil
try:
    locale.setlocale(locale.LC_TIME, 'pt_BR.utf8')
except:
    try:
        locale.setlocale(locale.LC_TIME, 'pt_BR')
    except:
        pass

# Mapeamento correto para dias da semana em português
DIAS_SEMANA = {
    0: 'Segunda-feira',
    1: 'Terça-feira',
    2: 'Quarta-feira',
    3: 'Quinta-feira',
    4: 'Sexta-feira',
    5: 'Sábado',
    6: 'Domingo'
}

def carregar_dados():
    arquivos = glob(os.path.join(DIRETORIO_ARQUIVOS, '*.xlsx'))
    df_list = []
    for arquivo in arquivos:
        try:
            planilha = pd.read_excel(arquivo, sheet_name=0)
            df_list.append(planilha)
        except Exception as e:
            print(f"Erro ao ler {arquivo}: {e}")
    if df_list:
        df = pd.concat(df_list, ignore_index=True)
        df['DATA'] = pd.to_datetime(df['DATA'])
        df['VALOR_TOTAL'] = df['VALOR DOS ITENS'] + df['TAXA DE ENTREGA']
        df['LUCRO'] = df['VALOR_TOTAL'] - df['INCENTIVO PROMOCIONAL DO IFOOD'].fillna(0) \
                    - df['INCENTIVO PROMOCIONAL DA LOJA'].fillna(0) - df['TAXA DE SERVIÇO'].fillna(0)
        
        # Extrair apenas o dia da semana para agrupar corretamente
        df['DIA_SEMANA_NUM'] = df['DATA'].dt.dayofweek  # 0 = Segunda, 6 = Domingo
        # Usar nosso mapeamento em português
        df['DIA_SEMANA'] = df['DIA_SEMANA_NUM'].map(DIAS_SEMANA)
        
        return df
    return pd.DataFrame()

@app.route('/')
def index():
    df = carregar_dados()
    if df.empty:
        return "Nenhum dado encontrado. Adicione arquivos .xlsx na pasta 'planilhas'."

    faturamento_bruto = df['VALOR_TOTAL'].sum()
    taxas_servico = df['TAXA DE SERVIÇO'].sum()
    incentivos = df['INCENTIVO PROMOCIONAL DO IFOOD'].sum() + df['INCENTIVO PROMOCIONAL DA LOJA'].sum()
    lucro = df['LUCRO'].sum()

    # Agrupar por dia da semana e ordenar corretamente
    pedidos_por_dia = df.groupby(['DIA_SEMANA', 'DIA_SEMANA_NUM'])['VALOR_TOTAL'].sum().reset_index()
    pedidos_por_dia = pedidos_por_dia.sort_values('DIA_SEMANA_NUM')
    
    # Lista de dias da semana em português para mostrar no gráfico
    dias_semana = pedidos_por_dia['DIA_SEMANA'].tolist()
    valores_por_dia = pedidos_por_dia['VALOR_TOTAL'].tolist()
    
    # Dados para gráfico de pizza - Distribuição de lucro vs taxas vs incentivos
    dados_pizza = {
        'Lucro Líquido': round(lucro, 2),
        'Taxas de Serviço': round(taxas_servico, 2),
        'Incentivos': round(incentivos, 2)
    }
    
    # Dados para gráfico de pizza - Volume de vendas por dia da semana
    vendas_por_dia = dict(zip(dias_semana, valores_por_dia))
    
    return render_template('index.html',
                           faturamento=round(faturamento_bruto, 2),
                           taxas=round(taxas_servico, 2),
                           incentivos=round(incentivos, 2),
                           lucro=round(lucro, 2),
                           labels=dias_semana,
                           valores=valores_por_dia,
                           dados_pizza=dados_pizza,
                           vendas_por_dia=vendas_por_dia)

if __name__ == '__main__':
    app.run(debug=True)