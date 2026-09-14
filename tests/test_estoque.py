CPF_ESTOQUE = "529.982.247-25"
CPF_ESTOQUE_2 = "123.456.789-09"


def _criar_peca(client, auth_headers, nome="Filtro de óleo", preco=35.00, quantidade=10, estoque_minimo=2):
    return client.post("/estoque/pecas", json={
        "nome": nome, "preco": preco, "quantidade": quantidade, "estoque_minimo": estoque_minimo
    }, headers=auth_headers).json()


def test_criar_peca(client, auth_headers):
    r = client.post("/estoque/pecas", json={
        "nome": "Filtro de óleo", "preco": 35.00, "quantidade": 10, "estoque_minimo": 2
    }, headers=auth_headers)
    assert r.status_code == 201
    assert r.json()["quantidade"] == 10


def test_criar_peca_preco_invalido(client, auth_headers):
    r = client.post("/estoque/pecas", json={
        "nome": "Peça", "preco": -10.00, "quantidade": 5, "estoque_minimo": 1
    }, headers=auth_headers)
    assert r.status_code == 422


def test_criar_peca_quantidade_negativa(client, auth_headers):
    r = client.post("/estoque/pecas", json={
        "nome": "Peça", "preco": 10.00, "quantidade": -1, "estoque_minimo": 1
    }, headers=auth_headers)
    assert r.status_code == 422


def test_listar_pecas(client, auth_headers):
    _criar_peca(client, auth_headers, "Peça A")
    _criar_peca(client, auth_headers, "Peça B")
    r = client.get("/estoque/pecas", headers=auth_headers)
    assert r.status_code == 200
    assert len(r.json()) == 2


def test_listar_pecas_paginacao(client, auth_headers):
    for i in range(3):
        _criar_peca(client, auth_headers, nome=f"Peça {i}")
    r = client.get("/estoque/pecas?skip=0&limit=2", headers=auth_headers)
    assert r.status_code == 200
    assert len(r.json()) == 2


def test_obter_peca(client, auth_headers):
    p = _criar_peca(client, auth_headers)
    r = client.get(f"/estoque/pecas/{p['id']}", headers=auth_headers)
    assert r.status_code == 200
    assert r.json()["id"] == p["id"]


def test_obter_peca_nao_encontrada(client, auth_headers):
    r = client.get("/estoque/pecas/00000000-0000-0000-0000-000000000000", headers=auth_headers)
    assert r.status_code == 404


def test_atualizar_peca(client, auth_headers):
    p = _criar_peca(client, auth_headers, nome="Nome Antigo")
    r = client.put(f"/estoque/pecas/{p['id']}", json={
        "nome": "Nome Novo", "preco": 50.00, "quantidade": 10, "estoque_minimo": 2
    }, headers=auth_headers)
    assert r.status_code == 200
    assert r.json()["nome"] == "Nome Novo"


def test_deletar_peca(client, auth_headers):
    p = _criar_peca(client, auth_headers, nome="Peça para deletar")
    r = client.delete(f"/estoque/pecas/{p['id']}", headers=auth_headers)
    assert r.status_code == 204


def test_deletar_peca_vinculada_a_os(client, auth_headers):
    peca = _criar_peca(client, auth_headers, nome="Pastilha vinculada")
    cliente = client.post("/cadastro/clientes", json={
        "nome": "Cliente", "cpf_cnpj": CPF_ESTOQUE, "telefone": "11999999999"
    }, headers=auth_headers).json()
    veiculo = client.post("/cadastro/veiculos", json={
        "placa": "DEL-0001", "marca": "Fiat", "modelo": "Uno",
        "ano": "2018", "cliente_id": cliente["id"]
    }, headers=auth_headers).json()
    client.post("/atendimento/os", json={
        "cliente_id": cliente["id"], "veiculo_id": veiculo["id"],
        "pecas": [{"peca_id": peca["id"], "quantidade": 1}]
    }, headers=auth_headers)
    r = client.delete(f"/estoque/pecas/{peca['id']}", headers=auth_headers)
    assert r.status_code == 422


def test_entrada_estoque(client, auth_headers):
    peca = _criar_peca(client, auth_headers, nome="Correia", quantidade=5)
    r = client.post(f"/estoque/pecas/{peca['id']}/entrada",
        json={"quantidade": 10, "motivo": "Compra NF 123"}, headers=auth_headers)
    assert r.status_code == 200
    assert r.json()["quantidade"] == 15


def test_entrada_estoque_quantidade_zero(client, auth_headers):
    peca = _criar_peca(client, auth_headers)
    r = client.post(f"/estoque/pecas/{peca['id']}/entrada",
        json={"quantidade": 0}, headers=auth_headers)
    assert r.status_code == 422


def test_entrada_estoque_quantidade_negativa(client, auth_headers):
    peca = _criar_peca(client, auth_headers)
    r = client.post(f"/estoque/pecas/{peca['id']}/entrada",
        json={"quantidade": -5}, headers=auth_headers)
    assert r.status_code == 422


def test_alerta_estoque_minimo(client, auth_headers):
    peca = _criar_peca(client, auth_headers, nome="Pastilha", quantidade=3, estoque_minimo=5)
    cliente = client.post("/cadastro/clientes", json={
        "nome": "Alerta Test", "cpf_cnpj": CPF_ESTOQUE_2, "telefone": "11999999999"
    }, headers=auth_headers).json()
    veiculo = client.post("/cadastro/veiculos", json={
        "placa": "ALR-0001", "marca": "VW", "modelo": "Gol", "ano": "2020", "cliente_id": cliente["id"]
    }, headers=auth_headers).json()
    os_resp = client.post("/atendimento/os", json={
        "cliente_id": cliente["id"], "veiculo_id": veiculo["id"],
        "pecas": [{"peca_id": peca["id"], "quantidade": 2}]
    }, headers=auth_headers).json()
    for s in ["RECEBIDA", "EM_DIAGNOSTICO", "EM_EXECUCAO"]:
        client.patch(f"/atendimento/os/{os_resp['id']}/status",
            json={"status": s}, headers=auth_headers)
    peca_atualizada = client.get(f"/estoque/pecas/{peca['id']}", headers=auth_headers).json()
    assert peca_atualizada["quantidade"] == 1
    assert peca_atualizada["quantidade"] < peca_atualizada["estoque_minimo"]


def test_baixa_automatica_ao_executar(client, auth_headers):
    peca = _criar_peca(client, auth_headers, nome="Pastilha de freio", preco=120.00, quantidade=5)
    cliente = client.post("/cadastro/clientes", json={
        "nome": "Lucas", "cpf_cnpj": CPF_ESTOQUE, "telefone": "11999999999"
    }, headers=auth_headers).json()
    veiculo = client.post("/cadastro/veiculos", json={
        "placa": "DEF-5678", "marca": "Fiat", "modelo": "Uno",
        "ano": "2018", "cliente_id": cliente["id"]
    }, headers=auth_headers).json()
    os = client.post("/atendimento/os", json={
        "cliente_id": cliente["id"], "veiculo_id": veiculo["id"],
        "pecas": [{"peca_id": peca["id"], "quantidade": 2}]
    }, headers=auth_headers).json()
    for s in ["RECEBIDA", "EM_DIAGNOSTICO", "EM_EXECUCAO"]:
        client.patch(f"/atendimento/os/{os['id']}/status",
            json={"status": s}, headers=auth_headers)
    peca_atualizada = client.get(f"/estoque/pecas/{peca['id']}", headers=auth_headers).json()
    assert peca_atualizada["quantidade"] == 3


def test_estoque_insuficiente_ao_executar_os(client, auth_headers):
    peca = _criar_peca(client, auth_headers, nome="Peça escassa", quantidade=1)
    cliente = client.post("/cadastro/clientes", json={
        "nome": "Sem Estoque", "cpf_cnpj": CPF_ESTOQUE, "telefone": "11999999999"
    }, headers=auth_headers).json()
    veiculo = client.post("/cadastro/veiculos", json={
        "placa": "SEM-0001", "marca": "Fiat", "modelo": "Palio", "ano": "2015", "cliente_id": cliente["id"]
    }, headers=auth_headers).json()
    os = client.post("/atendimento/os", json={
        "cliente_id": cliente["id"], "veiculo_id": veiculo["id"],
        "pecas": [{"peca_id": peca["id"], "quantidade": 5}]
    }, headers=auth_headers)
    assert os.status_code == 422


def test_entrada_de_estoque_trava_a_linha():
    """Sem SELECT FOR UPDATE, duas entradas simultâneas perderiam uma das somas."""
    from decimal import Decimal
    from uuid import uuid4
    from app.application.use_cases.gerenciar_estoque import GerenciarEstoqueUseCase
    from app.domain.entities.estoque import Peca

    class RepoQueRegistraATrava:
        def __init__(self):
            self.travou = False
            self.peca = Peca(nome="Correia", preco=Decimal("10"), quantidade=5, estoque_minimo=1)

        def buscar_peca_para_escrita(self, peca_id):
            self.travou = True
            return self.peca

        def registrar_movimentacao(self, *args):
            pass

        def commit(self):
            pass

        def refresh(self, peca):
            pass

    repo = RepoQueRegistraATrava()
    peca = GerenciarEstoqueUseCase(repo).registrar_entrada(uuid4(), 10, "Compra NF 1")
    assert repo.travou, "a entrada precisa travar a linha antes de somar"
    assert peca.quantidade == 15
