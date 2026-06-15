"""Steps para features/cadastro_medicamento.feature (PB03)."""

from behave import given, when, then

from src.models import Medicamento, NomeObrigatorioError
from features.steps.steps_comuns import tabela_para_dicionario


@given('que existe um usuário chamado "{nome}"')
def step_existe_usuario_chamado(context, nome):
    usuario = context.sistema.buscar_usuario_por_nome(nome)
    if usuario is None:
        email = f"{nome.lower().replace(' ', '.')}@email.com"
        usuario = context.sistema.cadastrar_usuario(
            nome=nome, email=email, telefone="71999999999"
        )
    context.usuario_atual = usuario


@when('{nome} cadastra o medicamento:')
def step_cadastra_medicamento(context, nome):
    dados = tabela_para_dicionario(context.table)

    context.erro = None
    try:
        medicamento = Medicamento(
            nome=dados.get("Nome"),
            dosagem=dados.get("Dosagem"),
            tipo=dados.get("Tipo"),
        )
        context.usuario_atual.adicionar_medicamento(medicamento)
        context.medicamento_atual = medicamento
    except NomeObrigatorioError as exc:
        context.erro = exc
        context.mensagem_exibida = str(exc)
        context.medicamento_atual = None


@then('o medicamento "{nome_medicamento}" deve ser associado a {nome_usuario}')
def step_medicamento_associado(context, nome_medicamento, nome_usuario):
    usuario = context.sistema.buscar_usuario_por_nome(nome_usuario)
    medicamento = usuario.buscar_medicamento(nome_medicamento)
    assert medicamento is not None, (
        f"Medicamento '{nome_medicamento}' não associado a {nome_usuario}"
    )
    assert medicamento.usuario is usuario


@then('sua dosagem deve ser registrada como "{dosagem}"')
def step_dosagem_registrada(context, dosagem):
    assert context.medicamento_atual.dosagem == dosagem


@when('{nome} tenta cadastrar um medicamento sem informar o nome')
def step_tenta_cadastrar_sem_nome(context, nome):
    context.erro = None
    try:
        medicamento = Medicamento(nome=None)
        context.usuario_atual.adicionar_medicamento(medicamento)
        context.medicamento_atual = medicamento
    except NomeObrigatorioError as exc:
        context.erro = exc
        context.mensagem_exibida = str(exc)
        context.medicamento_atual = None


@then('o medicamento não deve ser cadastrado')
def step_medicamento_nao_cadastrado(context):
    assert context.erro is not None, "Esperava um erro de validação"
    assert context.medicamento_atual is None
    assert context.usuario_atual.medicamentos == []
