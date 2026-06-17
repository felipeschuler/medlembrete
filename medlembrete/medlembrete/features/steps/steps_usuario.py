"""Steps para features/cadastro_usuario.feature (PB01)."""

from behave import given, when, then

from src.models import EmailJaCadastradoError
from features.steps.steps_comuns import tabela_para_dicionario


@given('que não existe um usuário cadastrado com o e-mail "{email}"')
def step_email_nao_cadastrado(context, email):
    assert not context.sistema.email_existe(email)


@when('{nome} cadastra os seguintes dados:')
def step_cadastra_dados(context, nome):
    dados = tabela_para_dicionario(context.table)

    context.erro = None
    try:
        context.usuario_atual = context.sistema.cadastrar_usuario(
            nome=dados["Nome"],
            email=dados["E-mail"],
            telefone=dados["Telefone"],
        )
    except EmailJaCadastradoError as exc:
        context.erro = exc
        context.mensagem_exibida = str(exc)


@then('o usuário "{nome}" deve ser cadastrado')
def step_usuario_cadastrado(context, nome):
    usuario = context.sistema.buscar_usuario_por_nome(nome)
    assert usuario is not None, f"Usuário '{nome}' não foi cadastrado"


@then('o e-mail "{email}" deve ficar associado ao usuário')
def step_email_associado(context, email):
    usuario = context.sistema.usuarios_por_email.get(email)
    assert usuario is not None, f"Nenhum usuário associado ao e-mail '{email}'"


@given('que já existe um usuário cadastrado chamado "{nome}" com o e-mail "{email}"')
def step_usuario_existente_com_email(context, nome, email):
    context.usuario_atual = context.sistema.cadastrar_usuario(
        nome=nome, email=email, telefone="00000000000"
    )


@when('outra pessoa tenta se cadastrar utilizando o e-mail "{email}"')
def step_outra_pessoa_tenta_cadastrar(context, email):
    context.erro = None
    try:
        context.sistema.cadastrar_usuario(
            nome="Outra Pessoa", email=email, telefone="11111111111"
        )
    except EmailJaCadastradoError as exc:
        context.erro = exc
        context.mensagem_exibida = str(exc)


@then('nenhum novo usuário deve ser cadastrado')
def step_nenhum_novo_usuario(context):
    assert context.erro is not None, "Esperava um erro de cadastro duplicado"
    usuarios = context.sistema.listar_usuarios()
    assert len(usuarios) == 1, (
        f"Esperava 1 usuário cadastrado, mas há {len(usuarios)}"
    )
