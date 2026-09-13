import logging
import time
import uuid

from starlette.middleware.base import BaseHTTPMiddleware

from app.infrastructure.logging_config import definir_correlation_id, obter_correlation_id

logger = logging.getLogger("oficina.http")

# Aceita o id vindo do API Gateway ou de outro serviço, para o fluxo manter a mesma marca.
CABECALHOS_ACEITOS = ("x-request-id", "x-correlation-id", "x-amzn-trace-id")


class CorrelationIdMiddleware(BaseHTTPMiddleware):
    """Marca a requisição com um id, registra entrada e saída e devolve o id ao cliente."""

    async def dispatch(self, request, call_next):
        recebido = next((request.headers[c] for c in CABECALHOS_ACEITOS if request.headers.get(c)), None)
        definir_correlation_id(recebido or str(uuid.uuid4()))
        extra = {"http_method": request.method, "http_path": request.url.path}
        inicio = time.perf_counter()
        try:
            response = await call_next(request)
        except Exception:
            logger.exception("Requisição falhou", extra={**extra, "duracao_ms": round((time.perf_counter() - inicio) * 1000, 2)})
            raise
        logger.info("%s %s %s", request.method, request.url.path, response.status_code, extra={
            **extra, "http_status": response.status_code, "duracao_ms": round((time.perf_counter() - inicio) * 1000, 2),
        })
        response.headers["x-request-id"] = obter_correlation_id()
        return response


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Cabeçalhos de segurança e ofuscação do servidor."""

    async def dispatch(self, request, call_next):
        response = await call_next(request)
        response.headers["server"] = "webserver"
        response.headers["x-content-type-options"] = "nosniff"
        response.headers["x-frame-options"] = "DENY"
        response.headers["referrer-policy"] = "no-referrer"
        return response
