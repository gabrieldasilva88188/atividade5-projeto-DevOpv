"""Funções puras de validação (sem I/O) — alvo principal dos testes unitários."""
from .errors import ValidationError

PRIORITIES = ("low", "medium", "high")
MAX_TITLE_LENGTH = 100
MAX_TAGS = 5


def validate_title(title) -> str:
    if not isinstance(title, str):
        raise ValidationError("title deve ser um texto")
    title = title.strip()
    if not title:
        raise ValidationError("title não pode ser vazio")
    if len(title) > MAX_TITLE_LENGTH:
        raise ValidationError(f"title deve ter no máximo {MAX_TITLE_LENGTH} caracteres")
    return title


def validate_priority(priority) -> str:
    if priority not in PRIORITIES:
        raise ValidationError(f"priority deve ser uma de: {', '.join(PRIORITIES)}")
    return priority


def normalize_tags(tags) -> list:
    if tags is None:
        return []
    if not isinstance(tags, (list, tuple)):
        raise ValidationError("tags deve ser uma lista")
    result = []
    for tag in tags:
        if not isinstance(tag, str) or not tag.strip():
            raise ValidationError("cada tag deve ser um texto não vazio")
        clean = tag.strip().lower()
        if clean not in result:
            result.append(clean)
    if len(result) > MAX_TAGS:
        raise ValidationError(f"no máximo {MAX_TAGS} tags por tarefa")
    return result
