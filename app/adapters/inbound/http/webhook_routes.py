import hmac
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.infrastructure.database import get_db
from app.infrastructure.config import settings
from app.adapters.inbound.http.webhook_schemas import WebhookEmailPayload
from app.adapters.inbound.http.atendimento_schemas import OSResponse
from app.adapters.outbound.persistence.os_repository import OSRepositoryAdapter
from app.adapters.outbound.persistence.cliente_repository import ClienteRepositoryAdapter
from app.application.use_cases.processar_webhook_email import ProcessarWebhookEmailUseCase

router = APIRouter(prefix="/webhooks", tags=["🔔 Webhooks"])


@router.post("/email", response_model=OSResponse,
    summary="Webhook de resposta por e-mail",
    description="""
Recebe a decisão do cliente (APROVAR / REJEITAR) via link de e-mail.

Autenticado por `token` comparado contra `WEBHOOK_SECRET` usando comparação
em tempo constante (`hmac.compare_digest`) para evitar timing attacks.

Não requer JWT — destinado a ser chamado pelo serviço de e-mail.
""")
def webhook_email(payload: WebhookEmailPayload, db: Session = Depends(get_db)):
    if not hmac.compare_digest(payload.token, settings.WEBHOOK_SECRET):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Token de webhook inválido",
        )
    return ProcessarWebhookEmailUseCase(
        os_repo=OSRepositoryAdapter(db),
        cliente_repo=ClienteRepositoryAdapter(db),
    ).executar(payload.os_id, payload.acao, payload.cpf_cnpj)
