"""Steps para features/quantidade_disponivel.feature (PB09)."""

from datetime import date

from behave import given, when, then

from src.models import Medicamento, QuantidadeNegativaError


def _obter_ou_criar_usuario(context, nome):
    usuario = context.sistema.buscar_usuario_por_nome(nome)
    if usuario is None:
        email = f"{nome.lower().replace(' ', '.')}@email.com"
        usuario = context.sistema.cadastrar_usuario(
            nome=nome, email=email, telefone="71999999999"
        )
    return usuario


def _obter_ou_criar_medicamento(usuario, nome_medicamento, **kwargs):
    medicamento = usuario.buscar_medicamento(nome_medicamento)
    if medicamento is None:
        medicamento = Medicamento(nome=nome_medicamento, **kwargs)
        usuario.adicionar_medicamento(medicamento)
    return medicamento


@when('{nome} define a quantidade inicial disponível como {quantidade:d}')
def step_define_quantidade(context, nome, quantidade):
    context.erro = None
    try:
        context.medicamento_atual.configurar_quantidade_disponivel(quantidade)
    except QuantidadeNegativaError as exc:
        context.erro = exc
        context.mensagem_exibida = str(exc)


@then('a quantidade disponível do medicamento "{nome_medicamento}" deve ser {quantidade:d}')
def step_quantidade_deve_ser(context, nome_medicamento, quantidade):
    medicamento = context.usuario_atual.buscar_medicamento(nome_medicamento)
    assert medicamento.quantidade_disponivel == quantidade, (
        f"Esperava quantidade {quantidade}, encontrei {medicamento.quantidade_disponivel}"
    )


@given(
    'que {nome} possui o medicamento "{nome_medicamento}" '
    'com quantidade disponível {quantidade:d}'
)
def step_possui_medicamento_com_quantidade(context, nome, nome_medicamento, quantidade):
    usuario = _obter_ou_criar_usuario(context, nome)
    medicamento = _obter_ou_criar_medicamento(
        usuario,
        nome_medicamento,
        dosagem="500 mg",
        tipo="Temporário",
        quantidade_disponivel=quantidade,
    )
    medicamento.quantidade_disponivel = quantidade
    context.usuario_atual = usuario
    context.medicamento_atual = medicamento


@when(
    '{nome} edita a quantidade disponível do medicamento "{nome_medicamento}" '
    'para {quantidade:d}'
)
def step_edita_quantidade(context, nome, nome_medicamento, quantidade):
    medicamento = context.usuario_atual.buscar_medicamento(nome_medicamento)
    context.erro = None
    try:
        medicamento.configurar_quantidade_disponivel(quantidade)
    except QuantidadeNegativaError as exc:
        context.erro = exc
        context.mensagem_exibida = str(exc)


@when(
    '{nome} tenta editar a quantidade disponível do medicamento "{nome_medicamento}" '
    'para {quantidade:d}'
)
def step_tenta_editar_quantidade_negativa(context, nome, nome_medicamento, quantidade):
    medicamento = context.usuario_atual.buscar_medicamento(nome_medicamento)
    context.erro = None
    try:
        medicamento.configurar_quantidade_disponivel(quantidade)
    except QuantidadeNegativaError as exc:
        context.erro = exc
        context.mensagem_exibida = str(exc)


@then(
    'a quantidade disponível do medicamento "{nome_medicamento}" deve continuar {quantidade:d}'
)
def step_quantidade_deve_continuar(context, nome_medicamento, quantidade):
    assert context.erro is not None, "Esperava um erro de validação de quantidade"
    medicamento = context.usuario_atual.buscar_medicamento(nome_medicamento)
    assert medicamento.quantidade_disponivel == quantidade


@given('o medicamento "{nome_medicamento}" está agendado para as {horario}')
def step_medicamento_agendado_para(context, nome_medicamento, horario):
    medicamento = context.usuario_atual.buscar_medicamento(nome_medicamento)
    if horario not in medicamento.horarios:
        medicamento.configurar_horario(horario)
    context.servico_notificacao.obter_ou_criar_agendamento(
        medicamento, horario, date.today()
    )


@when('{nome} confirma que tomou o medicamento "{nome_medicamento}" das {horario}')
def step_confirma_que_tomou(context, nome, nome_medicamento, horario):
    medicamento = context.usuario_atual.buscar_medicamento(nome_medicamento)
    agendamento = context.servico_notificacao.obter_ou_criar_agendamento(
        medicamento, horario, date.today()
    )
    agendamento.confirmar(horario)
    if medicamento.quantidade_disponivel is not None and medicamento.quantidade_disponivel > 0:
        medicamento.quantidade_disponivel -= 1
