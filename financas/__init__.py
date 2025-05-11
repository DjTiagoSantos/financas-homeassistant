"""Organizador Financeiro para Home Assistant."""
from __future__ import annotations
import logging
import sqlite3
from datetime import datetime
from typing import Any

from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.helpers.entity import Entity
from homeassistant.helpers.typing import ConfigType

_LOGGER = logging.getLogger(__name__)

DOMAIN = "financas"
DB_NAME = "financas.db"

def setup(hass: HomeAssistant, config: ConfigType) -> bool:
    """Configurar a integração de finanças."""
    _LOGGER.info("Iniciando integração de finanças")

    # Inicializa o banco de dados
    if not init_database(hass):
        _LOGGER.error("Falha ao iniciar o banco de dados")
        return False

    # Registra os serviços
    hass.services.register(DOMAIN, "add_conta", add_conta)
    hass.services.register(DOMAIN, "marcar_como_pago", marcar_como_pago)

    # Cria os sensores iniciais
    hass.helpers.discovery.load_platform("sensor", DOMAIN, {}, config)

    return True

def init_database(hass: HomeAssistant) -> bool:
    """Cria o banco de dados SQLite se não existir."""
    db_path = hass.config.path(DB_NAME)
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS contas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                descricao TEXT NOT NULL,
                valor REAL NOT NULL,
                data_vencimento TEXT NOT NULL,
                pago BOOLEAN DEFAULT FALSE,
                data_pagamento TEXT
            )
        """)
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        _LOGGER.error(f"Erro ao criar banco de dados: {e}")
        return False

def add_conta(call: ServiceCall) -> None:
    """Adiciona uma nova conta ao sistema."""
    descricao = call.data.get("descricao")
    valor = call.data.get("valor")
    data_vencimento = call.data.get("data_vencimento")

    if not all([descricao, valor, data_vencimento]):
        _LOGGER.error("Dados incompletos para adicionar conta")
        return

    hass = call.data.get("hass")
    db_path = hass.config.path(DB_NAME)
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO contas (descricao, valor, data_vencimento, pago)
            VALUES (?, ?, ?, ?)
        """, (descricao, valor, data_vencimento, False))
        conn.commit()
        conn.close()
        _LOGGER.info(f"Conta '{descricao}' adicionada com sucesso!")
    except Exception as e:
        _LOGGER.error(f"Erro ao adicionar conta: {e}")

def marcar_como_pago(call: ServiceCall) -> None:
    """Marca uma conta como paga."""
    conta_id = call.data.get("conta_id")
    if not conta_id:
        _LOGGER.error("ID da conta não fornecido")
        return

    hass = call.data.get("hass")
    db_path = hass.config.path(DB_NAME)
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE contas 
            SET pago = TRUE, data_pagamento = ?
            WHERE id = ?
        """, (datetime.now().strftime("%Y-%m-%d"), conta_id))
        conn.commit()
        conn.close()
        _LOGGER.info(f"Conta ID {conta_id} marcada como paga!")
    except Exception as e:
        _LOGGER.error(f"Erro ao marcar conta como paga: {e}")
