"""
Configuração do ambiente de testes do Behave.

- Garante que o pacote `src` (modelos de domínio) possa ser importado
  independentemente de onde o `behave` for executado.
- Recria o `SistemaCadastro` antes de cada cenário, garantindo isolamento
  entre os testes.
"""

import os
import sys

# Garante que a raiz do projeto está no sys.path para `import src...`
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from src.models import SistemaCadastro, ServicoNotificacao  # noqa: E402


def before_scenario(context, scenario):
    context.sistema = SistemaCadastro()
    context.servico_notificacao = ServicoNotificacao()

    # Estado auxiliar usado pelos steps
    context.usuario_atual = None
    context.medicamento_atual = None
    context.erro = None
    context.mensagem_exibida = None
    context.notificacoes = []
    context.data_simulada = None
    context.horario_simulado = None
