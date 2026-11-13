import requests

headers = {
    "Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIzIiwiZXhwIjoxNzk0NTIyNjg0fQ.7DsaqYKm1OMLe8IQNXk3o8EbQ9kEcKJd_dTlYEE-HbU"
}

requisicao = requests.get("http://127.0.0.1:8000/auth/refresh", headers=headers)
print('Response da requisicao',requisicao)
print('codigo da requisicao:', requisicao.status_code)

print('requisicao.json():', requisicao.json())
print('requisicao.headers:', requisicao.headers)
print('requisicao.text:', requisicao.text)
print('pegando o token do json da requisicao:', requisicao.json()['access_token']   )


"""
MODO DE TESTAR: 
    python3 testes.py

O código acima só deu certo após instalar o requests:

cd "/home/gilberto/APRENDIZADO/python/python impressionador/python-fastAPI/fastAPI"
 && source .venv/bin/activate 
 && python -m pip install -U pip && python -m pip install requests
 
 FORMA DE TESTAR SE O REQUESTS ESTÁ INSTALADO:  
 python -c "import requests; print('requests OK', requests.__version__)"
 FORMA DE TESTAR SE O REQUESTS ESTÁ INSTALADO:
 python -c "import requests; print('requests OK', requests.__version__)"
 FORMA DE TESTAR SE O REQUESTS ESTÁ INSTALADO:

"""