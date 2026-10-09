class ValidationError(ValueError):
    """Dados de entrada inválidos."""


class NotFoundError(LookupError):
    """Recurso não encontrado."""
