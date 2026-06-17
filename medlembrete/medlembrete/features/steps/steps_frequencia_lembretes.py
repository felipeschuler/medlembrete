"""Steps para features/frequencia_lembretes.feature (PB13)."""

from datetime import date, datetime

from behave import given, when, then


def _combinar(horario_str):
    hora, minuto = horario_str.split(":")
    return datetime.combine(
        date.today(), datetime.min.time().replace(hour=int(hora), minute=int(minuto))
    )


@given('{nome} não confirmou o uso do medicamento "{nome_medicamento}" das {horario}')
def step_nao_confirmou_uso(context, nome, nome_medicamento, horario):
    medicamento = context.usuario_atual.buscar_medicamento(nome_medicamento)
    agendamento = context.servico_notificacao.obter_ou_criar_agendamento(
        medicamento, horario, date.today()
    )
    assert agendamento.status != "Tomado"
    # Acumula todas as notificações recebidas ao longo do cenário,
    # já que vários "Quando" são executados em sequência.
    context.notificacoes_acumuladas = []


@when('o sistema verificar os medicamentos agendados às {horario}')
def step_sistema_verifica_as(context, horario):
    data_hora = _combinar(horario)
    novas = context.servico_notificacao.verificar_medicamentos_agendados(
        context.sistema, data_hora
    )
    context.notificacoes = novas
    if not hasattr(context, "notificacoes_acumuladas"):
        context.notificacoes_acumuladas = []
    context.notificacoes_acumuladas.extend(novas)
    context.ultimo_horario_verificado = horario


@when('{nome} confirma às {horario_confirmacao} que tomou o medicamento "{nome_medicamento}" das {horario}')
def step_confirma_as(context, nome, horario_confirmacao, nome_medicamento, horario):
    medicamento = context.usuario_atual.buscar_medicamento(nome_medicamento)
    agendamento = context.servico_notificacao.obter_ou_criar_agendamento(
        medicamento, horario, date.today()
    )
    agendamento.confirmar(horario_confirmacao)


@then('{quantidade:d} notificações devem ter sido enviadas para {nome} sobre o medicamento "{nome_medicamento}" das {horario}')
def step_n_notificacoes_enviadas(context, quantidade, nome, nome_medicamento, horario):
    relevantes = [
        n for n in context.notificacoes_acumuladas
        if n.usuario.nome == nome and nome_medicamento in n.mensagem
    ]
    assert len(relevantes) == quantidade, (
        f"Esperava {quantidade} notificações, obtive {len(relevantes)}"
    )


@then('nenhuma notificação deve ser enviada às {horario} para o medicamento "{nome_medicamento}" das {horario_original}')
def step_nenhuma_notificacao_as(context, horario, nome_medicamento, horario_original):
    assert context.ultimo_horario_verificado == horario
    assert context.notificacoes == [], (
        f"Esperava nenhuma notificação às {horario}, obtive {context.notificacoes}"
    )
