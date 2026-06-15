# language: pt

Funcionalidade: Cadastro de medicamento

  Como paciente
  Quero cadastrar um medicamento
  Para que eu possa receber lembretes de uso

  Cenário: Cadastro de medicamento com sucesso
    Dado que existe um usuário chamado "Maria Souza"
    Quando Maria Souza cadastra o medicamento:
      | Nome    | Amoxicilina |
      | Dosagem | 500 mg      |
      | Tipo    | Temporário  |
    Então o medicamento "Amoxicilina" deve ser associado a Maria Souza
    E sua dosagem deve ser registrada como "500 mg"

  Cenário: Cadastro de medicamento sem informar o nome
    Dado que existe um usuário chamado "Maria Souza"
    Quando Maria Souza tenta cadastrar um medicamento sem informar o nome
    Então o medicamento não deve ser cadastrado
    E a mensagem "Nome do medicamento é obrigatório" deve ser exibida
