# language: pt

Funcionalidade: Configuração de horário de administração

  Como paciente
  Quero configurar os horários de administração do medicamento
  Para que eu receba lembretes no momento correto

  Cenário: Definir horário para um medicamento
    Dado que Maria Souza possui o medicamento "Amoxicilina" cadastrado
    Quando Maria Souza configura os horários "08:00" e "20:00" para o medicamento "Amoxicilina"
    Então os horários "08:00" e "20:00" devem ficar registrados para o medicamento

  Cenário: Tentar cadastrar horário inválido
    Dado que Maria Souza possui o medicamento "Amoxicilina" cadastrado
    Quando Maria Souza informa o horário "25:30"
    Então o horário não deve ser registrado
    E a mensagem "Horário inválido" deve ser exibida
