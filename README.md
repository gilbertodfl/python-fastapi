### OBJETIVO: Usar as funções mais importantes fastAPI

Aqui não é objetivo fazer um backend com todos os detalhes, mas estabelecer uma documentação mínima e de boas práticas ao usar o fastAPI.

Vamos abordar: 

*   Swagger UI.
*   Token / JWT / Autenicação
*   Rotas
*   schemas
*   Banco de dados: sqlite

Nosso projeto visa cadastra o usuário, cadastrar pedido e cadastrar itens do pedido. 

No caso dos pedidos, teremos os devidos CRUDs em backend: incluir, consultar, apagar…

### COMO INSTALAR

```python
git clone https://github.com/gilbertodfl/python-fastapi.git
python3 -m venv .venv 
source .venv/bin/activate
pip install --upgrade pip

## instala o que está no requirements.txt
pip install -r requirements.txt


```

### COMO CHAMAR NO COMANDO DE LINHA

```plaintext
uvicorn main:app --reload

No browser digite: http://127.0.0.1:8000/docs
```

Onde:

*   `**main**` → nome do arquivo Python (ex: `main.py`)
*   `**app**` → nome da instância FastAPI dentro do arquivo (`app = FastAPI()`)
*   `**--reload**` → reinicia automaticamente ao salvar (usar só em desenvolvimento)

\# Porta personalizada: caso queira trocar de porta  
uvicorn main:app --reload --port 8080

\# Host acessível na rede local  
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Sem reload (produção)

    uvicorn main:app --host 0.0.0.0 --port 8000
    ou porta personalizada
    uvicorn main:app --host 0.0.0.0 --port 8080
    ou 4 núcleos
    uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4



A url padrão para este projeto: 

[http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

### Exemplo docker
```bash
FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]
```

### PROCESO PARA TESTAR O TOKEN: 

PASSO 01: cria uma conta : [http://127.0.0.1:8000/docs#/auth/criar\_conta\_auth\_criar\_conta\_post](http://127.0.0.1:8000/docs#/auth/criar_conta_auth_criar_conta_post)

{  
 "nome": "gilberto",  
 "email": "gilberto@gmail.com",  
 "senha": "123456",  
 "ativo": true,  
 "admin": true  
}

PASSO 02: Faça o login
    DICA :ambulance:  Se necessári abra o banco.db para pegar o usuário se não se lembrar. 

[http://127.0.0.1:8000/docs#/auth/login\_auth\_login\_post](http://127.0.0.1:8000/docs#/auth/login_auth_login_post)
Após abrir o link, preencha no body as informações semelhante abaixo: 
{  
"email": "gilberto@gmail.com",  
"senha": "123456",  
}

OUTRA MANEIRA DE LOGIN: Seria clicar no botão no topo à direita chamado AUTHORIZE e passar as mesmas credenciais. 

OBSERVAÇÃO: No arquivo .env definimos o refresh com no máximo de 30 minutos: ACCESS\_TOKEN\_EXPIRE\_MINUTES=30

### COMO ALTERAR TABELAS

A forma no FASTAPI é diferente: 

```plaintext
alembic revision --autogenerate -m 'adicionar items ao pedido'
alembic upgrade head
```
## alembic
O Alembic é uma ferramenta leve de migração de banco de dados em Python, criada pelos mesmos desenvolvedores

https://medium.com/@evembijo/beginners-guide-to-alembic-and-sqlalchemy-in-python-manage-your-database-like-a-pro-9395b5b5080d

https://alembic.sqlalchemy.org/en/latest/

    Não esqueça de configurar no alembic.ini o acesso ao database: ( linha 66 mais ou menos )

    sqlalchemy.url = sqlite:///banco.db

#### criando o ambiente alembic
    alembic init alembic
    alembic revision --autogenerate -m "create my db"    

    aplicando atualização: alembic upgrade head

### principais comandos alembic:

    alembic init alembic — Initialize Alembic in your project
    alembic revision --autogenerate -m "message" — Generate migration script automatically
    alembic upgrade head — Apply latest migrations
    alembic downgrade -1 — Undo the last migration (go back one version)
    alembic history — See migration history


#JWT

https://www.jwt.io/


Veja também:

O site oficial é [**https://fastapi.tiangolo.com**](https://fastapi.tiangolo.com)

*   [**https://docs.pydantic.dev**](https://docs.pydantic.dev) — essencial, pois o FastAPI usa Pydantic para validação de dados
*   [**https://www.sqlalchemy.org**](https://www.sqlalchemy.org) — se estiver usando SQLAlchemy com o Alembic
*   [**https://alembic.sqlalchemy.org**](https://alembic.sqlalchemy.org) — docs oficiais do Alembic
*   [**https://www.uvicorn.org**](https://www.uvicorn.org) — servidor ASGI usado pelo FastAPI

**Vídeos (YouTube)**

*   **ArjanCodes** — conteúdo em inglês, muito bem explicado, foca em boas práticas
*   **Patrick Loeber** — tutoriais diretos ao ponto sobre FastAPI
*   **Eric Roby (Codingwithroby)** — tem uma série completa de FastAPI com banco de dados
*   **Pycodebr / Pythonando** — boas opções em **português**