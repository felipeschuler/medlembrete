"""
Modelos de domínio do MedLembrete.

Este módulo concentra toda a lógica de negócio do aplicativo,
de forma independente da interface (Streamlit) e dos testes (Behave).
"""

from datetime import date


# ---------------------------------------------------------------------------
# Exceções de domínio
# ---------------------------------------------------------------------------

class EmailJaCadastradoError(Exception):
    """Lançada ao tentar cadastrar um e-mail que já existe."""


class NomeObrigatorioError(Exception):
    """Lançada ao tentar cadastrar um medicamento sem nome."""


class HorarioInvalidoError(Exception):
    """Lançada ao tentar configurar um horário fora do padrão HH:MM."""


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

    def verificar_medicamentos_agendados(self, sistema, data_hora):
        """Verifica, para o instante `data_hora`, quais medicamentos devem
        gerar notificação e retorna a lista de `Notificacao` geradas.

        Funciona inteiramente sobre dados em memória/local, sem nenhuma
        chamada de rede — o que garante o funcionamento mesmo sem acesso
        à internet (PB23).
        """
        notificacoes = []
        data_atual = data_hora.date()
        hora_atual = data_hora.strftime("%H:%M")

        for usuario in sistema.listar_usuarios():
            for medicamento in usuario.medicamentos:
                if hora_atual not in medicamento.horarios:
                    continue

                agendamento = self.obter_ou_criar_agendamento(
                    medicamento, hora_atual, data_atual
                )

                if not agendamento.notificado:
                    mensagem = (
                        f"Hora de tomar {medicamento.nome} "
                        f"({medicamento.dosagem})"
                    )
                    notificacoes.append(Notificacao(usuario, mensagem))
                    agendamento.notificado = True

        return notificacoes

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
