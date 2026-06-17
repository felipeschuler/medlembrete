# language: pt

Funcionalidade: Visualização da lista de medicamentos ordenada pelo próximo horário de uso

  Como paciente
  Quero ver meus medicamentos ordenados pelo próximo horário em que devem ser tomados
  Para saber rapidamente qual remédio tomar primeiro

  Cenário: Listar medicamentos ordenados a partir do horário atual
    Dado que Maria Souza possui os seguintes medicamentos e horários:
      | Medicamento  | Horários       |
      | Vitamina D   | 09:00          |
      | Amoxicilina  | 08:00, 20:00   |
      | Losartana    | 07:00, 19:00   |
    Quando Maria Souza visualiza a lista de medicamentos às 10:00
    Então a lista deve apresentar os medicamentos na seguinte ordem:
      | Losartana    |
      | Amoxicilina  |
      | Vitamina D   |

  Cenário: Medicamentos com todos os horários do dia já passados aparecem por último
    Dado que Maria Souza possui os seguintes medicamentos e horários:
      | Medicamento  | Horários |
      | Vitamina D   | 09:00    |
      | Amoxicilina  | 08:00    |
    Quando Maria Souza visualiza a lista de medicamentos às 23:00
    Então a lista deve apresentar os medicamentos na seguinte ordem:
      | Vitamina D   |
      | Amoxicilina  |
