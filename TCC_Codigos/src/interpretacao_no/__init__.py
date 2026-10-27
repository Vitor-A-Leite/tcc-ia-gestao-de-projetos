"""Interpretação local offline/injetável; não autoriza nem aplica propostas."""
from .contratos import montar_contexto, validar, hash_json, ContratoInvalido
from .adaptadores import Simulado, LLM, RespostaTransporte, FalhaTransporte
