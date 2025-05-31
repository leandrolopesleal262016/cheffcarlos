# 🍽️ Cheff Carlos - Sistema de Gerenciamento de Pedidos

Sistema completo de gerenciamento de pedidos e vendas para restaurantes, desenvolvido em Python Flask com interface moderna e responsiva.

## ✨ Funcionalidades

### 📋 Gestão de Pedidos (Entradas)
- ✅ Cadastro completo de clientes (nome, telefone, endereço)
- ✅ Opção "Balcão" que desabilita o campo endereço
- ✅ Cardápio digital com pratos e bebidas
- ✅ Cálculo automático do valor total
- ✅ Múltiplas formas de pagamento
- ✅ Controle de quantidades por item

### 💰 Controle de Saídas (Despesas)
- ✅ Categorização de gastos (Mercado, Funcionário, Açougue, etc.)
- ✅ Descrição opcional para cada saída
- ✅ Listagem em tempo real das despesas
- ✅ Exclusão de saídas com confirmação
- ✅ Cálculo automático do total de saídas

### 📊 Relatórios Avançados
- ✅ Filtro por período (data início e fim)
- ✅ Total de entradas vs saídas
- ✅ Cálculo automático do saldo
- ✅ Listagem detalhada de pedidos por período
- ✅ Visualização em cards com estatísticas

### 🎨 Interface Moderna
- ✅ Design responsivo com Bootstrap 5
- ✅ Cores personalizadas inspiradas em restaurante
- ✅ Ícones Font Awesome
- ✅ Navegação por abas intuitiva
- ✅ Alertas de sucesso/erro em tempo real
- ✅ Animações suaves e efeitos visuais

## 🚀 Instalação e Configuração

### Pré-requisitos
- Python 3.7 ou superior
- pip (gerenciador de pacotes Python)

### Passo a Passo

1. **Clone ou baixe o projeto**
```bash
# Se usando git
git clone <url-do-repositorio>
cd cheff-carlos

# Ou extraia os arquivos baixados
```

2. **Crie um ambiente virtual (recomendado)**
```bash
python -m venv venv

# No Windows
venv\Scripts\activate

# No Linux/Mac
source venv/bin/activate
```

3. **Instale as dependências**
```bash
pip install -r requirements.txt
```

4. **Estrutura de pastas necessária**
```
cheff-carlos/
├── app.py
├── requirements.txt
├── README.md
├── pedidos.db (será criado automaticamente)
└── templates/
    └── index.html
```

5. **Execute a aplicação**
```bash
python app.py
```

6. **Acesse no navegador**
```
http://localhost:5000
```

## 📁 Estrutura do Projeto

```
cheff-carlos/
├── app.py                 # Aplicação principal Flask
├── requirements.txt       # Dependências Python
├── README.md             # Este arquivo
├── pedidos.db            # Banco SQLite (criado automaticamente)
└── templates/
    └── index.html        # Template principal da interface
```

## 🗄️ Banco de Dados

O sistema utiliza **SQLite** com duas tabelas principais:

### Tabela `pedidos`
- `id` - Chave primária
- `cliente_nome` - Nome do cliente
- `cliente_telefone` - Telefone do cliente
- `cliente_endereco` - Endereço de entrega
- `eh_balcao` - Indica se é pedido no balcão
- `pratos` - JSON com pratos e quantidades
- `bebidas` - JSON com bebidas e quantidades
- `forma_pagamento` - Método de pagamento
- `valor_total` - Valor total do pedido
- `data_pedido` - Data do pedido
- `hora_pedido` - Hora do pedido

### Tabela `saidas`
- `id` - Chave primária
- `categoria` - Categoria da despesa
- `descricao` - Descrição opcional
- `valor` - Valor da saída
- `data_saida` - Data da saída
- `hora_saida` - Hora da saída

## 📋 Cardápio Configurável

O cardápio está definido no arquivo `app.py` na variável `CARDAPIO`:

```python
CARDAPIO = {
    'Pratos': {
        'Feijoada Completa': 28.50,
        'Picanha Grelhada': 45.00,
        # ... adicione mais pratos
    },
    'Bebidas': {
        'Coca Cola Lata': 4.50,
        'Cerveja Skol': 5.50,
        # ... adicione mais bebidas
    }
}
```

## 💳 Formas de Pagamento

Suporte completo para:
- PIX
- Dinheiro
- Cartão Débito
- Cartão Crédito
- Ticket
- Alelo
- Pluxee
- Vero Card
- VR
- Conta
- Permuta
- Cortesia

## 📊 Categorias de Saídas

- Mercado
- Funcionário
- Açougue
- Verduras/Legumes
- Bebidas/Fornecedor
- Manutenção
- Limpeza
- Combustível
- Conta de Luz
- Conta de Água
- Internet
- Aluguel
- Outros

## 🔧 Personalização

### Alterando o Cardápio
Edite a variável `CARDAPIO` no arquivo `app.py` para adicionar, remover ou alterar preços.

### Modificando Categorias
Edite a lista `CATEGORIAS_SAIDA` no arquivo `app.py`.

### Customizando Cores
Altere as variáveis CSS no `<style>` do arquivo `index.html`:
```css
:root {
    --primary-color: #d4a574;    /* Cor principal */
    --secondary-color: #8b4513;  /* Cor secundária */
    --accent-color: #f4f4f4;     /* Cor de destaque */
}
```

## 🔒 Segurança

- Validação de dados no frontend e backend
- Proteção contra SQL injection usando parâmetros
- Validação de tipos de dados
- Confirmações para exclusões

## 📱 Responsividade

A interface se adapta automaticamente a:
- Computadores/Laptops
- Tablets
- Smartphones

## 🆘 Solução de Problemas

### Erro: "No module named 'flask'"
```bash
pip install flask
```

### Banco não é criado
Verifique se você tem permissões de escrita na pasta do projeto.

### Interface não carrega corretamente
Verifique se os arquivos CSS/JS externos estão acessíveis (requer internet).

### Erro de porta em uso
Altere a porta no final do `app.py`:
```python
app.run(debug=True, port=5001)  # Use outra porta
```

## 📈 Próximas Melhorias

- [ ] Exportação de relatórios em PDF/Excel
- [ ] Sistema de usuários e autenticação
- [ ] Backup automático do banco
- [ ] Integração com impressora
- [ ] Notificações push
- [ ] Dashboard com gráficos

## 📞 Suporte

Para dúvidas ou problemas:
1. Verifique se seguiu todos os passos de instalação
2. Confira se todas as dependências foram instaladas
3. Verifique os logs no terminal onde rodou `python app.py`

## 📄 Licença

Este projeto foi desenvolvido para uso educacional e comercial do restaurante Cheff Carlos.

---

**Desenvolvido com ❤️ para o Cheff Carlos**