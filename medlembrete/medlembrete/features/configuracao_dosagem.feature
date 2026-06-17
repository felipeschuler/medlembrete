# language: pt

Funcionalidade: Configuração de dosagem do medicamento

  Como paciente
  Quero configurar e editar a dosagem do meu medicamento
  Para manter o tratamento correto ao longo do tempo

  Cenário: Configurar dosagem ao cadastrar o medicamento
    Dado que Maria Souza está cadastrando o medicamento "Amoxicilina"
    Quando Maria Souza define a dosagem como "500 mg"
    Então a dosagem do medicamento "Amoxicilina" deve ser "500 mg"

  Cenário: Editar a dosagem de um medicamento já cadastrado
    Dado que Maria Souza possui o medicamento "Amoxicilina" com dosagem "500 mg"
    Quando Maria Souza edita a dosagem do medicamento "Amoxicilina" para "250 mg"
    Então a dosagem do medicamento "Amoxicilina" deve ser "250 mg"

  Cenário: Tentar configurar dosagem vazia
    Dado que Maria Souza possui o medicamento "Amoxicilina" com dosagem "500 mg"
    Quando Maria Souza tenta editar a dosagem do medicamento "Amoxicilina" para ""
    Então a dosagem do medicamento "Amoxicilina" deve continuar "500 mg"
    E a mensagem "Dosagem é obrigatória" deve ser exibida
