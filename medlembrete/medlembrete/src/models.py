"""
Modelos de domínio do MedLembrete.

Este módulo concentra toda a lógica de negócio do aplicativo,
de forma independente da interface (Streamlit) e dos testes (Behave).
"""

from datetime import date, datetime


# ---------------------------------------------------------------------------
# Exceções de domínio
# ---------------------------------------------------------------------------

class EmailJaCadastradoError(Exception):
    """Lançada ao tentar cadastrar um e-mail que já existe."""


class NomeObrigatorioError(Exception):
    """Lançada ao tentar cadastrar um medicamento sem nome."""


class HorarioInvalidoError(Exception):
    """Lançada ao tentar configurar um horário fora do padrão HH:MM."""


class DosagemObrigatoriaError(Exception):
    """Lançada ao tentar configurar uma dosagem vazia."""


class TipoInvalidoError(Exception):
    """Lançada ao tentar configurar um tipo de uso fora dos valores aceitos."""


class QuantidadeNegativaError(Exception):
    """Lançada ao tentar configurar uma quantidade disponível negativa."""


# ---------------------------------------------------------------------------
# Entidades
# ---------------------------------------------------------------------------

class Usuario:
    """Representa o paciente (usuário principal do app)."""

    def __init__(self, nome, email, telefone):
        self.nome = nome
        self.email = email
        self.telefone = telefone
        self.medicamentos = []
        self.responsaveis = []

    def adicionar_medicamento(self, medicamento):
        medicamento.usuario = self
        self.medicamentos.append(medicamento)
        return medicamento

    def buscar_medicamento(self, nome):
        for med in self.medicamentos:
            if med.nome == nome:
                return med
        return None


class Medicamento:
    """Representa um medicamento cadastrado por um usuário."""

    TIPOS_VALIDOS = ("Contínuo", "Temporário")

    def __init__(self, nome, dosagem=None, tipo=None, quantidade_disponivel=None):
        if not nome:
            raise NomeObrigatorioError("Nome do medicamento é obrigatório")

        self.nome = nome
        self.dosagem = dosagem
        self.tipo = tipo
        self.quantidade_disponivel = quantidade_disponivel
        self.usuario = None
        self.horarios = []        # lista de strings "HH:MM"
        self.agendamentos = []    # lista de Agendamento

    def configurar_horario(self, horario_str):
        if not self._horario_valido(horario_str):
            raise HorarioInvalidoError("Horário inválido")
        if horario_str not in self.horarios:
            self.horarios.append(horario_str)
            self.horarios.sort()
        return self.horarios

    def configurar_dosagem(self, dosagem):
        """Define ou edita a dosagem do medicamento (PB06)."""
        if not dosagem:
            raise DosagemObrigatoriaError("Dosagem é obrigatória")
        self.dosagem = dosagem
        return self.dosagem

    def configurar_tipo(self, tipo):
        """Define ou edita o tipo de uso do medicamento: Contínuo ou
        Temporário (PB08)."""
        if tipo not in Medicamento.TIPOS_VALIDOS:
            raise TipoInvalidoError("Tipo de uso inválido")
        self.tipo = tipo
        return self.tipo

    def configurar_quantidade_disponivel(self, quantidade):
        """Define ou edita a quantidade disponível do medicamento (PB09)."""
        if quantidade is not None and quantidade < 0:
            raise QuantidadeNegativaError("Quantidade não pode ser negativa")
        self.quantidade_disponivel = quantidade
        return self.quantidade_disponivel

    def proximo_horario(self, hora_atual):
        """Retorna o próximo horário (string "HH:MM") a partir de
        `hora_atual` (também "HH:MM") dentre os horários cadastrados.

        Se todos os horários do dia já tiverem passado, retorna o
        primeiro horário do dia (usado apenas para exibição).
        """
        if not self.horarios:
            return None

        proximos = [h for h in self.horarios if h >= hora_atual]
        if proximos:
            return min(proximos)

        return min(self.horarios)

    def horarios_do_dia_restantes(self, hora_atual):
        """True se ainda existir algum horário >= hora_atual hoje."""
        return any(h >= hora_atual for h in self.horarios)

    def chave_ordenacao_proximo_horario(self, hora_atual):
        """Chave de ordenação para PB10: medicamentos com algum horário
        ainda não passado hoje vêm primeiro (ordenados por esse horário).

        Medicamentos cujos horários já passaram todos vão para o final,
        ordenados entre si pelo horário mais recentemente vencido (o que
        está "mais atrasado" para ser tomado aparece primeiro dentro
        desse grupo).
        """
        if not self.horarios:
            return (2, "99:99")

        if self.horarios_do_dia_restantes(hora_atual):
            return (0, self.proximo_horario(hora_atual))

        # Todos os horários já passaram: o mais recente (mais próximo de
        # hora_atual) indica o medicamento mais atrasado, então vem antes.
        horario_mais_recente = max(self.horarios)
        chave_secundaria = self._inverter_horario(horario_mais_recente)
        return (1, chave_secundaria)

    @staticmethod
    def _inverter_horario(horario_str):
        """Converte HH:MM em uma chave que ordena do mais tarde para o
        mais cedo (usado para colocar o horário mais recente primeiro)."""
        hora, minuto = horario_str.split(":")
        minutos_totais = int(hora) * 60 + int(minuto)
        return 24 * 60 - minutos_totais

    @staticmethod
    def _horario_valido(horario_str):
        try:
            partes = horario_str.split(":")
            if len(partes) != 2:
                return False
            hora, minuto = int(partes[0]), int(partes[1])
            return 0 <= hora <= 23 and 0 <= minuto <= 59
        except (ValueError, AttributeError):
            return False


class Agendamento:
    """Representa a ocorrência de um medicamento em um horário/data específicos."""

    PENDENTE = "Pendente"
    TOMADO = "Tomado"

    def __init__(self, medicamento, horario, data):
        self.medicamento = medicamento
        self.horario = horario  # "HH:MM"
        self.data = data        # datetime.date
        self.status = Agendamento.PENDENTE
        self.notificado = False
        self.horario_confirmacao = None
        self.lembretes_extras_enviados = 0  # PB13: lembretes após o atraso

    def confirmar(self, horario_confirmacao):
        self.status = Agendamento.TOMADO
        self.horario_confirmacao = horario_confirmacao


class Notificacao:
    """Representa uma notificação a ser exibida/enviada para um usuário."""

    def __init__(self, usuario, mensagem):
        self.usuario = usuario
        self.mensagem = mensagem

    def __repr__(self):
        return f"Notificacao(usuario={self.usuario.nome!r}, mensagem={self.mensagem!r})"


# ---------------------------------------------------------------------------
# Sistema (camada de aplicação)
# ---------------------------------------------------------------------------

class SistemaCadastro:
    """Mantém o cadastro de usuários e expõe operações de alto nível."""

    def __init__(self):
        self.usuarios_por_email = {}

    # --- Usuários ---------------------------------------------------------
    def email_existe(self, email):
        return email in self.usuarios_por_email

    def cadastrar_usuario(self, nome, email, telefone):
        if self.email_existe(email):
            raise EmailJaCadastradoError("E-mail já cadastrado")
        usuario = Usuario(nome, email, telefone)
        self.usuarios_por_email[email] = usuario
        return usuario

    def buscar_usuario_por_nome(self, nome):
        for usuario in self.usuarios_por_email.values():
            if usuario.nome == nome:
                return usuario
        return None

    def listar_usuarios(self):
        return list(self.usuarios_por_email.values())


class ServicoNotificacao:
    """Responsável por verificar agendamentos e gerar notificações."""

    # PB13: configuração da frequência de lembretes após o horário programado
    INTERVALO_LEMBRETE_MINUTOS = 10
    MAXIMO_LEMBRETES_EXTRAS = 3

    def verificar_medicamentos_agendados(self, sistema, data_hora):
        """Verifica, para o instante `data_hora`, quais medicamentos devem
        gerar notificação e retorna a lista de `Notificacao` geradas.

        Cobre dois casos:
          - Notificação no horário exato programado (PB12).
          - Lembretes extras de 10 em 10 minutos, até 3 vezes, quando o
            medicamento não foi confirmado a tempo (PB13).

        Funciona inteiramente sobre dados em memória/local, sem nenhuma
        chamada de rede — o que garante o funcionamento mesmo sem acesso
        à internet (PB23).
        """
        notificacoes = []
        data_atual = data_hora.date()

        for usuario in sistema.listar_usuarios():
            for medicamento in usuario.medicamentos:
                for horario in medicamento.horarios:
                    agendamento = self._agendamento_relevante(
                        medicamento, horario, data_atual, data_hora
                    )
                    if agendamento is None:
                        continue

                    notificacao = self._avaliar_agendamento(
                        usuario, medicamento, agendamento, data_hora
                    )
                    if notificacao:
                        notificacoes.append(notificacao)

        return notificacoes

    def _agendamento_relevante(self, medicamento, horario, data_atual, data_hora):
        """Retorna o Agendamento de `horario`/`data_atual` apenas se
        `data_hora` já tiver alcançado esse horário programado (ou algum
        dos instantes de lembrete extra derivados dele)."""
        hora_agendamento = self._combinar(data_atual, horario)
        if data_hora < hora_agendamento:
            return None

        return self.obter_ou_criar_agendamento(medicamento, horario, data_atual)

    def _avaliar_agendamento(self, usuario, medicamento, agendamento, data_hora):
        if agendamento.status == Agendamento.TOMADO:
            return None

        hora_agendamento = self._combinar(agendamento.data, agendamento.horario)
        minutos_passados = (data_hora - hora_agendamento).total_seconds() / 60

        # Notificação no horário exato (PB12): minutos_passados == 0
        if minutos_passados == 0 and not agendamento.notificado:
            agendamento.notificado = True
            return self._criar_notificacao(usuario, medicamento)

        # Lembretes extras de 10 em 10 minutos, até o máximo (PB13)
        if minutos_passados > 0:
            numero_lembrete = int(minutos_passados // self.INTERVALO_LEMBRETE_MINUTOS)
            dentro_do_intervalo = minutos_passados % self.INTERVALO_LEMBRETE_MINUTOS == 0

            if (
                dentro_do_intervalo
                and 1 <= numero_lembrete <= self.MAXIMO_LEMBRETES_EXTRAS
                and agendamento.lembretes_extras_enviados < numero_lembrete
            ):
                agendamento.lembretes_extras_enviados = numero_lembrete
                return self._criar_notificacao(usuario, medicamento)

        return None

    @staticmethod
    def _criar_notificacao(usuario, medicamento):
        mensagem = f"Hora de tomar {medicamento.nome} ({medicamento.dosagem})"
        return Notificacao(usuario, mensagem)

    @staticmethod
    def _combinar(data_ref, horario_str):
        hora, minuto = horario_str.split(":")
        return datetime.combine(
            data_ref, datetime.min.time().replace(hour=int(hora), minute=int(minuto))
        )

    @staticmethod
    def obter_ou_criar_agendamento(medicamento, horario, data):
        for agendamento in medicamento.agendamentos:
            if agendamento.horario == horario and agendamento.data == data:
                return agendamento

        agendamento = Agendamento(medicamento, horario, data)
        medicamento.agendamentos.append(agendamento)
        return agendamento

    @staticmethod
    def obter_agendamento(medicamento, horario, data=None):
        data = data or date.today()
        for agendamento in medicamento.agendamentos:
            if agendamento.horario == horario and agendamento.data == data:
                return agendamento
        return None
