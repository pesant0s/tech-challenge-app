import logging

logger = logging.getLogger("oficina.os")


def registrar_mudanca_de_status(os) -> None:
    """Loga a entrada da OS no status atual e o tempo que ela passou no anterior; base dos dashboards."""
    *anteriores, atual = os.historico
    anterior = anteriores[-1] if anteriores else None
    logger.info("OS %s entrou em %s", os.id, atual.status.value, extra={
        "evento": "os_status",
        "os_id": str(os.id),
        "status_anterior": anterior.status.value if anterior else None,
        "status_novo": atual.status.value,
        "segundos_no_status_anterior": (atual.entrou_em - anterior.entrou_em).total_seconds() if anterior else None,
    })
