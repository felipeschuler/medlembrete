# language: pt

Funcionalidade: Frequência dos lembretes após atraso na confirmação

  Como paciente
  Quero receber lembretes repetidos de 10 em 10 minutos quando eu não confirmar o uso do remédio
  Para não esquecer de tomar o medicamento mesmo se eu perder a primeira notificação

  Cenário: Primeiro lembrete extra 10 minutos após o horário programado
    Dado que Maria Souza possui o medicamento "Amoxicilina" configurado para as 16:00
      E Maria Souza não confirmou o uso do medicamento "Amoxicilina" das 16:00
    Quando o sistema verificar os medicamentos agendados às 16:10
    Então uma notificação deve ser enviada para Maria Souza
      E a notificação deve conter a mensagem "Hora de tomar Amoxicilina (500 mg)"

  Cenário: Lembretes extras continuam de 10 em 10 minutos até o limite de 3 vezes
    Dado que Maria Souza possui o medicamento "Amoxicilina" configurado para as 16:00
      E Maria Souza não confirmou o uso do medicamento "Amoxicilina" das 16:00
    Quando o sistema verificar os medicamentos agendados às 16:00
      E o sistema verificar os medicamentos agendados às 16:10
      E o sistema verificar os medicamentos agendados às 16:20
      E o sistema verificar os medicamentos agendados às 16:30
    Então 4 notificações devem ter sido enviadas para Maria Souza sobre o medicamento "Amoxicilina" das 16:00

  Cenário: Lembretes extras param após o limite de 3 tentativas
    Dado que Maria Souza possui o medicamento "Amoxicilina" configurado para as 16:00
      E Maria Souza não confirmou o uso do medicamento "Amoxicilina" das 16:00
    Quando o sistema verificar os medicamentos agendados às 16:00
      E o sistema verificar os medicamentos agendados às 16:10
      E o sistema verificar os medicamentos agendados às 16:20
      E o sistema verificar os medicamentos agendados às 16:30
      E o sistema verificar os medicamentos agendados às 16:40
    Então nenhuma notificação deve ser enviada às 16:40 para o medicamento "Amoxicilina" das 16:00

  Cenário: Lembretes extras param quando o medicamento é confirmado
    Dado que Maria Souza possui o medicamento "Amoxicilina" configurado para as 16:00
      E Maria Souza não confirmou o uso do medicamento "Amoxicilina" das 16:00
    Quando o sistema verificar os medicamentos agendados às 16:00
      E o sistema verificar os medicamentos agendados às 16:10
      E Maria Souza confirma às 16:12 que tomou o medicamento "Amoxicilina" das 16:00
      E o sistema verificar os medicamentos agendados às 16:20
    Então nenhuma notificação deve ser enviada às 16:20 para o medicamento "Amoxicilina" das 16:00
