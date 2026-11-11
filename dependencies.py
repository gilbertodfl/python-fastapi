from fastapi import Depends, HTTPException
from main import SECRET_KEY, ALGORITHM, oauth2_schema
from models import db
from sqlalchemy.orm import sessionmaker, Session
from models import Usuario
from jose import jwt, JWTError

def pegar_sessao():
    try:
        Session = sessionmaker(bind=db)
        session = Session()
        yield session
    finally:
        session.close()



###Como funciona o Depends no FastAPI
###O Depends é o sistema de injeção de dependências do FastAPI.
#  A ideia: em vez de você mesmo chamar uma função dentro da rota, você declara que a rota precisa do
# resultado dessa função, e o FastAPI se encarrega de executá-la antes e entregar o resultado pronto.

def verificar_token(token: str = Depends(oauth2_schema), session: Session = Depends(pegar_sessao)):
    try:
        dic_info = jwt.decode(token, SECRET_KEY, ALGORITHM)
        id_usuario = int(dic_info.get("sub"))
    except JWTError as erro:
        print(erro)
        raise HTTPException(status_code=401, detail="Acesso Negado, verifique a validade do token")
    # verificar se o token é válido
    # extrair o ID do usuário do token
    usuario = session.query(Usuario).filter(Usuario.id==id_usuario).first()
    if not usuario:
        raise HTTPException(status_code=401, detail="Acesso Inválido")
    return usuario