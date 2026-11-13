
# Autenticação JWT

Esta API usa **JWT (JSON Web Token)** no esquema `Bearer` para identificar o usuário em rotas protegidas. O token é assinado com as variáveis `SECRET_KEY` e `ALGORITHM`, definidas no ambiente, e contém o identificador do usuário no campo `sub`.

## Visão geral

Há dois tokens emitidos no login JSON (`POST /auth/login`):

| Token | Duração atual | Finalidade |
| --- | --- | --- |
| `access_token` | `ACCESS_TOKEN_EXPIRE_MINUTES` | Acessar rotas protegidas, como `/pedidos/*`. |
| `refresh_token` | 7 dias | Solicitar um novo `access_token` em `/auth/refresh`. |

## veja o arquivo env

  💣 Por tratar de um exemplo, não vi problema de colocar a chave, mas não faça isto em produção!
```plaintext
SECRET_KEY=0yQIfXdr3KpUXBIPLT1LWflqLLDFXrPs
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```
## Vantagem do token depois de autenticado. 
O cliente envia o token no cabeçalho HTTP abaixo

```http
Authorization: Bearer <token>
```
Não envie a senha novamente para cada requisição
Veja o exemplo chamado de teste.py
```python
import requests

headers = {
    "Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwiZXhwIjoxNzcyNDkxMTMzfQ.nJHKmiGe33nv4qrjtx6ApETTS-o3c5NQZjYBE1AkRJA"
}

requisicao = requests.get("http://127.0.0.1:8000/auth/refresh", headers=headers)
print('Response da requisicao',requisicao)
print('codigo da requisicao:', requisicao.status_code)

print('requisicao.json():', requisicao.json())
print('requisicao.headers:', requisicao.headers)
print('requisicao.text:', requisicao.text)
print('pegando o token do json da requisicao:', requisicao.json()['access_token']   )
```

## Fluxo completo

```mermaid
sequenceDiagram
    participant C as Cliente
    participant A as API FastAPI
    participant B as Banco de dados

    C->>A: POST /auth/login (email e senha)
    A->>B: Busca usuário por e-mail
    B-->>A: Usuário e hash da senha
    A->>A: bcrypt verifica a senha
    A->>A: Cria JWT de acesso e JWT de renovação
    A-->>C: access_token + refresh_token

    C->>A: Rota protegida + Authorization: Bearer access_token
    A->>A: Decodifica JWT e obtém sub (id do usuário)
    A->>B: Busca o usuário pelo id
    B-->>A: Usuário válido
    A-->>C: Resposta da rota

    Note over C,A: Quando o access token expirar
    C->>A: GET /auth/refresh + Authorization: Bearer refresh_token
    A->>A: Valida JWT e identifica o usuário
    A->>B: Confirma que o usuário existe
    A->>A: Cria novo access_token
    A-->>C: Novo access_token
```

## Configuração 
### SECRET_KEY ALGORITHM ACCESS_TOKEN_EXPIRE_MINUTES:

Crie um arquivo `.env` na raiz do projeto com valores seguros:

```env
SECRET_KEY=uma-chave-longa-aleatoria-e-secreta
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

O `main.py` carrega esses valores de .env e configura o `OAuth2PasswordBearer` com `tokenUrl="auth/login-form"` (form de login). Essa configuração também é usada pelo Swagger/OpenAPI para indicar onde obter credenciais no fluxo de formulário.


## Endpoints de autenticação 

### Criar conta — `POST /auth/criar_conta`
Recebe um `UsuarioSchema`, verifica se o e-mail já existe e armazena a senha usando hash bcrypt. A senha original não é salva no banco.

```json
{
  "nome": "Ana Silva",
  "email": "ana@example.com",
  "senha": "uma-senha-forte",
  "ativo": true,
  "admin": false
}
```

### Login JSON — `POST /auth/login`

Recebe e-mail e senha em JSON. Em caso de sucesso, devolve os dois tokens:

```json
{
  "email": "ana@example.com",
  "senha": "uma-senha-forte"
}
```

```json
{
  "access_token": "<jwt-de-acesso>",
  "refresh_token": "<jwt-de-renovacao>",
  "token_type": "Bearer"
}
```

### Login por formulário OAuth2 — `POST /auth/login-form`

Este endpoint recebe `application/x-www-form-urlencoded`; por compatibilidade com `OAuth2PasswordRequestForm`, o e-mail deve ser enviado no campo `username`.

```bash
curl -X POST http://127.0.0.1:8000/auth/login-form \
  -H 'Content-Type: application/x-www-form-urlencoded' \
  -d 'username=ana@example.com&password=uma-senha-forte'
```

No código atual, esse endpoint **cria** um refresh token, mas devolve apenas `access_token` e `token_type`. Portanto, use `POST /auth/login` quando precisar da renovação de token.

### Renovar acesso — `GET /auth/refresh`

Envie o `refresh_token` no cabeçalho `Authorization`. Se ele ainda for válido e o usuário existir, a API retorna um novo access token:

```bash
curl http://127.0.0.1:8000/auth/refresh \
  -H 'Authorization: Bearer <refresh_token>'
```

```json
{
  "access_token": "<novo-jwt-de-acesso>",
  "token_type": "Bearer"
}
```

O refresh token não é renovado nem devolvido novamente por esse endpoint; ele continua válido somente até sua expiração original de 7 dias. Quando expirar, o cliente deve fazer login outra vez.
 auth_routes.py:
  >refresh_token = criar_token(usuario.id, duracao_token=timedelta(days=7))

## Como uma rota protegida é executada

O router `/pedidos` declara `dependencies=[Depends(verificar_token)]`, por isso todas as suas rotas exigem autenticação. Algumas rotas também recebem `usuario: Usuario = Depends(verificar_token)` para usar os dados do usuário autenticado na regra de autorização.

```text
Requisição com Authorization: Bearer <jwt>
                |
                v
oauth2_schema extrai somente o token do cabeçalho
                |
                v
pegar_sessao abre uma sessão SQLAlchemy
                |
                v
verificar_token decodifica o JWT e lê o campo sub
                |
                v
Consulta Usuario.id == sub no banco
                |
        +-------+--------+
        |                |
        v                v
   usuário existe     token inválido/expirado
   rota é executada   ou usuário ausente
                         |
                         v
                    resposta 401
```

Em detalhes:

1. `OAuth2PasswordBearer` extrai o valor após `Bearer` no cabeçalho. Sem o cabeçalho, o FastAPI encerra a requisição com `401` antes de chamar a rota.
2. `pegar_sessao` cria a sessão antes da rota e a fecha no `finally` após a resposta, inclusive em caso de erro.
3. `verificar_token` chama `jwt.decode(...)`. A assinatura e a data `exp` são verificadas; depois, o `sub` é convertido para inteiro e usado para buscar o usuário.
4. Se a validação funcionar, a dependência retorna o objeto `Usuario`. Caso contrário, lança `HTTPException(401)` e a rota não é executada.

O FastAPI reutiliza o resultado de uma dependência dentro da mesma requisição. Assim, quando `verificar_token` e a rota pedem `pegar_sessao`, a sessão é criada uma única vez para aquela requisição.

## Conteúdo do JWT

Tokens criados por `criar_token` têm, conceitualmente, este payload:

```json
{
  "sub": "1",
  "exp": "data/hora UTC de expiração"
}
```

- `sub`: ID do usuário serializado como texto.
- `exp`: instante de expiração em UTC.

O token é **assinado**, não criptografado. Não coloque senha, dados pessoais ou informações confidenciais no payload: quem possuir o token pode decodificar seu conteúdo.

## Respostas de erro esperadas

| Situação | Resultado atual |
| --- | --- |
| Cabeçalho `Authorization` ausente em rota protegida | `401` gerado pelo `OAuth2PasswordBearer`. |
| Token expirado, malformado ou assinado com chave diferente | `401` com `Acesso Negado, verifique a validade do token`. |
| `sub` não corresponde a um usuário no banco | `401` com `Acesso Inválido`. |
| Token assinado com `sub` ausente ou não numérico | Não é tratado hoje; a conversão para `int` pode resultar em `500`. |
| E-mail inexistente ou senha incorreta no login | `400` com `Usuário não encontrado ou credenciais inválidas`. |

## Limitações atuais e próximos aprimoramentos

O fluxo funciona para fins de estudo, mas há pontos importantes antes de usá-lo em produção:

- Access e refresh tokens têm o mesmo payload e são validados pela mesma função. Assim, no estado atual, um `access_token` válido também consegue chamar `/auth/refresh`. O ideal é incluir uma claim como `"type": "access"` ou `"type": "refresh"` e exigir `refresh` na rota de renovação.
- Não há armazenamento, rotação, revogação ou lista de bloqueio de refresh tokens. Por isso, logout e comprometimento de token não invalidam um token já emitido (isto não necessariamente é um problema).
- A verificação atual confirma que o usuário existe, mas não verifica `usuario.ativo`. Se contas inativas não devem acessar a API, essa checagem deve ser adicionada.
- `GET /auth/refresh` cria um recurso credencial novo; por semântica HTTP e para reduzir exposição acidental, normalmente esse endpoint seria `POST`.
- Use HTTPS em produção, uma `SECRET_KEY` forte fora do repositório e armazenamento seguro dos tokens no cliente.

## Teste rápido

Com a API em execução (`uvicorn main:app --reload`), faça login, copie o `access_token` e teste uma rota protegida:

```bash
curl http://127.0.0.1:8000/pedidos/ \
  -H 'Authorization: Bearer <access_token>'
```

Quando o token de acesso expirar, troque-o pelo `refresh_token` somente na chamada a `/auth/refresh`, copie o novo `access_token` retornado e volte a usá-lo nas rotas protegidas.
