"""Steps para features/configuracao_horario.feature (PB07)."""

from behave import given, when, then

from src.models import Medicamento, HorarioInvalidoError


def _obter_ou_criar_usuario(context, nome):
    usuario = context.sistema.buscar_usuario_por_nome(nome)
    if usuario is None:
        email = f"{nome.lower().replace(' ', '.')}@email.com"
        usuario = context.sistema.cadastrar_usuario(
            nome=nome, email=email, telefone="71999999999"
        )
    return usuario


@given('que {nome} possui o medicamento "{nome_medicamento}" cadastrado')
def step_usuario_possui_medicamento_cadastrado(context, nome, nome_medicamento):
    usuario = _obter_ou_criar_usuario(context, nome)

    medicamento = usuario.buscar_medicamento(nome_medicamento)
    if medicamento is None:
        medicamento = Medicamento(
            nome=nome_medicamento, dosagem="500 mg", tipo="Temporário"
        )
        usuario.adicionar_medicamento(medicamento)

    context.usuario_atual = usuario
    context.medicamento_atual = medicamento


@when(
    '{nome} configura os horários "{horario1}" e "{horario2}" '
    'para o medicamento "{nome_medicamento}"'
)
def step_configura_horarios(context, nome, horario1, horario2, nome_medicamento):
    medicamento = context.usuario_atual.buscar_medicamento(nome_medicamento)
    context.erro = None
    try:
        medicamento.configurar_horario(horario1)
        medicamento.configurar_horario(horario2)
    except HorarioInvalidoError as exc:
        context.erro = exc
        context.mensagem_exibida = str(exc)


@then(
    'os horários "{horario1}" e "{horario2}" devem ficar registrados '
    'para o medicamento'
)
def step_horarios_registrados(context, horario1, horario2):
    horarios = context.medicamento_atual.horarios
    assert horario1 in horarios, f"Horário {horario1} não registrado"
    assert horario2 in horarios, f"Horário {horario2} não registrado"


@when('{nome} informa o horário "{horario}"')
def step_informa_horario(context, nome, horario):
    context.erro = None
    try:
        context.medicamento_atual.configurar_horario(horario)
    except HorarioInvalidoError as exc:
        context.erro = exc
        context.mensagem_exibida = str(exc)
        context.horario_tentado = horario


@then('o horário não deve ser registrado')
def step_horario_nao_registrado(context):
    assert context.erro is not None, "Esperava um erro de horário inválido"
    assert context.horario_tentado not in context.medicamento_atual.horarios
