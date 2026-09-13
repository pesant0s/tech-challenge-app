import logging

CPF_NOT = "529.982.247-25"


def _setup(client, auth_headers):
    cliente = client.post("/cadastro/clientes", json={
        "nome": "Cliente Notif", "cpf_cnpj": CPF_NOT,
        "telefone": "11988887777", "email": "cliente@exemplo.com",
    }, headers=auth_headers).json()
    veiculo = client.post("/cadastro/veiculos", json={
        "placa": "NOT-2024", "marca": "Fiat", "modelo": "Uno",
        "ano": "2019", "cliente_id": cliente["id"],
    }, headers=auth_headers).json()
    servico = client.post("/catalogo/servicos", json={
        "nome": "Alinhamento", "preco": 80.0,
    }, headers=auth_headers).json()
    return cliente, veiculo, servico


def test_criar_os_dispara_email_de_aprovacao(client, auth_headers, caplog):
    """A criação de OS deve acionar a porta de saída de notificação (e-mail simulado)."""
    c, v, s = _setup(client, auth_headers)
    with caplog.at_level(logging.INFO, logger="oficina.notificacoes"):
        r = client.post("/atendimento/os", json={
            "cliente_id": c["id"], "veiculo_id": v["id"],
            "servicos": [{"servico_id": s["id"], "quantidade": 1}],
        }, headers=auth_headers)
    assert r.status_code == 201
    mensagens = [rec.getMessage() for rec in caplog.records]
    assert any("E-MAIL SIMULADO" in m and "cliente@exemplo.com" in m for m in mensagens), \
        "Notificação de aprovação pendente não foi disparada ao criar a OS"
