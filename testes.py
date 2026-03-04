import requests

headers = {
    "Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwiZXhwIjoxNzcyNDkxMTMzfQ.nJHKmiGe33nv4qrjtx6ApETTS-o3c5NQZjYBE1AkRJA"
}

requisicao = requests.get("http://127.0.0.1:8000/auth/refresh", headers=headers)
print(requisicao)
print(requisicao.json())


"""
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