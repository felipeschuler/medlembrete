"""Steps compartilhados entre as diferentes features."""

from behave import then


@then('a mensagem "{mensagem}" deve ser exibida')
def step_mensagem_exibida(context, mensagem):
    assert context.mensagem_exibida == mensagem, (
        f"Esperava a mensagem '{mensagem}', "
        f"mas foi exibida '{context.mensagem_exibida}'"
    )


def tabela_para_dicionario(table):
    """Converte uma tabela vertical (label | valor) do Gherkin em dict.

    O Behave trata a primeira linha da tabela como cabeçalho. Como nossas
    tabelas são do tipo "label | valor" (sem cabeçalho de fato), incluímos
    também a linha de cabeçalho como um par chave/valor.
    """
    dados = {table.headings[0]: table.headings[1]}
    for row in table.rows:
        dados[row[0]] = row[1]
    return dados
