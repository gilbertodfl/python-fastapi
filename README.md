### COMO INSTALAR

```python
git clone ...
python3 -m venv .venv 
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

COMO CHAMAR NO COMANDO DE LINHA

```plaintext
uvicorn main:app --reload
```

Onde:

*   `**main**` → nome do arquivo Python (ex: `main.py`)
*   `**app**` → nome da instância FastAPI dentro do arquivo (`app = FastAPI()`)
*   `**--reload**` → reinicia automaticamente ao salvar (usar só em desenvolvimento)

\# Porta personalizada  
uvicorn main:app --reload --port 8080

\# Host acessível na rede local  
uvicorn main:app --reload --host 0.0.0.0 --port 8000

\# Sem reload (produção)

A url padrão para este projeto: 

[http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

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

[http://127.0.0.1:8000/docs#/auth/login\_auth\_login\_post](http://127.0.0.1:8000/docs#/auth/login_auth_login_post)

{  
"email": "gilberto@gmail.com",  
"senha": "123456",  
}

### COMO ALTERAR TABELAS

A forma no FASTAPI é diferente: 

```plaintext
alembic revision --autogenerate -m 'adicionar items ao pedido'
alembic upgrade head
```