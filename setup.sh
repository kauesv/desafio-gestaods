#!/bin/bash
# Quick start script for the Car Rental API - Linux/macOS version

echo "========================================"
echo "   Car Rental API - Setup Script"
echo "========================================"
echo ""

if [ ! -d "venv" ]; then
    echo "[OK] Criando ambiente virtual..."
    python3 -m venv venv
    if [ $? -ne 0 ]; then
        echo "[ERRO] Erro ao criar ambiente virtual. Verifique se Python esta instalado."
        exit 1
    fi
fi

echo "[OK] Ativando ambiente virtual..."
source venv/bin/activate
if [ $? -ne 0 ]; then
    echo "[ERRO] Erro ao ativar ambiente virtual."
    exit 1
fi

echo "[OK] Atualizando PIP..."
python -m pip install --upgrade pip
if [ $? -ne 0 ]; then
    echo "[ERRO] Erro ao atualizar o pip."
    exit 1
fi

echo "[OK] Instalando dependencias..."
pip install -r requirements.txt
if [ $? -ne 0 ]; then
    echo "[ERRO] Erro ao instalar dependencias."
    exit 1
fi

echo "[OK] Executando makemigrations..."
python manage.py makemigrations
if [ $? -ne 0 ]; then
    echo "[ERRO] Erro ao executar migrations."
    exit 1
fi

echo "[OK] Executando migrations..."
python manage.py migrate
if [ $? -ne 0 ]; then
    echo "[ERRO] Erro ao executar migrations."
    exit 1
fi

echo "[OK] Carregando dados de Carros..."
python manage.py shell < fixtures/init_data.py
if [ $? -ne 0 ]; then
    echo "[ERRO] Erro ao carregar dados de Carros."
    exit 1
fi

echo "[OK] Carregando dados de Cidades, Estados e Pais..."
python manage.py shell -c "exec(open('fixtures/core/init_data.py', encoding='utf-8').read())"
if [ $? -ne 0 ]; then
    echo "[ERRO] Erro ao carregar dados de Cidades, Estados e Pais."
    exit 1
fi

echo "[OK] Criando superuser..."
python manage.py createsuperuser
if [ $? -ne 0 ]; then
    echo "[ERRO] Erro ao criar superuser."
    exit 1
fi

echo ""
echo "[OK] Setup completo!"
echo ""
echo "Para iniciar o servidor, execute:"
echo "  python manage.py runserver"
echo ""
echo "Para iniciar o cronjobs, execute:"
echo "  python manage.py runapscheduler"
echo ""
echo "Para executar testes:"
echo "  python manage.py test rentals"
echo "  # ou"
echo "  pytest"
echo ""
echo "Ver documentacoes das APIs:"
echo "   http://localhost:8000/v1/redoc/"
echo "   http://localhost:8000/v1/swagger/"
echo ""
echo "Admin panel em: http://localhost:8000/admin/"
echo ""