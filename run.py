#!/usr/bin/env python3
"""
Script de inicialização simplificado para o Sistema Cheff Carlos
Execute este arquivo para iniciar a aplicação
"""

import os
import sys
import subprocess

def verificar_dependencias():
    """Verifica se as dependências estão instaladas"""
    try:
        import flask
        print("✅ Flask encontrado")
        return True
    except ImportError:
        print("❌ Flask não encontrado")
        return False

def instalar_dependencias():
    """Instala as dependências automaticamente"""
    print("📦 Instalando dependências...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "flask==2.3.3"])
        print("✅ Dependências instaladas com sucesso!")
        return True
    except subprocess.CalledProcessError:
        print("❌ Erro ao instalar dependências")
        return False

def criar_estrutura():
    """Cria a estrutura de pastas necessária"""
    if not os.path.exists('templates'):
        os.makedirs('templates')
        print("✅ Pasta 'templates' criada")

def main():
    """Função principal"""
    print("🍽️  Iniciando Sistema Cheff Carlos...")
    print("=" * 50)
    
    # Verificar estrutura
    criar_estrutura()
    
    # Verificar dependências
    if not verificar_dependencias():
        resposta = input("\n🤔 Deseja instalar as dependências automaticamente? (s/n): ")
        if resposta.lower() in ['s', 'sim', 'y', 'yes']:
            if not instalar_dependencias():
                print("\n❌ Falha na instalação. Execute manualmente:")
                print("pip install flask==2.3.3")
                return
        else:
            print("\n📋 Execute manualmente:")
            print("pip install flask==2.3.3")
            return
    
    # Verificar se app.py existe
    if not os.path.exists('app.py'):
        print("\n❌ Arquivo 'app.py' não encontrado!")
        print("Certifique-se de que todos os arquivos estão na mesma pasta.")
        return
    
    # Verificar se template existe
    if not os.path.exists('templates/index.html'):
        print("\n❌ Arquivo 'templates/index.html' não encontrado!")
        print("Certifique-se de que o template está na pasta 'templates/'.")
        return
    
    print("\n🚀 Iniciando servidor...")
    print("📍 Acesse: http://localhost:5000")
    print("🛑 Para parar: Ctrl+C")
    print("=" * 50)
    
    try:
        # Importar e executar a aplicação
        from app import app, init_db
        
        # Inicializar banco de dados
        init_db()
        print("✅ Banco de dados inicializado")
        
        # Executar aplicação
        app.run(debug=True, host='0.0.0.0', port=5000)
        
    except ImportError as e:
        print(f"\n❌ Erro ao importar app.py: {e}")
        print("Verifique se o arquivo app.py está correto.")
    except KeyboardInterrupt:
        print("\n\n👋 Sistema encerrado pelo usuário")
    except Exception as e:
        print(f"\n❌ Erro inesperado: {e}")

if __name__ == "__main__":
    main()