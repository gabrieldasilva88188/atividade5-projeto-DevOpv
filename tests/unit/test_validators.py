import pytest

from app.errors import ValidationError
from app.validators import (
    MAX_TAGS,
    MAX_TITLE_LENGTH,
    normalize_tags,
    validate_priority,
    validate_title,
)


class TestValidateTitle:
    def test_remove_espacos_nas_pontas(self):
        assert validate_title("  Estudar CI/CD  ") == "Estudar CI/CD"

    @pytest.mark.parametrize("valor", ["", "   ", "\t\n"])
    def test_rejeita_vazio(self, valor):
        with pytest.raises(ValidationError):
            validate_title(valor)

    @pytest.mark.parametrize("valor", [None, 123, ["a"]])
    def test_rejeita_tipo_invalido(self, valor):
        with pytest.raises(ValidationError):
            validate_title(valor)

    def test_aceita_tamanho_maximo(self):
        titulo = "a" * MAX_TITLE_LENGTH
        assert validate_title(titulo) == titulo

    def test_rejeita_acima_do_maximo(self):
        with pytest.raises(ValidationError):
            validate_title("a" * (MAX_TITLE_LENGTH + 1))


class TestValidatePriority:
    @pytest.mark.parametrize("valor", ["low", "medium", "high"])
    def test_aceita_valores_validos(self, valor):
        assert validate_priority(valor) == valor

    @pytest.mark.parametrize("valor", ["urgent", "", None, "HIGH"])
    def test_rejeita_valores_invalidos(self, valor):
        with pytest.raises(ValidationError):
            validate_priority(valor)


class TestNormalizeTags:
    def test_none_vira_lista_vazia(self):
        assert normalize_tags(None) == []

    def test_normaliza_caixa_e_remove_duplicadas(self):
        assert normalize_tags([" Python ", "python", "CI"]) == ["python", "ci"]

    def test_preserva_ordem(self):
        assert normalize_tags(["b", "a", "c"]) == ["b", "a", "c"]

    def test_rejeita_nao_lista(self):
        with pytest.raises(ValidationError):
            normalize_tags("python")

    @pytest.mark.parametrize("tags", [[""], ["  "], [1], [None]])
    def test_rejeita_tag_invalida(self, tags):
        with pytest.raises(ValidationError):
            normalize_tags(tags)

    def test_rejeita_excesso_de_tags(self):
        with pytest.raises(ValidationError):
            normalize_tags([f"t{i}" for i in range(MAX_TAGS + 1)])
