# language: pt

Funcionalidade: Notificação para tomar medicamento

  Como paciente
  Quero receber notificações nos horários configurados
  Para que eu não esqueça de tomar meus medicamentos

  Cenário: Receber notificação no horário programado
    Dado que Maria Souza possui o medicamento "Amoxicilina" configurado para as 08:00
    E a data é 03/06/2026
    E o horário atual é 08:00
    Quando o sistema verificar os medicamentos agendados
    Então uma notificação deve ser enviada para Maria Souza
    E a notificação deve conter a mensagem "Hora de tomar Amoxicilina (500 mg)"

  Cenário: Não receber notificação fora do horário programado
    Dado que Maria Souza possui o medicamento "Amoxicilina" configurado para as 08:00
    E o horário atual é 07:30
    Quando o sistema verificar os medicamentos agendados
    Então nenhuma notificação deve ser enviada
