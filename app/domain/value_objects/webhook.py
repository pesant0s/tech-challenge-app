from enum import Enum


class AcaoWebhook(str, Enum):
    APROVAR = "APROVAR"
    REJEITAR = "REJEITAR"
