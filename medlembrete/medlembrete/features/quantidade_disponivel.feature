# language: pt

Funcionalidade: Configuração da quantidade inicial disponível do medicamento

  Como paciente
  Quero configurar e atualizar a quantidade disponível do meu medicamento
  Para saber quando preciso repor o estoque

  Cenário: Configurar quantidade inicial ao cadastrar o medicamento
    Dado que Maria Souza está cadastrando o medicamento "Amoxicilina"
    Quando Maria Souza define a quantidade inicial disponível como 20
    Então a quantidade disponível do medicamento "Amoxicilina" deve ser 20

  Cenário: Editar a quantidade disponível de um medicamento já cadastrado
    Dado que Maria Souza possui o medicamento "Amoxicilina" com quantidade disponível 20
    Quando Maria Souza edita a quantidade disponível do medicamento "Amoxicilina" para 15
    Então a quantidade disponível do medicamento "Amoxicilina" deve ser 15

  Cenário: Tentar configurar quantidade negativa
    Dado que Maria Souza possui o medicamento "Amoxicilina" com quantidade disponível 20
    Quando Maria Souza tenta editar a quantidade disponível do medicamento "Amoxicilina" para -5
    Então a quantidade disponível do medicamento "Amoxicilina" deve continuar 20
    E a mensagem "Quantidade não pode ser negativa" deve ser exibida

  Cenário: Quantidade é reduzida automaticamente após confirmação de uso
    Dado que Maria Souza possui o medicamento "Amoxicilina" com quantidade disponível 20
      E o medicamento "Amoxicilina" está agendado para as 08:00
    Quando Maria Souza confirma que tomou o medicamento "Amoxicilina" das 08:00
    Então a quantidade disponível do medicamento "Amoxicilina" deve ser 19
