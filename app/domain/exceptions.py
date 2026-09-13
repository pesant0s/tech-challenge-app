class NotFoundException(Exception):
    def __init__(self, detail: str = "Recurso não encontrado"):
        super().__init__(detail)
        self.detail = detail


class ConflictException(Exception):
    def __init__(self, detail: str = "Conflito de dados"):
        super().__init__(detail)
        self.detail = detail


class BusinessRuleException(Exception):
    def __init__(self, detail: str = "Regra de negócio violada"):
        super().__init__(detail)
        self.detail = detail
