"""
MedLembrete — Interface de demonstração (Streamlit).

Cobre as funcionalidades da Sprint 1:
  - PB01: Cadastro de usuário
  - PB03: Cadastro de medicamento
  - PB07: Configuração de horário de administração
  - PB12: Receber notificação para tomar medicamento
  - PB14: Confirmar administração / histórico

Toda a lógica roda em memória, localmente (sem nenhuma chamada de rede),
o que demonstra o funcionamento sem acesso à internet (PB23).
"""

from datetime import date, datetime

import streamlit as st

from src.models import (
    Agendamento,
    EmailJaCadastradoError,
    HorarioInvalidoError,
    Medicamento,
    NomeObrigatorioError,
    ServicoNotificacao,
    SistemaCadastro,
)

st.set_page_config(page_title="MedLembrete", page_icon="💊", layout="centered")

# ---------------------------------------------------------------------------
# Estado da sessão
# ---------------------------------------------------------------------------
if "sistema" not in st.session_state:
    st.session_state.sistema = SistemaCadastro()
if "servico" not in st.session_state:
    st.session_state.servico = ServicoNotificacao()
if "usuario_email" not in st.session_state:
    st.session_state.usuario_email = None

sistema: SistemaCadastro = st.session_state.sistema
servico: ServicoNotificacao = st.session_state.servico

st.title("💊 MedLembrete")
st.caption(
    "Aplicativo de gestão e lembretes de medicamentos — "
    "todos os dados ficam no dispositivo, sem necessidade de internet."
)


# ---------------------------------------------------------------------------
# Tela de login / cadastro de usuário (PB01)
# ---------------------------------------------------------------------------
def tela_login():
    st.subheader("Bem-vindo(a)!")

    tab_entrar, tab_cadastrar = st.tabs(["Entrar", "Cadastrar novo usuário"])

    with tab_entrar:
        usuarios = sistema.listar_usuarios()
        if not usuarios:
            st.info("Nenhum usuário cadastrado ainda. Use a aba **Cadastrar novo usuário**.")
        else:
            opcoes = {f"{u.nome} ({u.email})": u.email for u in usuarios}
            escolha = st.selectbox("Selecione seu usuário", list(opcoes.keys()))
            if st.button("Entrar", type="primary"):
                st.session_state.usuario_email = opcoes[escolha]
                st.rerun()

    with tab_cadastrar:
        with st.form("form_cadastro_usuario"):
            nome = st.text_input("Nome completo")
            email = st.text_input("E-mail")
            telefone = st.text_input("Telefone")
            submitted = st.form_submit_button("Cadastrar", type="primary")

            if submitted:
                if not nome or not email:
                    st.error("Nome e e-mail são obrigatórios.")
                else:
                    try:
                        sistema.cadastrar_usuario(nome=nome, email=email, telefone=telefone)
                        st.success(f"Usuário **{nome}** cadastrado com sucesso!")
                        st.session_state.usuario_email = email
                        st.rerun()
                    except EmailJaCadastradoError as exc:
                        st.error(str(exc))


# ---------------------------------------------------------------------------
# Aplicativo principal (usuário logado)
# ---------------------------------------------------------------------------
def tela_principal():
    usuario = sistema.usuarios_por_email[st.session_state.usuario_email]

    with st.sidebar:
        st.markdown(f"### 👤 {usuario.nome}")
        st.caption(f"📧 {usuario.email}")
        st.caption(f"📱 {usuario.telefone}")
        if st.button("Sair"):
            st.session_state.usuario_email = None
            st.rerun()
        st.divider()
        st.success("🔌 **Modo offline**: dados armazenados localmente, sem internet.")

    tab_meds, tab_cadastro, tab_notif, tab_hist = st.tabs(
        ["💊 Meus medicamentos", "➕ Cadastrar medicamento", "🔔 Notificações", "📜 Histórico"]
    )

    # --- Tab: Meus medicamentos (PB07, PB14) -------------------------------
    with tab_meds:
        st.subheader("Meus medicamentos")

        if not usuario.medicamentos:
            st.info("Você ainda não cadastrou nenhum medicamento.")

        for med in sorted(
            usuario.medicamentos, key=lambda m: m.horarios[0] if m.horarios else "99:99"
        ):
            with st.container(border=True):
                st.markdown(f"#### 💊 {med.nome}")
                col1, col2, col3 = st.columns(3)
                col1.metric("Dosagem", med.dosagem or "—")
                col2.metric("Tipo", med.tipo or "—")
                col3.metric(
                    "Qtd. disponível",
                    med.quantidade_disponivel
                    if med.quantidade_disponivel is not None
                    else "—",
                )

                if med.quantidade_disponivel is not None and med.quantidade_disponivel <= 3:
                    st.warning("⚠️ A quantidade desse medicamento está acabando!")

                st.markdown("**Horários de hoje:**")
                if not med.horarios:
                    st.caption("Nenhum horário configurado para este medicamento.")

                for horario in med.horarios:
                    agendamento = servico.obter_ou_criar_agendamento(med, horario, date.today())
                    col_a, col_b = st.columns([3, 1])
                    if agendamento.status == Agendamento.TOMADO:
                        col_a.markdown(
                            f"✅ **{horario}** — tomado às {agendamento.horario_confirmacao}"
                        )
                    else:
                        col_a.markdown(f"⏳ **{horario}** — status: *Pendente*")
                        if col_b.button("Marquei como tomado", key=f"tomar_{med.nome}_{horario}"):
                            agendamento.confirmar(datetime.now().strftime("%H:%M"))
                            if (
                                med.quantidade_disponivel is not None
                                and med.quantidade_disponivel > 0
                            ):
                                med.quantidade_disponivel -= 1
                            st.rerun()

                with st.expander("⚙️ Configurar horário de administração"):
                    novo_horario = st.text_input(
                        "Novo horário (HH:MM)", key=f"novo_horario_{med.nome}"
                    )
                    if st.button("Adicionar horário", key=f"add_horario_{med.nome}"):
                        try:
                            med.configurar_horario(novo_horario)
                            st.success(f"Horário {novo_horario} adicionado!")
                            st.rerun()
                        except HorarioInvalidoError as exc:
                            st.error(str(exc))

    # --- Tab: Cadastrar medicamento (PB03) ---------------------------------
    with tab_cadastro:
        st.subheader("Cadastrar novo medicamento")

        with st.form("form_cadastro_medicamento"):
            nome = st.text_input("Nome do medicamento")
            dosagem = st.text_input("Dosagem (ex: 500 mg)")
            tipo = st.selectbox("Tipo de uso", Medicamento.TIPOS_VALIDOS)
            quantidade = st.number_input(
                "Quantidade inicial disponível", min_value=0, step=1, value=0
            )
            horarios_str = st.text_input(
                "Horários de administração (separados por vírgula)",
                placeholder="08:00, 20:00",
            )
            submitted = st.form_submit_button("Cadastrar medicamento", type="primary")

            if submitted:
                try:
                    medicamento = Medicamento(
                        nome=nome,
                        dosagem=dosagem or None,
                        tipo=tipo,
                        quantidade_disponivel=int(quantidade) if quantidade else None,
                    )
                    usuario.adicionar_medicamento(medicamento)

                    horarios_invalidos = []
                    for horario in [h.strip() for h in horarios_str.split(",") if h.strip()]:
                        try:
                            medicamento.configurar_horario(horario)
                        except HorarioInvalidoError:
                            horarios_invalidos.append(horario)

                    st.success(f"Medicamento **{nome}** cadastrado com sucesso!")
                    if horarios_invalidos:
                        st.warning(
                            "Horário(s) inválido(s) e não registrados: "
                            + ", ".join(horarios_invalidos)
                        )
                    st.rerun()
                except NomeObrigatorioError as exc:
                    st.error(str(exc))

    # --- Tab: Notificações (PB12) ------------------------------------------
    with tab_notif:
        st.subheader("Verificação de notificações")
        st.write(
            "O sistema verifica, com base no horário atual, quais medicamentos "
            "precisam ser tomados — tudo processado localmente, sem internet."
        )

        col1, col2 = st.columns(2)
        data_simulada = col1.date_input("Data", value=date.today())
        hora_simulada = col2.time_input("Horário atual", value=datetime.now().time())

        if st.button("🔔 Verificar medicamentos agendados", type="primary"):
            data_hora = datetime.combine(data_simulada, hora_simulada)
            notificacoes = servico.verificar_medicamentos_agendados(sistema, data_hora)

            if notificacoes:
                for notificacao in notificacoes:
                    st.toast(notificacao.mensagem, icon="🔔")
                    st.success(f"🔔 {notificacao.mensagem}")
            else:
                st.info("Nenhuma notificação para o horário informado.")

    # --- Tab: Histórico (PB14 / PB15) ---------------------------------------
    with tab_hist:
        st.subheader("Histórico de administração")

        linhas = []
        for med in usuario.medicamentos:
            for agendamento in sorted(
                med.agendamentos, key=lambda a: (a.data, a.horario)
            ):
                linhas.append(
                    {
                        "Medicamento": med.nome,
                        "Data": agendamento.data.strftime("%d/%m/%Y"),
                        "Horário programado": agendamento.horario,
                        "Status": agendamento.status,
                        "Confirmado às": agendamento.horario_confirmacao or "—",
                    }
                )

        if linhas:
            st.dataframe(linhas, use_container_width=True, hide_index=True)
        else:
            st.info("Ainda não há histórico de administração registrado.")


# ---------------------------------------------------------------------------
# Roteamento
# ---------------------------------------------------------------------------
if st.session_state.usuario_email is None:
    tela_login()
else:
    tela_principal()
