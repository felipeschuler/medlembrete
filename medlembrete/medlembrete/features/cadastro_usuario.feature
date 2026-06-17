# language: pt

Funcionalidade: Cadastro de usuário

  Como paciente
  Quero cadastrar meus dados no aplicativo
  Para que eu possa utilizar o sistema de lembretes de medicamentos

  Cenário: Cadastro de usuário com dados válidos
    Dado que não existe um usuário cadastrado com o e-mail "maria.souza@email.com"
    Quando Maria Souza cadastra os seguintes dados:
      | Nome     | Maria Souza            |
      | E-mail   | maria.souza@email.com  |
      | Telefone | 71999999999            |
    Então o usuário "Maria Souza" deve ser cadastrado
    E o e-mail "maria.souza@email.com" deve ficar associado ao usuário

  Cenário: Cadastro de usuário com e-mail já utilizado
    Dado que já existe um usuário cadastrado chamado "Maria Souza" com o e-mail "maria.souza@email.com"
    Quando outra pessoa tenta se cadastrar utilizando o e-mail "maria.souza@email.com"
    Então nenhum novo usuário deve ser cadastrado
    E a mensagem "E-mail já cadastrado" deve ser exibida
