"""Agregado OrdemDeServico sem banco, HTTP ou ORM: quebra aqui se o domínio voltar a depender da infraestrutura."""
from decimal import Decimal

import pytest

from app.domain.entities.os import ItemOS, OrdemDeServico, StatusOS
from app.domain.exceptions import BusinessRuleException


def test_os_nova_nasce_com_colecao_de_itens_vazia():
    assert OrdemDeServico().itens == []


def test_os_nova_registra_o_status_inicial_no_historico():
    assert [h.status for h in OrdemDeServico().historico] == [StatusOS.AGUARDANDO_APROVACAO]


def test_recalcular_total_sem_banco():
    os_teste = OrdemDeServico(itens=[
        ItemOS(servico_id="s1", quantidade=2, preco_unitario=Decimal("150.00")),
        ItemOS(peca_id="p1", quantidade=3, preco_unitario=Decimal("29.90")),
    ])
    os_teste.recalcular_total()
    assert os_teste.valor_total == Decimal("389.70")


def test_recalcular_total_de_os_sem_itens_e_zero():
    os_teste = OrdemDeServico()
    os_teste.recalcular_total()
    assert os_teste.valor_total == 0


def test_subtotal_do_item_preserva_precisao_decimal():
    assert ItemOS(peca_id="p1", quantidade=3, preco_unitario=Decimal("0.10")).calcular_subtotal() == Decimal("0.30")


def test_fluxo_completo_da_os_em_memoria():
    os_teste = OrdemDeServico()
    os_teste.aprovar()
    os_teste.transicionar_para(StatusOS.EM_DIAGNOSTICO)
    os_teste.transicionar_para(StatusOS.EM_EXECUCAO)
    os_teste.transicionar_para(StatusOS.FINALIZADA)
    os_teste.transicionar_para(StatusOS.ENTREGUE)
    assert os_teste.status == StatusOS.ENTREGUE
    assert [h.status.value for h in os_teste.historico] == [
        "AGUARDANDO_APROVACAO", "RECEBIDA", "EM_DIAGNOSTICO", "EM_EXECUCAO", "FINALIZADA", "ENTREGUE",
    ]
    assert os_teste.historico[-2].entrou_em == os_teste.finalizado_em
    assert os_teste.finalizado_em >= os_teste.iniciado_em


def test_transicao_fora_do_mapa_e_recusada():
    os_teste = OrdemDeServico()
    with pytest.raises(BusinessRuleException, match="Transição inválida"):
        os_teste.transicionar_para(StatusOS.FINALIZADA)
    assert len(os_teste.historico) == 1


def test_estado_terminal_nao_transiciona():
    os_teste = OrdemDeServico()
    os_teste.rejeitar()
    with pytest.raises(BusinessRuleException):
        os_teste.transicionar_para(StatusOS.RECEBIDA)


def test_aprovar_so_vale_aguardando_aprovacao():
    with pytest.raises(BusinessRuleException, match="não está aguardando aprovação"):
        OrdemDeServico(status=StatusOS.EM_EXECUCAO).aprovar()
