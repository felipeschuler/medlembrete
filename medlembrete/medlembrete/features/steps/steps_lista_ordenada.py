"""Steps para features/lista_medicamentos_ordenada.feature (PB10)."""

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


@given('que {nome} possui os seguintes medicamentos e horários:')
def step_possui_medicamentos_e_horarios(context, nome):
    usuario = _obter_ou_criar_usuario(context, nome)
    context.usuario_atual = usuario

    for row in context.table:
        nome_medicamento = row["Medicamento"].strip()
        horarios_str = row["Horários"].strip()

        medicamento = usuario.buscar_medicamento(nome_medicamento)
        if medicamento is None:
            medicamento = Medicamento(
                nome=nome_medicamento, dosagem="—", tipo="Contínuo"
            )
            usuario.adicionar_medicamento(medicamento)

        for horario in [h.strip() for h in horarios_str.split(",") if h.strip()]:
            medicamento.configurar_horario(horario)


@when('{nome} visualiza a lista de medicamentos às {horario}')
def step_visualiza_lista_as(context, nome, horario):
    usuario = context.usuario_atual
    context.lista_ordenada = sorted(
        usuario.medicamentos,
        key=lambda m: m.chave_ordenacao_proximo_horario(horario),
    )


@then('a lista deve apresentar os medicamentos na seguinte ordem:')
def step_lista_na_ordem(context):
    # A primeira linha da tabela do Gherkin é tratada pelo Behave como
    # "cabeçalho" (table.headings) — como aqui não há cabeçalho de fato,
    # incluímos esse valor como o primeiro item esperado.
    nomes_esperados = [context.table.headings[0].strip()] + [
        row[0].strip() for row in context.table.rows
    ]
    nomes_obtidos = [m.nome for m in context.lista_ordenada]
    assert nomes_obtidos == nomes_esperados, (
        f"Esperava ordem {nomes_esperados}, obtive {nomes_obtidos}"
    )
