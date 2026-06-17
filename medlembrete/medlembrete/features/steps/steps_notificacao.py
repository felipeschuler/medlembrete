"""Steps para features/notificacao_medicamento.feature (PB12)."""

from datetime import date, datetime

from behave import given, when, then

from src.models import Medicamento


def _obter_ou_criar_usuario(context, nome):
    usuario = context.sistema.buscar_usuario_por_nome(nome)
    if usuario is None:
        email = f"{nome.lower().replace(' ', '.')}@email.com"
        usuario = context.sistema.cadastrar_usuario(
            nome=nome, email=email, telefone="71999999999"
        )
    return usuario


@given('que {nome} possui o medicamento "{nome_medicamento}" configurado para as {horario}')
def step_usuario_possui_medicamento_configurado(context, nome, nome_medicamento, horario):
    usuario = _obter_ou_criar_usuario(context, nome)

    medicamento = usuario.buscar_medicamento(nome_medicamento)
    if medicamento is None:
        medicamento = Medicamento(
            nome=nome_medicamento, dosagem="500 mg", tipo="Temporário"
        )
        usuario.adicionar_medicamento(medicamento)

    medicamento.configurar_horario(horario)

    context.usuario_atual = usuario
    context.medicamento_atual = medicamento


@given('a data é {data}')
def step_a_data_e(context, data):
    context.data_simulada = datetime.strptime(data, "%d/%m/%Y").date()


@given('o horário atual é {horario}')
def step_horario_atual_e(context, horario):
    context.horario_simulado = horario


@when('o sistema verificar os medicamentos agendados')
def step_sistema_verifica_agendados(context):
    data_referencia = context.data_simulada or date.today()
    hora, minuto = context.horario_simulado.split(":")
    data_hora = datetime.combine(
        data_referencia, datetime.min.time().replace(hour=int(hora), minute=int(minuto))
    )
    context.notificacoes = context.servico_notificacao.verificar_medicamentos_agendados(
        context.sistema, data_hora
    )


@then('uma notificação deve ser enviada para {nome}')
def step_notificacao_enviada_para(context, nome):
    enviadas = [n for n in context.notificacoes if n.usuario.nome == nome]
    assert enviadas, f"Nenhuma notificação foi enviada para {nome}"


@then('a notificação deve conter a mensagem "{mensagem}"')
def step_notificacao_contem_mensagem(context, mensagem):
    mensagens = [n.mensagem for n in context.notificacoes]
    assert mensagem in mensagens, (
        f"Mensagem '{mensagem}' não encontrada em {mensagens}"
    )


@then('nenhuma notificação deve ser enviada')
def step_nenhuma_notificacao_enviada(context):
    assert context.notificacoes == [], (
        f"Esperava nenhuma notificação, mas foram enviadas: {context.notificacoes}"
    )
