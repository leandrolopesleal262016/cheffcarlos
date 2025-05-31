from flask import Flask, render_template, request, jsonify, redirect, url_for, flash
from datetime import datetime, date
import sqlite3
import json

app = Flask(__name__)
app.secret_key = 'cheff_carlos_secret_key_2024'

# Configuração do banco de dados
DATABASE = 'pedidos.db'

# Dados do cardápio organizados (atualizado com novos itens)
CARDAPIO = {
    'Pratos': {
        # La Parmegiana Completa
        'La Parmegiana Frango individual completa': 39.90,
        'La Parmegiana Frango 2 pessoas completa': 65.90,
        'La Parmegiana Frango 3 pessoas completa': 95.90,
        'La Parmegiana de Carne individual completa': 49.90,
        'La Parmegiana Carne 2 pessoas completa': 75.90,
        'La Parmegiana Carne 3 pessoas completa': 105.90,
        'La Parmegiana Filé Mignon individual (completa)': 59.90,
        'La Parmegiana Filé Mignon 2 pessoas (completa)': 99.90,
        'La Parmegiana Filé Mignon 3 pessoas (completa)': 169.90,
        
        # Parmegiana com Presunto e Queijo
        'La Parmegiana Frango com Presunto e queijo (individual)': 45.90,
        'La Parmegiana Frango com Presunto e Queijo (2 pessoas)': 75.90,
        'La Parmegiana Frango com Presunto e Queijo (3 pessoas)': 105.90,
        'La Parmegiana de Carne com Presunto e Queijo (Individual)': 55.90,
        'La Parmegiana Carne com Presunto e Queijo (2 pessoas)': 89.90,
        'La Parmegiana Carne Presunto e Queijo (3 pessoas)': 115.90,
        'La Parmegiana Filé Mignon com Presunto e Queijo (individual)': 65.90,
        'La Parmegiana Filé Mignon com Presunto e Queijo (2 pessoas)': 139.90,
        'La Parmegiana Filé Mignon com Presunto e Queijo (3 pessoas)': 185.90,
        
        # Porção Parmegiana (Sem acompanhamentos)
        'Porção Parmegiana Frango individual ( Sem acompanhamentos )': 25.90,
        'Porção Parmegiana Frango 2 pessoas ( Sem acompanhamentos )': 45.90,
        'Porção Parmegiana Frango 3 pessoas ( Sem acompanhamentos )': 69.90,
        'Porção Parmegiana de Carne 1 pessoas ( Sem acompanhamentos )': 35.90,
        'Porção Parmegiana Alcatra 2 pessoas ( Sem acompanhamentos )': 55.90,
        'Porção Parmegiana Alcatra 3 pessoas ( Sem acompanhamentos )': 79.90,
        
        # Combo Macarrão & Parmegiana
        'Combo especial de carne (1 pessoa )': 59.90,
        'Combo Especial de Carne 2 pessoas': 89.90,
        'Combo Especial de Carne 3 pessoas': 119.90,
        'Combo especial De Frango indiviadual': 54.90,
        'Combo Especial Frango 2 Pessoas': 84.90,
        'Combo Especial frango 3 Pessoas': 114.90,
        'Como Especial de Filé Mignon Individual': 75.90,
        'Como especial Filé Mignon 2 pessoas': 119.90,
        'Como Especial Filé Mignon 3 pessoas': 179.90,
        
        # Combinhos do Cheff
        'Combinho Frango 2 pessoas': 65.90,
        'Combinho Frango 3 pessoas': 94.90,
        'Combinho de Carne 2 pessoas': 75.90,
        'Combinho de Carne 3 pessoas': 105.90,
        'Combinho Filé Mignon 2 pessoas': 99.90,
        
        # Massas Frescas Artesanais 500g
        'Talharim ao molho sugo (500)': 34.90,
        'Talharim à bolonhesa (500gr)': 37.90,
        'Talharim ao molho formaggio (500gr)': 44.90,
        'Talharim ao molho bechamel (500gr)': 34.90,
        
        # Massas Frescas Artesanais 1kg
        'Talharim ao molho sugo (1kg)': 49.90,
        'Talharim à bolonhesa (1kg)': 62.90,
        'Talharim ao molho formaggio (1kg)': 59.90,
        'Talharim ao molho bechamel (1kg)': 55.90,
        
        # Do Dia (Pratos do Dia)
        'Do Dia Frango Parmegiana': 29.90,
        'Do Dia Mignom A Parmegiana': 55.90,
        'Do Dia Patinho A Parmegiana': 33.90,
        'Do Dia Tilápia A Parmegiana': 38.90,
        'Do Dia Beringela A Parmegiana': 26.90,
        
        # Parmegianas Especiais do Cheff
        'Parmegiana de Mignon para 2 pessoas': 75.90,
        'Parmegiana de mignon para 3 pessoas': 144.90,
        'Parmegiana de mignon para 5 pessoas': 229.90,
        'Frango a Parmegiana para 5 pessoas': 179.90,
        'Frango a Parmegiana para 3 pessoas': 109.90,
        'Frango a Parmegiana para 2 pessoas': 59.90,
        'Tilápia a Parmegiana p/ 5 pessoas': 199.90,
        'Tilapia a Parmegiana p/ 3 pessoas': 145.90,
        'Tilápia a Parmegiana para 2 pessoas': 69.90,
        'Beringela A Parmegiana 1 pessoa': 79.90,
        'Beringela A Parmegiana 3 pessoas': 109.90,
        'Beringela A Parmegiana 5 pessoas': 179.90,
        
        # Especial P/ 2 Pessoas
        'Patinho 2 Pessoas A Parmegiana (4 filés)': 99.90,
        'File de Frango P/ 2 Pessoas A Parmegiana (4 filés)': 79.90,
        
        # Rondelli
        'Rondelli 4 Queijos Ao Sugo': 46.90,
        'Rondelli de espinafre': 46.90
    },
    'Complementos': {
        'Batata chips 25g': 6.90,
        'Batata Chips 25g': 6.90,
        'Adicional de Arroz': 15.00,
        'Adicional De Arroz': 18.00,
        'Adicional Bife De Patinho Parmegiana': 19.90,
        'Adicional Filé De Frango A Parmegiana': 17.90,
        'Adicional De Berinjela A Parmegiana': 17.90,
        'Adicional De Molho De Tomate': 19.90
    },
    'Sobremesas': {
        'GELADINHO GOURMET DE MORANGO': 7.50,
        'Geladinho Gourmet Morango': 7.50
    },
    'Bebidas': {
        'Coca-Cola Lata 350ml': 6.00,
        'Coca lata': 6.00,
        'Coca-Cola Original 350m': 6.00,
        'Coca-Cola sem Açúcar 310ml': 6.00,
        'Coca lata zero': 6.00,
        'Coca-Cola sem Açúcar 350ml': 8.00,
        'Refrigerante Taubaiana Guarana 450ml': 6.00,
        'Kuat Guaraná 2l': 10.00,
        'Coca-Cola Original 2l': 15.00,
        'Coca 2 litros': 16.00,
        'Coca-Cola Garrafa 2l': 18.00,
        'Coca-Cola sem Açúcar 2l': 15.00,
        'Água Crystal sem Gás 500ml': 7.00,
        'Água': 4.00,
        'CERVEJA ORIGINAL LATA': 9.00,
        'Cerveja Original lata': 9.00,
        'Refrigerante Guaraná Conti Pet 2l': 10.00,
        'Pepsi 200ml': 4.00
    }
}

CATEGORIAS_SAIDA = [
    'Mercado', 'Funcionário', 'Açougue', 'Verduras/Legumes', 
    'Bebidas/Fornecedor', 'Manutenção', 'Limpeza', 'Combustível',
    'Conta de Luz', 'Conta de Água', 'Internet', 'Aluguel', 'Outros'
]

FORMAS_PAGAMENTO = [
    'PIX', 'Dinheiro', 'Cartão Débito', 'Cartão Crédito', 
    'Ticket', 'Alelo', 'Pluxee', 'Vero Card', 'VR', 
    'Conta', 'Permuta', 'Cortesia'
]

def init_db():
    """Inicializa o banco de dados com as tabelas necessárias"""
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    
    # Tabela de clientes
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS clientes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            telefone TEXT,
            endereco TEXT,
            data_cadastro DATE DEFAULT CURRENT_DATE,
            UNIQUE(nome, telefone)
        )
    ''')
    
    # Tabela de itens do cardápio
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS cardapio_itens (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL UNIQUE,
            categoria TEXT NOT NULL,
            preco REAL NOT NULL,
            ativo BOOLEAN DEFAULT 1,
            data_criacao DATETIME DEFAULT CURRENT_TIMESTAMP,
            data_atualizacao DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Tabela de pedidos
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS pedidos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            cliente_nome TEXT NOT NULL,
            cliente_telefone TEXT,
            cliente_endereco TEXT,
            eh_balcao BOOLEAN DEFAULT 0,
            pratos TEXT,  -- JSON string com pratos e quantidades
            bebidas TEXT, -- JSON string com bebidas e quantidades
            forma_pagamento TEXT,
            valor_total REAL,
            data_pedido DATE DEFAULT CURRENT_DATE,
            hora_pedido DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Tabela de saídas/despesas
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS saidas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            categoria TEXT NOT NULL,
            descricao TEXT,
            valor REAL NOT NULL,
            data_saida DATE DEFAULT CURRENT_DATE,
            hora_saida DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    conn.commit()
    
    # Migrar dados existentes para a nova tabela se ela estiver vazia
    migrar_cardapio_inicial(conn)
    
    conn.close()

def migrar_cardapio_inicial(conn):
    """Migra os dados do cardápio para o banco se não existirem"""
    cursor = conn.cursor()
    
    # Verificar se já existem dados
    count = cursor.execute('SELECT COUNT(*) FROM cardapio_itens').fetchone()[0]
    
    if count == 0:
        # Inserir dados iniciais do cardápio
        for categoria, itens in CARDAPIO.items():
            for nome, preco in itens.items():
                cursor.execute('''
                    INSERT INTO cardapio_itens (nome, categoria, preco)
                    VALUES (?, ?, ?)
                ''', (nome, categoria, preco))
        
        conn.commit()

def get_preco_item(nome_item):
    """Busca o preço de um item em todas as categorias"""
    for categoria, itens in CARDAPIO.items():
        if nome_item in itens:
            return itens[nome_item]
    return 0

def get_db_connection():
    """Retorna uma conexão com o banco de dados"""
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/')
def index():
    """Página principal com as abas"""
    return render_template('index.html', 
                         cardapio=CARDAPIO, 
                         categorias_saida=CATEGORIAS_SAIDA,
                         formas_pagamento=FORMAS_PAGAMENTO)

@app.route('/api/buscar_cliente')
def buscar_cliente():
    """API para buscar dados do cliente por nome ou telefone"""
    termo = request.args.get('termo', '').strip()
    
    if not termo:
        return jsonify({'cliente': None})
    
    conn = get_db_connection()
    
    # Buscar cliente por nome ou telefone (busca parcial)
    cliente = conn.execute('''
        SELECT nome, telefone, endereco 
        FROM clientes 
        WHERE nome LIKE ? OR telefone LIKE ?
        ORDER BY data_cadastro DESC
        LIMIT 1
    ''', (f'%{termo}%', f'%{termo}%')).fetchone()
    
    conn.close()
    
    if cliente:
        return jsonify({
            'cliente': {
                'nome': cliente['nome'],
                'telefone': cliente['telefone'],
                'endereco': cliente['endereco']
            }
        })
    else:
        return jsonify({'cliente': None})

@app.route('/api/cardapio')
def listar_cardapio():
    """API para listar todos os itens do cardápio"""
    conn = get_db_connection()
    
    itens = conn.execute('''
        SELECT id, nome, categoria, preco, ativo 
        FROM cardapio_itens 
        WHERE ativo = 1
        ORDER BY categoria, nome
    ''').fetchall()
    
    conn.close()
    
    itens_list = []
    for item in itens:
        itens_list.append({
            'id': item['id'],
            'nome': item['nome'],
            'categoria': item['categoria'],
            'preco': item['preco'],
            'ativo': item['ativo']
        })
    
    return jsonify(itens_list)

@app.route('/api/cardapio', methods=['POST'])
def criar_item_cardapio():
    """API para criar novo item no cardápio"""
    try:
        data = request.get_json()
        nome = data.get('nome')
        categoria = data.get('categoria')
        preco = float(data.get('preco'))
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO cardapio_itens (nome, categoria, preco)
            VALUES (?, ?, ?)
        ''', (nome, categoria, preco))
        
        item_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return jsonify({
            'success': True, 
            'message': 'Item criado com sucesso!',
            'id': item_id
        })
        
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/cardapio/<int:item_id>', methods=['PUT'])
def atualizar_item_cardapio(item_id):
    """API para atualizar item do cardápio"""
    try:
        data = request.get_json()
        nome = data.get('nome')
        categoria = data.get('categoria')
        preco = float(data.get('preco'))
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE cardapio_itens 
            SET nome = ?, categoria = ?, preco = ?, data_atualizacao = datetime('now', 'localtime')
            WHERE id = ?
        ''', (nome, categoria, preco, item_id))
        
        conn.commit()
        conn.close()
        
        return jsonify({
            'success': True, 
            'message': 'Item atualizado com sucesso!'
        })
        
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/cardapio/<int:item_id>', methods=['DELETE'])
def excluir_item_cardapio(item_id):
    """API para excluir item do cardápio (soft delete)"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE cardapio_itens 
            SET ativo = 0, data_atualizacao = datetime('now', 'localtime')
            WHERE id = ?
        ''', (item_id,))
        
        conn.commit()
        conn.close()
        
        return jsonify({
            'success': True, 
            'message': 'Item removido com sucesso!'
        })
        
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/cardapio/categorias')
def listar_categorias():
    """API para listar categorias disponíveis"""
    categorias = list(CARDAPIO.keys())
    return jsonify(categorias)
def listar_clientes():
    """API para listar clientes para autocompletar"""
    termo = request.args.get('termo', '').strip()
    
    conn = get_db_connection()
    
    if termo:
        clientes = conn.execute('''
            SELECT DISTINCT nome, telefone 
            FROM clientes 
            WHERE nome LIKE ? OR telefone LIKE ?
            ORDER BY nome
            LIMIT 10
        ''', (f'%{termo}%', f'%{termo}%')).fetchall()
    else:
        clientes = conn.execute('''
            SELECT DISTINCT nome, telefone 
            FROM clientes 
            ORDER BY nome
            LIMIT 10
        ''').fetchall()
    
    conn.close()
    
    clientes_list = []
    for cliente in clientes:
        clientes_list.append({
            'nome': cliente['nome'],
            'telefone': cliente['telefone']
        })
    
    return jsonify(clientes_list)
def calcular_total():
    """API para calcular o total do pedido"""
    data = request.get_json()
    pratos = data.get('pratos', {})
    bebidas = data.get('bebidas', {})
    
    total = 0
    
    # Calcular valor dos pratos (buscar em todas as categorias)
    for prato, quantidade in pratos.items():
        preco = get_preco_prato(prato)
        if preco > 0:
            total += preco * int(quantidade)
    
    # Calcular valor das bebidas
    for bebida, quantidade in bebidas.items():
        if bebida in CARDAPIO.get('Bebidas', {}):
            total += CARDAPIO['Bebidas'][bebida] * int(quantidade)
    
    return jsonify({'total': round(total, 2)})

@app.route('/pedidos', methods=['POST'])
def criar_pedido():
    """Cria um novo pedido"""
    try:
        # Coleta dados do formulário
        cliente_nome = request.form.get('cliente_nome')
        cliente_telefone = request.form.get('cliente_telefone')
        cliente_endereco = request.form.get('cliente_endereco')
        eh_balcao = 'eh_balcao' in request.form
        forma_pagamento = request.form.get('forma_pagamento')
        
        # Processa itens selecionados do carrinho
        itens_pedido = {}
        for key, value in request.form.items():
            if key.startswith('item_') and value:
                item_nome = key.replace('item_', '')
                quantidade = int(value)
                if quantidade > 0:
                    itens_pedido[item_nome] = quantidade
        
        # Calcula valor total
        valor_total = 0
        for item_nome, quantidade in itens_pedido.items():
            preco = get_preco_item(item_nome)
            valor_total += preco * quantidade

        # Salva ou atualiza cliente
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Verificar se cliente existe
        cliente_existente = cursor.execute('''
            SELECT id FROM clientes 
            WHERE nome = ? OR telefone = ?
        ''', (cliente_nome, cliente_telefone)).fetchone()
        
        if not cliente_existente:
            # Inserir novo cliente
            cursor.execute('''
                INSERT OR IGNORE INTO clientes (nome, telefone, endereco)
                VALUES (?, ?, ?)
            ''', (cliente_nome, cliente_telefone, cliente_endereco))
        else:
            # Atualizar dados do cliente existente
            cursor.execute('''
                UPDATE clientes 
                SET nome = ?, telefone = ?, endereco = ?
                WHERE id = ?
            ''', (cliente_nome, cliente_telefone, cliente_endereco, cliente_existente['id']))
        
        # Salva o pedido
        cursor.execute('''
            INSERT INTO pedidos 
            (cliente_nome, cliente_telefone, cliente_endereco, eh_balcao, 
             pratos, bebidas, forma_pagamento, valor_total, hora_pedido)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, datetime('now', 'localtime'))
        ''', (cliente_nome, cliente_telefone, cliente_endereco, eh_balcao,
              json.dumps(itens_pedido), '', forma_pagamento, valor_total))
        
        conn.commit()
        conn.close()
        
        flash('Pedido registrado com sucesso!', 'success')
        
    except Exception as e:
        flash(f'Erro ao registrar pedido: {str(e)}', 'error')
    
    return redirect(url_for('index'))

@app.route('/saidas', methods=['POST'])
def criar_saida():
    """Cria uma nova saída/despesa"""
    try:
        categoria = request.form.get('categoria')
        descricao = request.form.get('descricao', '')
        valor = float(request.form.get('valor'))
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO saidas (categoria, descricao, valor, hora_saida)
            VALUES (?, ?, ?, datetime('now', 'localtime'))
        ''', (categoria, descricao, valor))
        
        conn.commit()
        conn.close()
        
        flash('Saída registrada com sucesso!', 'success')
        
    except Exception as e:
        flash(f'Erro ao registrar saída: {str(e)}', 'error')
    
    return redirect(url_for('index'))

@app.route('/api/saidas')
def listar_saidas():
    """API para listar saídas"""
    conn = get_db_connection()
    saidas = conn.execute('''
        SELECT * FROM saidas 
        ORDER BY data_saida DESC, hora_saida DESC
    ''').fetchall()
    conn.close()
    
    saidas_list = []
    for saida in saidas:
        saidas_list.append({
            'id': saida['id'],
            'categoria': saida['categoria'],
            'descricao': saida['descricao'],
            'valor': saida['valor'],
            'data_saida': saida['data_saida'],
            'hora_saida': saida['hora_saida']
        })
    
    return jsonify(saidas_list)

@app.route('/saidas/<int:saida_id>', methods=['DELETE'])
def excluir_saida(saida_id):
    """Exclui uma saída"""
    try:
        conn = get_db_connection()
        conn.execute('DELETE FROM saidas WHERE id = ?', (saida_id,))
        conn.commit()
        conn.close()
        
        return jsonify({'success': True, 'message': 'Saída excluída com sucesso!'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/relatorio')
def relatorio():
    """API para gerar relatório por período"""
    data_inicio = request.args.get('data_inicio', date.today().isoformat())
    data_fim = request.args.get('data_fim', date.today().isoformat())
    
    conn = get_db_connection()
    
    # Total de entradas (pedidos)
    total_entradas = conn.execute('''
        SELECT COALESCE(SUM(valor_total), 0) as total
        FROM pedidos 
        WHERE data_pedido BETWEEN ? AND ?
    ''', (data_inicio, data_fim)).fetchone()['total']
    
    # Total de saídas
    total_saidas = conn.execute('''
        SELECT COALESCE(SUM(valor), 0) as total
        FROM saidas 
        WHERE data_saida BETWEEN ? AND ?
    ''', (data_inicio, data_fim)).fetchone()['total']
    
    # Detalhes dos pedidos
    pedidos = conn.execute('''
        SELECT * FROM pedidos 
        WHERE data_pedido BETWEEN ? AND ?
        ORDER BY data_pedido DESC, hora_pedido DESC
    ''', (data_inicio, data_fim)).fetchall()
    
    conn.close()
    
    saldo = total_entradas - total_saidas
    
    pedidos_list = []
    for pedido in pedidos:
        pedidos_list.append({
            'id': pedido['id'],
            'cliente_nome': pedido['cliente_nome'],
            'valor_total': pedido['valor_total'],
            'forma_pagamento': pedido['forma_pagamento'],
            'data_pedido': pedido['data_pedido'],
            'hora_pedido': pedido['hora_pedido']
        })
    
    return jsonify({
        'total_entradas': total_entradas,
        'total_saidas': total_saidas,
        'saldo': saldo,
        'pedidos': pedidos_list,
        'periodo': {
            'inicio': data_inicio,
            'fim': data_fim
        }
    })

if __name__ == '__main__':
    init_db()
    app.run(debug=True)