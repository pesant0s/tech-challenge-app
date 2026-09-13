import re

# CPFs válidos (verificados com o algoritmo de dígito verificador)
CPF_1 = "529.982.247-25"   # normalizado: 52998224725
CPF_2 = "123.456.789-09"   # normalizado: 12345678909
CPF_3 = "000.000.001-91"   # normalizado: 00000000191
CPF_4 = "123.456.787-39"   # normalizado: 12345678739
CPF_5 = "987.654.321-00"   # normalizado: 98765432100
CPF_6 = "246.824.682-94"   # normalizado: 24682468294


def _digits(v: str) -> str:
    return re.sub(r"\D", "", v)


def test_criar_cliente(client, auth_headers):
    r = client.post("/cadastro/clientes", json={
        "nome": "João Silva", "cpf_cnpj": CPF_1,
        "telefone": "11999999999", "email": "joao@email.com"
    }, headers=auth_headers)
    assert r.status_code == 201
    assert r.json()["nome"] == "João Silva"
    # CPF e telefone são armazenados e retornados normalizados (apenas dígitos)
    assert r.json()["cpf_cnpj"] == _digits(CPF_1)
    assert r.json()["telefone"] == "11999999999"


def test_criar_cliente_cpf_com_letras(client, auth_headers):
    r = client.post("/cadastro/clientes", json={
        "nome": "Fraude", "cpf_cnpj": "14698qqweqw083745", "telefone": "11999999999"
    }, headers=auth_headers)
    assert r.status_code == 422


def test_criar_cliente_cpf_invalido_digitos(client, auth_headers):
    r = client.post("/cadastro/clientes", json={
        "nome": "Teste", "cpf_cnpj": "111.111.111-11", "telefone": "11999999999"
    }, headers=auth_headers)
    assert r.status_code == 422


def test_criar_cliente_nome_curto(client, auth_headers):
    r = client.post("/cadastro/clientes", json={
        "nome": "A", "cpf_cnpj": CPF_1, "telefone": "11999999999"
    }, headers=auth_headers)
    assert r.status_code == 422


def test_criar_cliente_telefone_invalido(client, auth_headers):
    r = client.post("/cadastro/clientes", json={
        "nome": "João", "cpf_cnpj": CPF_1, "telefone": "123"
    }, headers=auth_headers)
    assert r.status_code == 422


def test_criar_cliente_telefone_com_letras(client, auth_headers):
    r = client.post("/cadastro/clientes", json={
        "nome": "João", "cpf_cnpj": CPF_1, "telefone": "119abc99999"
    }, headers=auth_headers)
    assert r.status_code == 422


def test_cpf_duplicado(client, auth_headers):
    payload = {"nome": "João", "cpf_cnpj": CPF_2, "telefone": "11999999999"}
    r1 = client.post("/cadastro/clientes", json=payload, headers=auth_headers)
    assert r1.status_code == 201
    r2 = client.post("/cadastro/clientes", json=payload, headers=auth_headers)
    assert r2.status_code == 409


def test_cpf_duplicado_formatacao_diferente(client, auth_headers):
    """Mesmo CPF com e sem pontuação deve ser detectado como duplicata."""
    r1 = client.post("/cadastro/clientes", json={
        "nome": "Formatado", "cpf_cnpj": CPF_1, "telefone": "11999999999"
    }, headers=auth_headers)
    assert r1.status_code == 201
    r2 = client.post("/cadastro/clientes", json={
        "nome": "Sem formatacao", "cpf_cnpj": _digits(CPF_1), "telefone": "11988888888"
    }, headers=auth_headers)
    assert r2.status_code == 409


def test_listar_clientes(client, auth_headers):
    r = client.get("/cadastro/clientes", headers=auth_headers)
    assert r.status_code == 200
    assert isinstance(r.json(), list)


def test_listar_clientes_paginacao(client, auth_headers):
    for cpf in [CPF_1, CPF_2, CPF_3]:
        client.post("/cadastro/clientes", json={
            "nome": "Cliente", "cpf_cnpj": cpf, "telefone": "11999999999"
        }, headers=auth_headers)
    r = client.get("/cadastro/clientes?skip=0&limit=2", headers=auth_headers)
    assert r.status_code == 200
    assert len(r.json()) == 2


def test_buscar_cliente_por_cpf_formatado(client, auth_headers):
    client.post("/cadastro/clientes", json={
        "nome": "Ana", "cpf_cnpj": CPF_3, "telefone": "11999999999"
    }, headers=auth_headers)
    r = client.get(f"/cadastro/clientes/buscar?cpf_cnpj={CPF_3}", headers=auth_headers)
    assert r.status_code == 200
    assert r.json()["cpf_cnpj"] == _digits(CPF_3)


def test_buscar_cliente_por_cpf_sem_formatacao(client, auth_headers):
    """Busca com CPF sem formatação deve encontrar o cliente cadastrado com formatação."""
    client.post("/cadastro/clientes", json={
        "nome": "Ana", "cpf_cnpj": CPF_3, "telefone": "11999999999"
    }, headers=auth_headers)
    r = client.get(f"/cadastro/clientes/buscar?cpf_cnpj={_digits(CPF_3)}", headers=auth_headers)
    assert r.status_code == 200


def test_buscar_cliente_cpf_com_letras(client, auth_headers):
    r = client.get("/cadastro/clientes/buscar?cpf_cnpj=14698083745q", headers=auth_headers)
    assert r.status_code == 422


def test_buscar_cliente_nao_encontrado(client, auth_headers):
    r = client.get(f"/cadastro/clientes/buscar?cpf_cnpj={CPF_4}", headers=auth_headers)
    assert r.status_code == 404


def test_obter_cliente_por_id(client, auth_headers):
    c = client.post("/cadastro/clientes", json={
        "nome": "Maria", "cpf_cnpj": CPF_4, "telefone": "11999999999"
    }, headers=auth_headers).json()
    r = client.get(f"/cadastro/clientes/{c['id']}", headers=auth_headers)
    assert r.status_code == 200
    assert r.json()["id"] == c["id"]


def test_obter_cliente_nao_encontrado(client, auth_headers):
    r = client.get("/cadastro/clientes/00000000-0000-0000-0000-000000000000", headers=auth_headers)
    assert r.status_code == 404


def test_atualizar_cliente(client, auth_headers):
    c = client.post("/cadastro/clientes", json={
        "nome": "Nome Antigo", "cpf_cnpj": CPF_5, "telefone": "11999999999"
    }, headers=auth_headers).json()
    r = client.patch(f"/cadastro/clientes/{c['id']}", json={
        "nome": "Nome Novo", "telefone": "11988888888"
    }, headers=auth_headers)
    assert r.status_code == 200
    assert r.json()["nome"] == "Nome Novo"
    assert r.json()["cpf_cnpj"] == _digits(CPF_5)  # CPF não muda


def test_nao_pode_alterar_cpf(client, auth_headers):
    c = client.post("/cadastro/clientes", json={
        "nome": "Imutável", "cpf_cnpj": CPF_6, "telefone": "11999999999"
    }, headers=auth_headers).json()
    r = client.patch(f"/cadastro/clientes/{c['id']}", json={
        "nome": "Novo Nome", "cpf_cnpj": CPF_2, "telefone": "11999999999"
    }, headers=auth_headers)
    assert r.status_code == 422


def test_criar_veiculo(client, auth_headers):
    c = client.post("/cadastro/clientes", json={
        "nome": "Maria", "cpf_cnpj": CPF_2, "telefone": "11999999999"
    }, headers=auth_headers).json()
    r = client.post("/cadastro/veiculos", json={
        "placa": "ABC-1234", "marca": "Toyota", "modelo": "Corolla",
        "ano": "2020", "cliente_id": c["id"]
    }, headers=auth_headers)
    assert r.status_code == 201


def test_criar_veiculo_placa_mercosul(client, auth_headers):
    c = client.post("/cadastro/clientes", json={
        "nome": "Carlos", "cpf_cnpj": CPF_3, "telefone": "11999999999"
    }, headers=auth_headers).json()
    r = client.post("/cadastro/veiculos", json={
        "placa": "ABC1D23", "marca": "Honda", "modelo": "Civic",
        "ano": "2022", "cliente_id": c["id"]
    }, headers=auth_headers)
    assert r.status_code == 201


def test_placa_invalida(client, auth_headers):
    c = client.post("/cadastro/clientes", json={
        "nome": "Carlos", "cpf_cnpj": CPF_4, "telefone": "11999999999"
    }, headers=auth_headers).json()
    r = client.post("/cadastro/veiculos", json={
        "placa": "INVALIDA", "marca": "Ford", "modelo": "Ka",
        "ano": "2019", "cliente_id": c["id"]
    }, headers=auth_headers)
    assert r.status_code == 422


def test_placa_duplicada(client, auth_headers):
    c = client.post("/cadastro/clientes", json={
        "nome": "Pedro", "cpf_cnpj": CPF_5, "telefone": "11999999999"
    }, headers=auth_headers).json()
    payload = {"placa": "XYZ-9999", "marca": "VW", "modelo": "Gol", "ano": "2021", "cliente_id": c["id"]}
    r1 = client.post("/cadastro/veiculos", json=payload, headers=auth_headers)
    assert r1.status_code == 201
    r2 = client.post("/cadastro/veiculos", json=payload, headers=auth_headers)
    assert r2.status_code == 409


def test_listar_veiculos_do_cliente(client, auth_headers):
    c = client.post("/cadastro/clientes", json={
        "nome": "Lucas", "cpf_cnpj": CPF_6, "telefone": "11999999999"
    }, headers=auth_headers).json()
    client.post("/cadastro/veiculos", json={
        "placa": "DEF-1111", "marca": "Fiat", "modelo": "Uno", "ano": "2018", "cliente_id": c["id"]
    }, headers=auth_headers)
    r = client.get(f"/cadastro/clientes/{c['id']}/veiculos", headers=auth_headers)
    assert r.status_code == 200
    assert len(r.json()) == 1


def test_atualizar_veiculo(client, auth_headers):
    c = client.post("/cadastro/clientes", json={
        "nome": "Teste", "cpf_cnpj": CPF_1, "telefone": "11999999999"
    }, headers=auth_headers).json()
    v = client.post("/cadastro/veiculos", json={
        "placa": "GHI-2222", "marca": "Chevrolet", "modelo": "Onix", "ano": "2020", "cliente_id": c["id"]
    }, headers=auth_headers).json()
    r = client.put(f"/cadastro/veiculos/{v['id']}", json={
        "placa": "GHI-2222", "marca": "Chevrolet", "modelo": "Onix Plus", "ano": "2021", "cliente_id": c["id"]
    }, headers=auth_headers)
    assert r.status_code == 200
    assert r.json()["modelo"] == "Onix Plus"


def test_deletar_veiculo(client, auth_headers):
    c = client.post("/cadastro/clientes", json={
        "nome": "Delete Test", "cpf_cnpj": CPF_2, "telefone": "11999999999"
    }, headers=auth_headers).json()
    v = client.post("/cadastro/veiculos", json={
        "placa": "JKL-3333", "marca": "Renault", "modelo": "Sandero", "ano": "2019", "cliente_id": c["id"]
    }, headers=auth_headers).json()
    r = client.delete(f"/cadastro/veiculos/{v['id']}", headers=auth_headers)
    assert r.status_code == 204


def test_rota_sem_auth(client):
    r = client.get("/cadastro/clientes")
    assert r.status_code == 401
