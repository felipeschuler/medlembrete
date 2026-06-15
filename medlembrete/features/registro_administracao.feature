# language: pt

Funcionalidade: Registro de administração de medicamento

  Como paciente
  Quero registrar que tomei meu medicamento
  Para acompanhar meu tratamento e evitar lembretes desnecessários

  Cenário: Confirmar administração de medicamento
    Dado que Maria Souza possui o medicamento "Amoxicilina" agendado para as 08:00
    E recebeu uma notificação às 08:00
    Quando Maria Souza confirma às 08:05 que tomou o medicamento
    Então o medicamento deve ser registrado como tomado
    E o horário da administração deve ser salvo como 08:05
    E nenhum novo lembrete deve ser enviado para esse horário

  Cenário: Medicamento ainda não confirmado
    Dado que Maria Souza possui o medicamento "Amoxicilina" agendado para as 08:00
    Quando o horário atual for 08:30
    E Maria Souza não tiver confirmado a administração
    Então o medicamento deve permanecer com status "Pendente"
