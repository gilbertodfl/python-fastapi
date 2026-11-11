from fastapi import FastAPI
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordBearer
from dotenv import load_dotenv
import os

## Carregando as variáveis de ambiente do arquivo .env
load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES"))
##########################################################

## 
app = FastAPI()

## A biblioteca passlib é usada para criptografar a senha do usuário que vamos salvar no banco de dados.
#  A função CryptContext é usada para criar um contexto de criptografia, que é usado para gerar e verificar senhas criptografadas.
bcrypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

## Aqui estamos definindo o esquema de autenticação OAuth2 com senha e token JWT
## aqui abre um formmulário de login para o usuário digitar email e senha, e depois gerar o token JWT
## é chamado no arquivo dependencies.py na função verificar_token, que é usada para proteger as rotas que precisam de autenticação
oauth2_schema = OAuth2PasswordBearer(tokenUrl="auth/login-form")

from auth_routes import auth_router
from order_routes import order_router

## estamos incluindo os routers das rotas de autenticação e de pedidos na aplicação FastAPI
app.include_router(auth_router)
app.include_router(order_router)

# MODO DE USO NO COMANDO DE LINHA:  para rodar o nosso código, executar no terminal: uvicorn main:app --reload
