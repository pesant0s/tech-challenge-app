from uuid import UUID
from pydantic import BaseModel, Field
from app.domain.value_objects.webhook import AcaoWebhook


class WebhookEmailPayload(BaseModel):
    os_id: UUID
    acao: AcaoWebhook
    cpf_cnpj: str = Field(min_length=11, max_length=18)
    token: str = Field(min_length=1)
