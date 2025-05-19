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
        df['DATA_FORMATADA'] = df['DATA'].dt.strftime('%A, %d/%m').str.capitalize()
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

    pedidos_por_dia = df.groupby(['DATA', 'DATA_FORMATADA'])['VALOR_TOTAL'].sum().reset_index()
    pedidos_por_dia = pedidos_por_dia.sort_values('DATA')

    return render_template('index.html',
                           faturamento=round(faturamento_bruto, 2),
                           taxas=round(taxas_servico, 2),
                           incentivos=round(incentivos, 2),
                           lucro=round(lucro, 2),
                           labels=pedidos_por_dia['DATA_FORMATADA'].tolist(),
                           valores=pedidos_por_dia['VALOR_TOTAL'].tolist())

if __name__ == '__main__':
    app.run(debug=True)
