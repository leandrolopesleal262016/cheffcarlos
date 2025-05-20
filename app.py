from flask import Flask, render_template, jsonify, send_file, request, redirect, url_for, flash
import os
import pandas as pd
from glob import glob
import locale
import json
from datetime import datetime, timedelta
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = "fechamento_caixa_secret_key"  # Necessário para flash messages

DIRETORIO_ARQUIVOS = 'planilhas'
ARQUIVO_JSON = 'dados_historicos.json'
EXTENSOES_PERMITIDAS = {'xlsx', 'xls'}

# Criar o diretório se não existir
if not os.path.exists(DIRETORIO_ARQUIVOS):
    os.makedirs(DIRETORIO_ARQUIVOS)

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

# Mapeamento para nomes dos meses
NOMES_MESES = {
    1: 'Janeiro', 2: 'Fevereiro', 3: 'Março', 4: 'Abril',
    5: 'Maio', 6: 'Junho', 7: 'Julho', 8: 'Agosto',
    9: 'Setembro', 10: 'Outubro', 11: 'Novembro', 12: 'Dezembro'
}

def extensao_permitida(filename):
    """Verifica se a extensão do arquivo é permitida"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in EXTENSOES_PERMITIDAS

def carregar_dados():
    """Carrega dados das planilhas e processa-os"""
    arquivos = glob(os.path.join(DIRETORIO_ARQUIVOS, '*.xlsx')) + glob(os.path.join(DIRETORIO_ARQUIVOS, '*.xls'))
    df_list = []
    
    for arquivo in arquivos:
        try:
            planilha = pd.read_excel(arquivo, sheet_name=0)
            df_list.append(planilha)
        except Exception as e:
            print(f"Erro ao ler {arquivo}: {e}")
    
    if not df_list:
        return pd.DataFrame(), {}, {}, {}
    
    df = pd.concat(df_list, ignore_index=True)
    df['DATA'] = pd.to_datetime(df['DATA'])
    df['VALOR_TOTAL'] = df['VALOR DOS ITENS'] + df['TAXA DE ENTREGA']
    df['LUCRO'] = df['VALOR_TOTAL'] - df['INCENTIVO PROMOCIONAL DO IFOOD'].fillna(0) \
                - df['INCENTIVO PROMOCIONAL DA LOJA'].fillna(0) - df['TAXA DE SERVIÇO'].fillna(0)
    
    # Extrair dia da semana
    df['DIA_SEMANA_NUM'] = df['DATA'].dt.dayofweek
    df['DIA_SEMANA'] = df['DIA_SEMANA_NUM'].map(DIAS_SEMANA)
    
    # Extrair informações de data para agrupamentos
    df['DATA_DIA'] = df['DATA'].dt.date
    df['ANO'] = df['DATA'].dt.year
    df['MES'] = df['DATA'].dt.month
    df['SEMANA'] = df['DATA'].dt.isocalendar().week
    
    # Agrupar dados por dia, semana e mês
    dados_dia = agrupar_por_periodo(df, 'DATA_DIA')
    dados_semana = agrupar_por_periodo(df, ['ANO', 'SEMANA'])
    dados_mes = agrupar_por_periodo(df, ['ANO', 'MES'])
    
    # Salvar histórico em JSON
    salvar_historico(dados_dia, dados_semana, dados_mes)
    
    return df, dados_dia, dados_semana, dados_mes

def agrupar_por_periodo(df, periodo):
    """Agrupa dados por um período específico (dia, semana ou mês)"""
    if df.empty:
        return {}
    
    # Agrupar por período
    agrupado = df.groupby(periodo).agg({
        'VALOR_TOTAL': 'sum',
        'TAXA DE SERVIÇO': 'sum',
        'INCENTIVO PROMOCIONAL DO IFOOD': 'sum',
        'INCENTIVO PROMOCIONAL DA LOJA': 'sum',
        'LUCRO': 'sum',
        'RESTAURANTE': 'nunique',
        'DATA': 'count'
    }).reset_index()
    
    # Renomear colunas
    agrupado = agrupado.rename(columns={
        'DATA': 'NUM_PEDIDOS',
        'RESTAURANTE': 'NUM_RESTAURANTES'
    })
    
    # Converter período para string para facilitar a serialização
    if isinstance(periodo, list):
        # Usar a data mais recente como chave para semana e mês
        if 'SEMANA' in periodo:
            # Para semanas, vamos usar o formato "ANO-SEMANA"
            agrupado['PERIODO'] = agrupado.apply(lambda x: f"{int(x['ANO'])}-{int(x['SEMANA'])}", axis=1)
        elif 'MES' in periodo:
            # Para meses, vamos usar o formato "ANO-MES"
            agrupado['PERIODO'] = agrupado.apply(lambda x: f"{int(x['ANO'])}-{int(x['MES'])}", axis=1)
    else:
        # Para dias, usamos a própria data
        agrupado['PERIODO'] = agrupado[periodo].astype(str)
    
    # Calcular totais de incentivos
    agrupado['INCENTIVOS_TOTAL'] = agrupado['INCENTIVO PROMOCIONAL DO IFOOD'] + agrupado['INCENTIVO PROMOCIONAL DA LOJA']
    
    # Converter para dicionário com PERIODO como chave
    resultados = {}
    for _, row in agrupado.iterrows():
        periodo_str = row['PERIODO']
        resultados[periodo_str] = {
            'faturamento_bruto': round(float(row['VALOR_TOTAL']), 2),
            'taxas_servico': round(float(row['TAXA DE SERVIÇO']), 2),
            'incentivos': round(float(row['INCENTIVOS_TOTAL']), 2),
            'lucro': round(float(row['LUCRO']), 2),
            'num_pedidos': int(row['NUM_PEDIDOS']),
            'num_restaurantes': int(row['NUM_RESTAURANTES'])
        }
    
    return resultados

def salvar_historico(dados_dia, dados_semana, dados_mes):
    """Salva os dados históricos em um arquivo JSON"""
    try:
        # Verificar se já existe um arquivo JSON
        dados_existentes = {'diario': {}, 'semanal': {}, 'mensal': {}}
        if os.path.exists(ARQUIVO_JSON):
            with open(ARQUIVO_JSON, 'r') as f:
                dados_existentes = json.load(f)
        
        # Atualizar com novos dados
        dados_existentes['diario'].update(dados_dia)
        dados_existentes['semanal'].update(dados_semana)
        dados_existentes['mensal'].update(dados_mes)
        
        # Adicionar timestamp da última atualização
        dados_existentes['ultima_atualizacao'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Salvar no arquivo
        with open(ARQUIVO_JSON, 'w') as f:
            json.dump(dados_existentes, f, indent=4)
            
    except Exception as e:
        print(f"Erro ao salvar histórico: {e}")

def carregar_historico():
    """Carrega os dados históricos do arquivo JSON"""
    if os.path.exists(ARQUIVO_JSON):
        try:
            with open(ARQUIVO_JSON, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"Erro ao carregar histórico: {e}")
    
    return {'diario': {}, 'semanal': {}, 'mensal': {}, 'ultima_atualizacao': None}

def obter_resumo_atual(df, dados_dia, dados_semana, dados_mes):
    """Obtém o resumo dos dados para o dia atual, semana atual e mês atual"""
    if df.empty:
        return None, None, None
    
    # Obter a data mais recente no DataFrame
    data_atual = df['DATA'].max().date()
    ano_atual = data_atual.year
    mes_atual = data_atual.month
    
    # Calcular o número da semana atual
    semana_atual = data_atual.isocalendar()[1]
    
    # Chaves para os períodos atuais
    dia_atual_key = str(data_atual)
    semana_atual_key = f"{ano_atual}-{semana_atual}"
    mes_atual_key = f"{ano_atual}-{mes_atual}"
    
    # Obter os dados para os períodos atuais
    resumo_dia = dados_dia.get(dia_atual_key, None)
    resumo_semana = dados_semana.get(semana_atual_key, None)
    resumo_mes = dados_mes.get(mes_atual_key, None)
    
    return resumo_dia, resumo_semana, resumo_mes

def formatar_periodo_mes(periodo):
    """Formata um período no formato 'ANO-MES' para exibição"""
    try:
        # Correção do erro: garantir que lidamos corretamente com valores decimais
        partes = periodo.split('-')
        if len(partes) != 2:
            return periodo
            
        ano = partes[0]
        mes = partes[1]
        
        # Converter para int removendo qualquer possível parte decimal
        mes_int = int(float(mes))
        
        if mes_int in NOMES_MESES:
            return f"{NOMES_MESES[mes_int]}/{ano}"
        return periodo
    except Exception as e:
        print(f"Erro ao formatar período {periodo}: {e}")
        return periodo

def listar_arquivos():
    """Lista os arquivos na pasta planilhas"""
    extensoes = ['*.xlsx', '*.xls']
    arquivos = []
    
    for ext in extensoes:
        arquivos.extend(glob(os.path.join(DIRETORIO_ARQUIVOS, ext)))
    
    # Formatar informações dos arquivos
    arquivos_info = []
    for arquivo in arquivos:
        nome = os.path.basename(arquivo)
        tamanho = os.path.getsize(arquivo) / 1024  # KB
        data_modificacao = datetime.fromtimestamp(os.path.getmtime(arquivo)).strftime('%d/%m/%Y %H:%M')
        
        arquivos_info.append({
            'nome': nome,
            'tamanho': f"{tamanho:.1f} KB",
            'data': data_modificacao
        })
    
    return arquivos_info

@app.route('/')
def index():
    # Carregar todos os dados
    df, dados_dia, dados_semana, dados_mes = carregar_dados()
    
    if df.empty:
        # Se não há dados, mostrar mensagem sobre upload
        arquivos = listar_arquivos()
        return render_template('upload.html', arquivos=arquivos)
    
    # Obter histórico mais completo
    historico = carregar_historico()
    
    # Obter resumos para o dia, semana e mês atuais
    resumo_dia, resumo_semana, resumo_mes = obter_resumo_atual(df, dados_dia, dados_semana, dados_mes)
    
    # Verificar se temos os resumos
    if not resumo_dia:
        # Se não temos o dia atual, usar o dia mais recente
        if dados_dia:
            data_recente = max(dados_dia.keys())
            resumo_dia = dados_dia[data_recente]
        else:
            resumo_dia = {'faturamento_bruto': 0, 'taxas_servico': 0, 'incentivos': 0, 'lucro': 0}
    
    if not resumo_semana:
        # Se não temos a semana atual, usar a semana mais recente
        if dados_semana:
            semana_recente = max(dados_semana.keys())
            resumo_semana = dados_semana[semana_recente]
        else:
            resumo_semana = {'faturamento_bruto': 0, 'taxas_servico': 0, 'incentivos': 0, 'lucro': 0}
    
    if not resumo_mes:
        # Se não temos o mês atual, usar o mês mais recente
        if dados_mes:
            mes_recente = max(dados_mes.keys())
            resumo_mes = dados_mes[mes_recente]
        else:
            resumo_mes = {'faturamento_bruto': 0, 'taxas_servico': 0, 'incentivos': 0, 'lucro': 0}
    
    # Dados por dia da semana
    df_recente = df[df['DATA'] >= (df['DATA'].max() - timedelta(days=30))]
    pedidos_por_dia = df_recente.groupby(['DIA_SEMANA', 'DIA_SEMANA_NUM'])['VALOR_TOTAL'].sum().reset_index()
    pedidos_por_dia = pedidos_por_dia.sort_values('DIA_SEMANA_NUM')
    
    # Lista de dias da semana em português para mostrar no gráfico
    dias_semana = pedidos_por_dia['DIA_SEMANA'].tolist()
    valores_por_dia = pedidos_por_dia['VALOR_TOTAL'].tolist()
    
    # Dados para gráfico de pizza - Distribuição de lucro vs taxas vs incentivos (usando dados do mês)
    dados_pizza = {
        'Lucro Líquido': round(resumo_mes['lucro'], 2),
        'Taxas de Serviço': round(resumo_mes['taxas_servico'], 2),
        'Incentivos': round(resumo_mes['incentivos'], 2)
    }
    
    # Dados para gráfico de pizza - Volume de vendas por dia da semana
    vendas_por_dia = dict(zip(dias_semana, valores_por_dia))
    
    # Informações por restaurante
    restaurantes = df['RESTAURANTE'].unique().tolist()
    
    # Dados por restaurante
    dados_restaurantes = []
    cores_restaurantes = ['#3B82F6', '#10B981', '#F59E0B', '#EF4444', '#8B5CF6', '#EC4899']
    
    faturamento_bruto = resumo_mes['faturamento_bruto']
    
    for i, restaurante in enumerate(restaurantes):
        # Dados do restaurante
        df_rest = df[df['RESTAURANTE'] == restaurante]
        
        # Faturamento e contagem de pedidos
        faturamento_rest = df_rest['VALOR_TOTAL'].sum()
        num_pedidos = len(df_rest)
        ticket_medio = faturamento_rest / num_pedidos if num_pedidos > 0 else 0
        participacao = (faturamento_rest / faturamento_bruto * 100) if faturamento_bruto > 0 else 0
        
        # Pedidos por dia da semana
        pedidos_por_dia_rest = df_rest.groupby(['DIA_SEMANA', 'DIA_SEMANA_NUM']).size().reset_index(name='CONTAGEM')
        pedidos_por_dia_rest = pedidos_por_dia_rest.sort_values('DIA_SEMANA_NUM')
        
        # Criar dicionário com dias da semana como chaves e número de pedidos como valores
        contagem_dias = {dia: 0 for dia in DIAS_SEMANA.values()}
        for _, row in pedidos_por_dia_rest.iterrows():
            contagem_dias[row['DIA_SEMANA']] = row['CONTAGEM']
        
        # Definir cor do restaurante (usar cores cíclicas se houver mais restaurantes que cores)
        cor_index = i % len(cores_restaurantes)
        cor_restaurante = cores_restaurantes[cor_index]
        
        dados_restaurantes.append({
            'nome': restaurante,
            'faturamento': round(faturamento_rest, 2),
            'num_pedidos': num_pedidos,
            'ticket_medio': round(ticket_medio, 2),
            'participacao': round(participacao, 1),
            'pedidos_por_dia': contagem_dias,
            'cor': cor_restaurante
        })
    
    # Ordenar restaurantes por faturamento (do maior para o menor)
    dados_restaurantes.sort(key=lambda x: x['faturamento'], reverse=True)
    
    # Gerar dados históricos para gráficos de tendência
    tendencia_mensal = []
    for periodo, dados in historico['mensal'].items():
        # Formatar período para exibição
        periodo_formatado = formatar_periodo_mes(periodo)
        
        tendencia_mensal.append({
            'periodo': periodo,
            'periodo_formatado': periodo_formatado,
            'faturamento': dados['faturamento_bruto'],
            'lucro': dados['lucro']
        })
    
    # Ordenar histórico por período
    tendencia_mensal.sort(key=lambda x: x['periodo'])
    
    # Obter a data atual
    data_atual = df['DATA'].max().date()
    data_formatada = data_atual.strftime('%d/%m/%Y')
    
    # Obter a semana e mês atuais formatados
    semana_atual = data_atual.isocalendar()[1]
    mes_atual = data_atual.month
    mes_nome = NOMES_MESES.get(mes_atual, '')
    
    # Listar arquivos
    arquivos = listar_arquivos()
    
    return render_template('index.html',
                          # Resumos por período
                          faturamento_dia=resumo_dia['faturamento_bruto'],
                          taxas_dia=resumo_dia['taxas_servico'],
                          incentivos_dia=resumo_dia['incentivos'],
                          lucro_dia=resumo_dia['lucro'],
                          
                          faturamento_semana=resumo_semana['faturamento_bruto'],
                          taxas_semana=resumo_semana['taxas_servico'],
                          incentivos_semana=resumo_semana['incentivos'],
                          lucro_semana=resumo_semana['lucro'],
                          
                          faturamento_mes=resumo_mes['faturamento_bruto'],
                          taxas_mes=resumo_mes['taxas_servico'],
                          incentivos_mes=resumo_mes['incentivos'],
                          lucro_mes=resumo_mes['lucro'],
                          
                          # Informações de período
                          data_atual=data_formatada,
                          semana_atual=semana_atual,
                          mes_atual=mes_nome,
                          
                          # Dados para gráficos
                          labels=dias_semana,
                          valores=valores_por_dia,
                          dados_pizza=dados_pizza,
                          vendas_por_dia=vendas_por_dia,
                          restaurantes=dados_restaurantes,
                          tendencia_mensal=tendencia_mensal,
                          
                          # Informações de arquivos
                          arquivos=arquivos)

@app.route('/upload', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        # Verificar se o post tem o arquivo
        if 'arquivo' not in request.files:
            flash('Nenhum arquivo enviado', 'error')
            return redirect(request.url)
        
        arquivo = request.files['arquivo']
        
        # Se o usuário não selecionar um arquivo
        if arquivo.filename == '':
            flash('Nenhum arquivo selecionado', 'error')
            return redirect(request.url)
        
        if arquivo and extensao_permitida(arquivo.filename):
            # Salvar o arquivo com nome seguro
            filename = secure_filename(arquivo.filename)
            arquivo.save(os.path.join(DIRETORIO_ARQUIVOS, filename))
            flash(f'Arquivo {filename} carregado com sucesso!', 'success')
            return redirect(url_for('index'))
        else:
            flash('Formato de arquivo não permitido. Use .xlsx ou .xls', 'error')
            return redirect(request.url)
    
    # Listar arquivos existentes para o GET request
    arquivos = listar_arquivos()
    return render_template('upload.html', arquivos=arquivos)

@app.route('/excluir/<filename>')
def excluir_arquivo(filename):
    """Exclui um arquivo da pasta planilhas"""
    try:
        caminho_arquivo = os.path.join(DIRETORIO_ARQUIVOS, secure_filename(filename))
        if os.path.exists(caminho_arquivo):
            os.remove(caminho_arquivo)
            flash(f'Arquivo {filename} excluído com sucesso!', 'success')
        else:
            flash(f'Arquivo {filename} não encontrado.', 'error')
    except Exception as e:
        flash(f'Erro ao excluir arquivo: {str(e)}', 'error')
    
    return redirect(url_for('upload_file'))

@app.route('/api/resumo')
def api_resumo():
    """API para obter resumo dos dados em formato JSON"""
    historico = carregar_historico()
    return jsonify(historico)

@app.route('/api/exportar/json')
def exportar_json():
    """Exporta os dados históricos como JSON"""
    if os.path.exists(ARQUIVO_JSON):
        return send_file(ARQUIVO_JSON, 
                         mimetype='application/json',
                         as_attachment=True,
                         download_name='historico_fechamento.json')
    return jsonify({"erro": "Nenhum dado histórico encontrado"}), 404

if __name__ == '__main__':
    app.run(debug=True)