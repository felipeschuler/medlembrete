# language: pt

Funcionalidade: Definição do tipo de uso do medicamento

  Como paciente
  Quero definir se um medicamento é de uso contínuo ou temporário
  Para que o aplicativo saiba como tratar os lembretes e o histórico desse medicamento

  Cenário: Definir medicamento como uso contínuo
    Dado que Maria Souza está cadastrando o medicamento "Losartana"
    Quando Maria Souza define o tipo de uso como "Contínuo"
    Então o tipo de uso do medicamento "Losartana" deve ser "Contínuo"

  Cenário: Definir medicamento como uso temporário
    Dado que Maria Souza está cadastrando o medicamento "Amoxicilina"
    Quando Maria Souza define o tipo de uso como "Temporário"
    Então o tipo de uso do medicamento "Amoxicilina" deve ser "Temporário"

  Cenário: Editar o tipo de uso de um medicamento já cadastrado
    Dado que Maria Souza possui o medicamento "Amoxicilina" com tipo "Temporário"
    Quando Maria Souza edita o tipo de uso do medicamento "Amoxicilina" para "Contínuo"
    Então o tipo de uso do medicamento "Amoxicilina" deve ser "Contínuo"

  Cenário: Tentar definir um tipo de uso inválido
    Dado que Maria Souza está cadastrando o medicamento "Amoxicilina"
    Quando Maria Souza tenta definir o tipo de uso como "Esporádico"
    Então o tipo de uso do medicamento "Amoxicilina" não deve ser definido
    E a mensagem "Tipo de uso inválido" deve ser exibida
