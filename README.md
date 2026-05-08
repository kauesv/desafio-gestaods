# API de Locação de Carros - Desafio Técnico GestãoDS

Proposta técnica da empresa [GestãoDS](https://www.gestaods.com.br/) para a vaga **Desenvolvedor Python Pleno/Sênior**.

Este projeto implementa uma API com Django REST Framework para gestão de locações de carros, incluindo módulo de gamificação com pontuação automática, histórico de pontos e resgate de prêmios.

## Objetivo do Desafio

Implementar e evoluir um backend com foco em:
- Qualidade de código e organização por domínio.
- Boas práticas em Django/DRF.
- Regras de negócio de locação e recompensas.
- Cobertura de testes e documentação técnica.

## Stack

- Python 3.11
- Django 4.2.7
- Django REST Framework 3.14
- SQLite (ambiente local)
- drf-yasg (Swagger/Redoc)
- django-filter
- django-autocomplete-light
- APScheduler + django-apscheduler

## Estrutura do Projeto

```text
car_rental/         # Configurações do projeto Django
core/               # Entidades base (país/estado/cidade) + autocomplete
users/              # Modelo de usuário customizado
rentals/            # Regras e endpoints de locação
gamifications/      # Pontuação, níveis, histórico e resgate de prêmios
fixtures/           # Scripts e dados iniciais
manage.py
```

## Como Executar Localmente

### 1) Pré-requisitos

- Python 3.11+
- pip

### 2) Variáveis de ambiente

Crie um arquivo `.env` na raiz do projeto com as seguintes chaves:

```env
SECRET_KEY=sua_chave_secreta
DEBUG=True
DJANGO_SETTINGS_MODULE=car_rental.settings
TIME_ZONE=UTC
```

Observações:
- `SECRET_KEY`: chave do Django (obrigatória).
- `DEBUG`: use `True` para desenvolvimento local.
- `DJANGO_SETTINGS_MODULE`: módulo de settings do projeto.
- `TIME_ZONE`: opcional (se não definir, o projeto pode usar UTC conforme configuração).

### 3) Configuração rápida

No Windows:

```bash
setup.cmd
```

No Linux/macOS:

```bash
./setup.sh
```

### 4) Execução manual (alternativa)

```bash
python -m venv venv
venv\Scripts\activate  # Windows
pip install -r requirements.txt
python manage.py makemigrations
python manage.py migrate
python manage.py shell -c "exec(open('fixtures/init_data.py', encoding='utf-8').read())"
python manage.py shell -c "exec(open('fixtures/core/init_data.py', encoding='utf-8').read())"
python manage.py createsuperuser
```

Depois inicie o servidor e o scheduler(cron)
```bash
python manage.py runserver
python manage.py runapscheduler
```

API em: `http://localhost:8000/v1/`

## Execução com Docker

```bash
docker-compose up --build
```

Comandos úteis:

```bash
docker-compose logs -f
docker-compose exec web python manage.py test
docker-compose down
```

## Endpoints Principais

Base URL: `http://localhost:8000/v1/`

### Documentação
- `GET /v1/swagger/`
- `GET /v1/redoc/`
- `GET /v1/swagger.json` e `GET /v1/swagger.yaml`

### Rentals (`/v1/rentals/`)
- `GET /v1/rentals/`
- `GET /v1/rentals/cars`
- `GET /v1/rentals/cars/{car_id}`
- `GET /v1/rentals/list`
- `POST /v1/rentals/create`
- `POST /v1/rentals/{rental_id}/return`
- `GET /v1/rentals/customer/{customer_email}`
- `GET /v1/rentals/stats`

### Gamifications (`/v1/gamifications/`)
- `GET /v1/gamifications/user-points/{user_id}/`
- `GET /v1/gamifications/user-points/history/`
- `GET /v1/gamifications/user-points/{user_id}/history`
- `POST /v1/gamifications/awards/{award_id}/redeem/`

### Core (`/v1/core/`)
- `GET /v1/core/states/`
- `GET /v1/core/states/{id}/`
- `GET /v1/core/cities/`
- `GET /v1/core/cities/{id}/`

Autocomplete:
- `GET /estados-autocomplete/?q={texto}`
- `GET /municipios-autocomplete/?state={id}&q={texto}`

## Regras de Recompensa (Resumo)

A pontuação é processada no fluxo de devolução da locação e considera:
- Pontos base por dia.
- Bônus por categoria/valor do carro.
- Bônus por duração da locação.
- Bônus por devolução pontual.
- Nível do usuário (Bronze/Prata/Ouro) e histórico de movimentações.

## Testes

```bash
python manage.py test rentals
python manage.py test core
python manage.py test gamifications
python manage.py test users
python manage.py test
pytest
```

## Admin e Operação

- Admin Django: `http://localhost:8000/admin/`
- Scheduler (tarefas recorrentes):

```bash
python manage.py runapscheduler
```

## Documentos de Apoio

- `docs/INSTRUCOES_CANDIDATO.md`
- `docs/FEATURE.md`
- `docs/IMPLEMENTACAO.md`
- `docs/PROJECT_OFFICIAL_DOC.md`
- `docs/DOCKER.md`

## Contato

Para mais informações ou para discutir qualquer um dos repositórios, sinta-se à vontade para entrar em contato:

- **Email:** [kauesousavieira534@gmail.com](mailto:kauesousavieira534@gmail.com)
- **LinkedIn:** [LinkedIn](https://www.linkedin.com/in/kaue-sousa-vieira/)

---
Obrigado por visitar meu repositório!
