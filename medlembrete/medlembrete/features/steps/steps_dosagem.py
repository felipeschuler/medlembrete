"""Steps para features/configuracao_dosagem.feature (PB06)."""

from behave import given, when, then

from src.models import DosagemObrigatoriaError, Medicamento


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


@given('que {nome} está cadastrando o medicamento "{nome_medicamento}"')
def step_usuario_cadastrando_medicamento(context, nome, nome_medicamento):
    usuario = _obter_ou_criar_usuario(context, nome)
    medicamento = _obter_ou_criar_medicamento(usuario, nome_medicamento)
    context.usuario_atual = usuario
    context.medicamento_atual = medicamento


@when('{nome} define a dosagem como "{dosagem}"')
def step_define_dosagem(context, nome, dosagem):
    context.erro = None
    try:
        context.medicamento_atual.configurar_dosagem(dosagem)
    except DosagemObrigatoriaError as exc:
        context.erro = exc
        context.mensagem_exibida = str(exc)


@then('a dosagem do medicamento "{nome_medicamento}" deve ser "{dosagem}"')
def step_dosagem_deve_ser(context, nome_medicamento, dosagem):
    medicamento = context.usuario_atual.buscar_medicamento(nome_medicamento)
    assert medicamento.dosagem == dosagem, (
        f"Esperava dosagem '{dosagem}', encontrei '{medicamento.dosagem}'"
    )


@given('que {nome} possui o medicamento "{nome_medicamento}" com dosagem "{dosagem}"')
def step_possui_medicamento_com_dosagem(context, nome, nome_medicamento, dosagem):
    usuario = _obter_ou_criar_usuario(context, nome)
    medicamento = _obter_ou_criar_medicamento(
        usuario, nome_medicamento, dosagem=dosagem, tipo="Temporário"
    )
    medicamento.dosagem = dosagem
    context.usuario_atual = usuario
    context.medicamento_atual = medicamento


@when('{nome} edita a dosagem do medicamento "{nome_medicamento}" para "{dosagem}"')
def step_edita_dosagem(context, nome, nome_medicamento, dosagem):
    medicamento = context.usuario_atual.buscar_medicamento(nome_medicamento)
    context.erro = None
    try:
        medicamento.configurar_dosagem(dosagem)
    except DosagemObrigatoriaError as exc:
        context.erro = exc
        context.mensagem_exibida = str(exc)


@when('{nome} tenta editar a dosagem do medicamento "{nome_medicamento}" para ""')
def step_tenta_editar_dosagem_vazia(context, nome, nome_medicamento):
    medicamento = context.usuario_atual.buscar_medicamento(nome_medicamento)
    context.erro = None
    try:
        medicamento.configurar_dosagem("")
    except DosagemObrigatoriaError as exc:
        context.erro = exc
        context.mensagem_exibida = str(exc)


@then('a dosagem do medicamento "{nome_medicamento}" deve continuar "{dosagem}"')
def step_dosagem_deve_continuar(context, nome_medicamento, dosagem):
    assert context.erro is not None, "Esperava um erro de validação de dosagem"
    medicamento = context.usuario_atual.buscar_medicamento(nome_medicamento)
    assert medicamento.dosagem == dosagem
