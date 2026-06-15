"""
Persistência local (arquivo JSON) para o MedLembrete.

Como o app deve funcionar sem internet (PB23), os dados são salvos em um
arquivo JSON simples na mesma pasta do programa — sem necessidade de
banco de dados externo ou conexão de rede.
"""

import json
import os
from datetime import date

from src.models import Agendamento, Medicamento, SistemaCadastro

NOME_ARQUIVO_PADRAO = "dados_medlembrete.json"


def _caminho_padrao():
    """Salva o arquivo na mesma pasta onde está o código do app."""
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_dir, NOME_ARQUIVO_PADRAO)


def sistema_para_dict(sistema: SistemaCadastro) -> dict:
    """Converte o estado do sistema em um dicionário serializável em JSON."""
    usuarios = []
    for usuario in sistema.listar_usuarios():
        medicamentos = []
        for med in usuario.medicamentos:
            agendamentos = [
                {
                    "horario": ag.horario,
                    "data": ag.data.isoformat(),
                    "status": ag.status,
                    "notificado": ag.notificado,
                    "horario_confirmacao": ag.horario_confirmacao,
                }
                for ag in med.agendamentos
            ]
            medicamentos.append(
                {
                    "nome": med.nome,
                    "dosagem": med.dosagem,
                    "tipo": med.tipo,
                    "quantidade_disponivel": med.quantidade_disponivel,
                    "horarios": med.horarios,
                    "agendamentos": agendamentos,
                }
            )

        usuarios.append(
            {
                "nome": usuario.nome,
                "email": usuario.email,
                "telefone": usuario.telefone,
                "medicamentos": medicamentos,
            }
        )

    return {"usuarios": usuarios}


def sistema_de_dict(dados: dict) -> SistemaCadastro:
    """Reconstrói um SistemaCadastro a partir de um dicionário (JSON carregado)."""
    sistema = SistemaCadastro()

    for usuario_dict in dados.get("usuarios", []):
        usuario = sistema.cadastrar_usuario(
            nome=usuario_dict["nome"],
            email=usuario_dict["email"],
            telefone=usuario_dict.get("telefone", ""),
        )

        for med_dict in usuario_dict.get("medicamentos", []):
            medicamento = Medicamento(
                nome=med_dict["nome"],
                dosagem=med_dict.get("dosagem"),
                tipo=med_dict.get("tipo"),
                quantidade_disponivel=med_dict.get("quantidade_disponivel"),
            )
            usuario.adicionar_medicamento(medicamento)
            medicamento.horarios = list(med_dict.get("horarios", []))

            for ag_dict in med_dict.get("agendamentos", []):
                agendamento = Agendamento(
                    medicamento,
                    ag_dict["horario"],
                    date.fromisoformat(ag_dict["data"]),
                )
                agendamento.status = ag_dict.get("status", Agendamento.PENDENTE)
                agendamento.notificado = ag_dict.get("notificado", False)
                agendamento.horario_confirmacao = ag_dict.get("horario_confirmacao")
                medicamento.agendamentos.append(agendamento)

    return sistema


def salvar_dados(sistema: SistemaCadastro, caminho: str = None) -> None:
    """Salva o estado atual do sistema em um arquivo JSON local."""
    caminho = caminho or _caminho_padrao()
    dados = sistema_para_dict(sistema)

    try:
        with open(caminho, "w", encoding="utf-8") as arquivo:
            json.dump(dados, arquivo, ensure_ascii=False, indent=2)
    except OSError as exc:
        # Falha ao salvar não deve travar o app — apenas avisa no console.
        print(f"[MedLembrete] Não foi possível salvar os dados em '{caminho}': {exc}")


def carregar_dados(caminho: str = None) -> SistemaCadastro:
    """Carrega o sistema a partir do arquivo JSON local.

    Retorna um `SistemaCadastro` vazio se o arquivo não existir ou estiver
    corrompido (o app continua funcionando normalmente nesse caso).
    """
    caminho = caminho or _caminho_padrao()

    if not os.path.exists(caminho):
        return SistemaCadastro()

    try:
        with open(caminho, "r", encoding="utf-8") as arquivo:
            dados = json.load(arquivo)
        return sistema_de_dict(dados)
    except (OSError, json.JSONDecodeError, KeyError) as exc:
        print(f"[MedLembrete] Não foi possível carregar '{caminho}': {exc}")
        return SistemaCadastro()
