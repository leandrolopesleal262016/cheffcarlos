# Sistema de Gestão Chef Carlos

Sistema completo de gestão para restaurante desenvolvido em Flask, especializado em controle de pedidos, cardápio e fluxo de caixa.

## 🍽️ Funcionalidades

### Gestão de Pedidos
- Registro de pedidos para balcão e delivery
- Cadastro automático de clientes
- Busca inteligente de clientes por nome ou telefone
- Cálculo automático de totais
- Múltiplas formas de pagamento

### Gestão de Cardápio
- Cardápio organizado por categorias:
    - **Pratos**: Parmegianas, massas, combos e pratos especiais
    - **Complementos**: Acompanhamentos e adicionais
    - **Bebidas**: Refrigerantes, cervejas e águas
    - **Sobremesas**: Geladinhos gourmet
- CRUD completo de itens do cardápio
- Controle de preços em tempo real

### Controle Financeiro
- Registro de saídas/despesas por categoria
- Relatórios financeiros por período
- Cálculo automático de saldo (entradas - saídas)
- Categorias de despesas: Mercado, Funcionário, Açougue, Contas, etc.

### Relatórios
- Relatório de vendas por período
- Controle de fluxo de caixa
- Histórico de pedidos
- Análise de entradas e saídas

## 🚀 Tecnologias Utilizadas

- **Backend**: Python Flask
- **Banco de Dados**: SQLite
- **Frontend**: HTML5, CSS3, JavaScript
- **Estilização**: Bootstrap (responsivo)
- **Persistência**: SQLite com migrations automáticas

## 📋 Pré-requisitos

```bash
python >= 3.7
flask >= 2.0
```

## 🔧 Instalação

1. Clone o repositório:
```bash
git clone <url-do-repositorio>
cd chef-carlos-sistema
```

2. Instale as dependências:
```bash
pip install flask
```

3. Execute a aplicação:
```bash
python app.py
```

4. Acesse no navegador:
```
http://localhost:5000
```

## 📊 Estrutura do Banco de Dados

### Tabelas Principais

#### `clientes`
- `id`: Chave primária
- `nome`: Nome do cliente
- `telefone`: Telefone para contato
- `endereco`: Endereço para delivery
- `data_cadastro`: Data de cadastro

#### `cardapio_itens`
- `id`: Chave primária
- `nome`: Nome do item
- `categoria`: Categoria (Pratos, Bebidas, etc.)
- `preco`: Preço do item
- `ativo`: Status do item
- `data_criacao/atualizacao`: Timestamps

#### `pedidos`
- `id`: Chave primária
- `cliente_*`: Dados do cliente
- `eh_balcao`: Tipo de pedido (balcão/delivery)
- `pratos`: JSON com itens e quantidades
- `forma_pagamento`: Método de pagamento
- `valor_total`: Total do pedido
- `data_pedido/hora_pedido`: Timestamps

#### `saidas`
- `id`: Chave primária
- `categoria`: Categoria da despesa
- `descricao`: Descrição da saída
- `valor`: Valor da despesa
- `data_saida/hora_saida`: Timestamps

## 🎯 Funcionalidades Detalhadas

### Sistema de Pedidos
- Interface intuitiva com abas organizadas
- Busca automática de clientes cadastrados
- Carrinho de compras com cálculo em tempo real
- Suporte a pedidos balcão e delivery
- Formas de pagamento: PIX, Dinheiro, Cartões, Tickets alimentação

### Cardápio Especializado
- **La Parmegiana**: Completas para 1, 2 e 3 pessoas
- **Combos Especiais**: Macarrão & Parmegiana
- **Massas Artesanais**: Talharim com diversos molhos
- **Pratos do Dia**: Opções econômicas
- **Parmegianas Especiais**: Para grupos de até 5 pessoas

### Controle de Estoque e Despesas
- Categorização detalhada de gastos
- Controle de fornecedores
- Gestão de contas fixas (luz, água, aluguel)
- Relatórios de lucratividade

## 🔄 APIs Disponíveis

### Clientes
- `GET /api/buscar_cliente?termo=<nome_ou_telefone>`
- `GET /api/clientes?termo=<filtro>`

### Cardápio
- `GET /api/cardapio` - Lista todos os itens
- `POST /api/cardapio` - Cria novo item
- `PUT /api/cardapio/<id>` - Atualiza item
- `DELETE /api/cardapio/<id>` - Remove item
- `GET /api/cardapio/categorias` - Lista categorias

### Financeiro
- `GET /api/saidas` - Lista todas as saídas
- `DELETE /saidas/<id>` - Remove saída
- `GET /api/relatorio?data_inicio=<>&data_fim=<>` - Relatório por período

### Pedidos
- `POST /pedidos` - Cria novo pedido
- `POST /saidas` - Registra nova despesa
- `POST /api/calcular_total` - Calcula total do carrinho

## 🎨 Interface do Usuário

- Design responsivo para desktop e mobile
- Navegação por abas: Pedidos, Cardápio, Saídas, Relatórios
- Feedback visual com mensagens de sucesso/erro
- Autocompletar para busca de clientes
- Calculadora automática de totais

## 🔐 Configurações

### Chave Secreta
```python
app.secret_key = 'cheff_carlos_secret_key_2024'
```

### Banco de Dados
```python
DATABASE = 'pedidos.db'
```

## 📈 Relatórios Disponíveis

1. **Relatório Diário**: Vendas e despesas do dia
2. **Relatório por Período**: Análise customizada
3. **Fluxo de Caixa**: Entradas vs Saídas
4. **Histórico de Pedidos**: Detalhamento completo

## 🛠️ Manutenção

### Backup do Banco
```bash
cp pedidos.db pedidos_backup_$(date +%Y%m%d).db
```

### Logs de Erro
O sistema utiliza o sistema de flash messages do Flask para feedback ao usuário.

## 📞 Suporte

Sistema desenvolvido especificamente para o Chef Carlos, com foco em:
- Gestão eficiente de pedidos
- Controle financeiro detalhado
- Interface amigável para operação diária
- Relatórios gerenciais precisos

## 🔄 Atualizações Futuras

- [ ] Sistema de delivery integrado
- [ ] Relatórios em PDF
- [ ] Dashboard com gráficos
- [ ] Integração com WhatsApp
- [ ] Sistema de fidelidade
- [ ] Controle de estoque avançado

---

**Versão**: 2.0  
**Última Atualização**: 2024  
**Desenvolvido para**: Chef Carlos Restaurant System