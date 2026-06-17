"""Steps para features/tipo_medicamento.feature (PB08)."""

from behave import given, when, then

from src.models import Medicamento, TipoInvalidoError


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


@when('{nome} define o tipo de uso como "{tipo}"')
def step_define_tipo(context, nome, tipo):
    context.erro = None
    try:
        context.medicamento_atual.configurar_tipo(tipo)
    except TipoInvalidoError as exc:
        context.erro = exc
        context.mensagem_exibida = str(exc)


@then('o tipo de uso do medicamento "{nome_medicamento}" deve ser "{tipo}"')
def step_tipo_deve_ser(context, nome_medicamento, tipo):
    medicamento = context.usuario_atual.buscar_medicamento(nome_medicamento)
    assert medicamento.tipo == tipo, (
        f"Esperava tipo '{tipo}', encontrei '{medicamento.tipo}'"
    )


@given('que {nome} possui o medicamento "{nome_medicamento}" com tipo "{tipo}"')
def step_possui_medicamento_com_tipo(context, nome, nome_medicamento, tipo):
    usuario = _obter_ou_criar_usuario(context, nome)
    medicamento = _obter_ou_criar_medicamento(
        usuario, nome_medicamento, dosagem="500 mg", tipo=tipo
    )
    medicamento.tipo = tipo
    context.usuario_atual = usuario
    context.medicamento_atual = medicamento


@when('{nome} edita o tipo de uso do medicamento "{nome_medicamento}" para "{tipo}"')
def step_edita_tipo(context, nome, nome_medicamento, tipo):
    medicamento = context.usuario_atual.buscar_medicamento(nome_medicamento)
    context.erro = None
    try:
        medicamento.configurar_tipo(tipo)
    except TipoInvalidoError as exc:
        context.erro = exc
        context.mensagem_exibida = str(exc)


@when('{nome} tenta definir o tipo de uso como "{tipo}"')
def step_tenta_definir_tipo_invalido(context, nome, tipo):
    context.erro = None
    try:
        context.medicamento_atual.configurar_tipo(tipo)
    except TipoInvalidoError as exc:
        context.erro = exc
        context.mensagem_exibida = str(exc)


@then('o tipo de uso do medicamento "{nome_medicamento}" não deve ser definido')
def step_tipo_nao_deve_ser_definido(context, nome_medicamento):
    assert context.erro is not None, "Esperava um erro de validação de tipo"
    medicamento = context.usuario_atual.buscar_medicamento(nome_medicamento)
    assert medicamento.tipo is None
