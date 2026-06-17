"""Steps para features/registro_administracao.feature (PB14)."""

from datetime import date

from behave import given, when, then

from src.models import Agendamento, Medicamento


def _obter_ou_criar_usuario(context, nome):
    usuario = context.sistema.buscar_usuario_por_nome(nome)
    if usuario is None:
        email = f"{nome.lower().replace(' ', '.')}@email.com"
        usuario = context.sistema.cadastrar_usuario(
            nome=nome, email=email, telefone="71999999999"
        )
    return usuario


@given('que {nome} possui o medicamento "{nome_medicamento}" agendado para as {horario}')
def step_usuario_possui_medicamento_agendado(context, nome, nome_medicamento, horario):
    usuario = _obter_ou_criar_usuario(context, nome)

    medicamento = usuario.buscar_medicamento(nome_medicamento)
    if medicamento is None:
        medicamento = Medicamento(
            nome=nome_medicamento, dosagem="500 mg", tipo="Temporário"
        )
        usuario.adicionar_medicamento(medicamento)

    if horario not in medicamento.horarios:
        medicamento.configurar_horario(horario)

    agendamento = Agendamento(medicamento, horario, date.today())
    medicamento.agendamentos.append(agendamento)

    context.usuario_atual = usuario
    context.medicamento_atual = medicamento
    context.agendamento_atual = agendamento


@given('recebeu uma notificação às {horario}')
def step_recebeu_notificacao(context, horario):
    assert context.agendamento_atual.horario == horario
    context.agendamento_atual.notificado = True


@when('{nome} confirma às {horario_confirmacao} que tomou o medicamento')
def step_confirma_administracao(context, nome, horario_confirmacao):
    context.agendamento_atual.confirmar(horario_confirmacao)


@then('o medicamento deve ser registrado como tomado')
def step_medicamento_registrado_tomado(context):
    assert context.agendamento_atual.status == Agendamento.TOMADO


@then('o horário da administração deve ser salvo como {horario}')
def step_horario_administracao_salvo(context, horario):
    assert context.agendamento_atual.horario_confirmacao == horario


@then('nenhum novo lembrete deve ser enviado para esse horário')
def step_nenhum_novo_lembrete(context):
    notificacoes_antes = len(context.notificacoes)

    from datetime import datetime

    horario = context.agendamento_atual.horario
    hora, minuto = horario.split(":")
    data_hora = datetime.combine(
        date.today(), datetime.min.time().replace(hour=int(hora), minute=int(minuto))
    )

    novas = context.servico_notificacao.verificar_medicamentos_agendados(
        context.sistema, data_hora
    )

    assert len(novas) == 0, (
        "Não deveria haver novo lembrete para um horário já confirmado"
    )
    assert notificacoes_antes == len(context.notificacoes)


@when('o horário atual for {horario}')
def step_horario_atual_for(context, horario):
    context.horario_simulado = horario


@when('{nome} não tiver confirmado a administração')
def step_nao_confirmou_administracao(context, nome):
    assert context.agendamento_atual.status == Agendamento.PENDENTE


@then('o medicamento deve permanecer com status "{status}"')
def step_medicamento_permanece_status(context, status):
    assert context.agendamento_atual.status == status
