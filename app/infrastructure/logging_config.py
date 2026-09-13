"""Logs com o correlation_id da requisição, propagado por ContextVar até os casos de uso."""
import json
import logging
from contextvars import ContextVar
from datetime import datetime, timezone

_correlation_id: ContextVar[str] = ContextVar("correlation_id", default="")

# Atributos nativos do LogRecord; o restante são campos passados em `extra`.
_ATRIBUTOS_PADRAO = frozenset((
    "args", "asctime", "created", "exc_info", "exc_text", "filename", "funcName",
    "levelname", "levelno", "lineno", "module", "msecs", "message", "msg", "name",
    "pathname", "process", "processName", "relativeCreated", "stack_info",
    "taskName", "thread", "threadName",
))


def definir_correlation_id(valor: str) -> None:
    _correlation_id.set(valor)


def obter_correlation_id() -> str:
    return _correlation_id.get()


class JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        evento = {
            "timestamp": datetime.fromtimestamp(record.created, timezone.utc).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }
        if correlation_id := _correlation_id.get():
            evento["correlation_id"] = correlation_id
        if record.exc_info:
            evento["exception"] = self.formatException(record.exc_info)
        evento.update({k: v for k, v in record.__dict__.items() if k not in _ATRIBUTOS_PADRAO and not k.startswith("_")})
        return json.dumps(evento, ensure_ascii=False, default=str)


class ConsoleFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        marca = f" [{c[:8]}]" if (c := _correlation_id.get()) else ""
        linha = f"{self.formatTime(record)} | {record.levelname:<8}{marca} | {record.name} | {record.getMessage()}"
        return f"{linha}\n{self.formatException(record.exc_info)}" if record.exc_info else linha
