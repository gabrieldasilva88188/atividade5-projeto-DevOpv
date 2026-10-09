"""Servidor para execução real e testes de carga (waitress, multiplataforma)."""
import os

from waitress import serve

from .api import create_app

if __name__ == "__main__":
    port = int(os.environ.get("PORT", "5055"))
    serve(create_app(), host="127.0.0.1", port=port, threads=8)
