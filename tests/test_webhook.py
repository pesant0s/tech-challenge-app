CPF_WH = "529.982.247-25"
VALID_TOKEN = "webhook-secret-local"


def _setup(client, auth_headers):
    """Cria cliente, veículo, serviço e OS em AGUARDANDO_APROVACAO."""
    cliente = client.post("/cadastro/clientes", json={
        "nome": "Cliente Webhook", "cpf_cnpj": CPF_WH, "telefone": "11999999999"
    }, headers=auth_headers).json()
    veiculo = client.post("/cadastro/veiculos", json={
        "placa": "WBH-0001", "marca": "Toyota", "modelo": "Corolla",
        "ano": "2022", "cliente_id": cliente["id"]
    }, headers=auth_headers).json()
    servico = client.post("/catalogo/servicos", json={
        "nome": "Revisão", "preco": 200.0
    }, headers=auth_headers).json()
    os = client.post("/atendimento/os", json={
        "cliente_id": cliente["id"], "veiculo_id": veiculo["id"],
        "servicos": [{"servico_id": servico["id"], "quantidade": 1}]
    }, headers=auth_headers).json()
    return os


def test_webhook_aprovar_os(client, auth_headers):
    os = _setup(client, auth_headers)
    r = client.post("/webhooks/email", json={
        "os_id": os["id"], "acao": "APROVAR",
        "cpf_cnpj": CPF_WH, "token": VALID_TOKEN,
    })
    assert r.status_code == 200
    assert r.json()["status"] == "RECEBIDA"


def test_webhook_rejeitar_os(client, auth_headers):
    os = _setup(client, auth_headers)
    r = client.post("/webhooks/email", json={
        "os_id": os["id"], "acao": "REJEITAR",
        "cpf_cnpj": CPF_WH, "token": VALID_TOKEN,
    })
    assert r.status_code == 200
    assert r.json()["status"] == "NEGADA"


def test_webhook_token_invalido(client, auth_headers):
    os = _setup(client, auth_headers)
    r = client.post("/webhooks/email", json={
        "os_id": os["id"], "acao": "APROVAR",
        "cpf_cnpj": CPF_WH, "token": "token-errado",
    })
    assert r.status_code == 403


def test_webhook_acao_invalida(client, auth_headers):
    os = _setup(client, auth_headers)
    r = client.post("/webhooks/email", json={
        "os_id": os["id"], "acao": "DELETAR",
        "cpf_cnpj": CPF_WH, "token": VALID_TOKEN,
    })
    assert r.status_code == 422


def test_webhook_os_nao_encontrada(client, auth_headers):
    r = client.post("/webhooks/email", json={
        "os_id": "00000000-0000-0000-0000-000000000000",
        "acao": "APROVAR",
        "cpf_cnpj": CPF_WH,
        "token": VALID_TOKEN,
    })
    assert r.status_code == 404


def test_webhook_cpf_errado(client, auth_headers):
    os = _setup(client, auth_headers)
    r = client.post("/webhooks/email", json={
        "os_id": os["id"], "acao": "APROVAR",
        "cpf_cnpj": "123.456.789-09",  # CPF válido mas de outro cliente
        "token": VALID_TOKEN,
    })
    assert r.status_code == 422
