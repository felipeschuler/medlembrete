"""
MedLembrete — Aplicativo desktop (CustomTkinter).

Abre uma janela no formato de smartphone, com navegação por abas inferiores,
usando a MESMA lógica de negócio do projeto (src/models.py).

Como executar:
    pip install -r requirements.txt
    python desktop_app.py
"""

from datetime import date, datetime

import customtkinter as ctk
from tkinter import messagebox

from src.models import (
    Agendamento,
    EmailJaCadastradoError,
    HorarioInvalidoError,
    Medicamento,
    NomeObrigatorioError,
    ServicoNotificacao,
    SistemaCadastro,
)
from src.persistencia import carregar_dados, salvar_dados


# ---------------------------------------------------------------------------
# Tema visual
# ---------------------------------------------------------------------------
ctk.set_appearance_mode("light")

COR_PRIMARIA = "#0F9D8C"
COR_PRIMARIA_HOVER = "#0C7C6E"
COR_PRIMARIA_CLARA = "#E6F6F3"
COR_FUNDO = "#F2F5F7"
COR_CARTAO = "#FFFFFF"
COR_BORDA = "#E5E9EC"
COR_TEXTO = "#1F2A37"
COR_TEXTO_SECUNDARIO = "#6B7785"
COR_PENDENTE = "#F59E0B"
COR_PENDENTE_BG = "#FEF3E2"
COR_TOMADO = "#10B981"
COR_TOMADO_BG = "#E7F8F1"
COR_ERRO = "#E54848"
COR_ERRO_BG = "#FDECEC"

FONTE_APP = "Segoe UI"
F_TITULO_APP = (FONTE_APP, 22, "bold")
F_TITULO_TELA = (FONTE_APP, 17, "bold")
F_SUBTITULO = (FONTE_APP, 13, "bold")
F_TEXTO = (FONTE_APP, 12)
F_TEXTO_SEC = (FONTE_APP, 11)
F_PEQUENA = (FONTE_APP, 10)
F_BOTAO_NAV = (FONTE_APP, 10)


class MedLembreteApp(ctk.CTk):
    LARGURA = 375
    ALTURA = 690

    def __init__(self):
        super().__init__()

        self.title("MedLembrete")
        self.geometry(f"{self.LARGURA}x{self.ALTURA}")
        self.minsize(self.LARGURA, self.ALTURA)
        self.maxsize(self.LARGURA, self.ALTURA)
        self.configure(fg_color=COR_FUNDO)

        # --- "Backend": mesma lógica de domínio do projeto ---
        # Carrega dados salvos anteriormente (arquivo local JSON).
        # Se não existir ainda, começa com um sistema vazio.
        self.sistema = carregar_dados()
        self.servico = ServicoNotificacao()
        self.usuario_atual = None

        # Tela "moldura de celular": um frame central que ocupa toda a janela
        self.tela = ctk.CTkFrame(self, fg_color=COR_FUNDO, corner_radius=0)
        self.tela.pack(fill="both", expand=True)

        self.mostrar_login()

    # ------------------------------------------------------------------
    def salvar(self):
        """Persiste o estado atual do sistema em disco (arquivo JSON local)."""
        salvar_dados(self.sistema)

    # ------------------------------------------------------------------
    # Utilidades de layout
    # ------------------------------------------------------------------
    def limpar_tela(self):
        for widget in self.tela.winfo_children():
            widget.destroy()

    def criar_cabecalho(self, titulo, subtitulo=None, on_voltar=None):
        header = ctk.CTkFrame(self.tela, fg_color=COR_PRIMARIA, corner_radius=0, height=84)
        header.pack(side="top", fill="x")
        header.pack_propagate(False)

        linha_topo = ctk.CTkFrame(header, fg_color="transparent")
        linha_topo.pack(fill="x", padx=16, pady=(14, 0))

        if on_voltar:
            btn_voltar = ctk.CTkButton(
                linha_topo, text="←", width=30, height=30, corner_radius=15,
                fg_color=COR_PRIMARIA_HOVER, hover_color="#0A6B5F",
                font=(FONTE_APP, 14, "bold"), command=on_voltar,
            )
            btn_voltar.pack(side="left", padx=(0, 8))

        ctk.CTkLabel(
            linha_topo, text=titulo, font=F_TITULO_TELA, text_color="white",
        ).pack(side="left", anchor="w")

        if subtitulo:
            ctk.CTkLabel(
                header, text=subtitulo, font=F_TEXTO_SEC, text_color=COR_PRIMARIA_CLARA,
            ).pack(anchor="w", padx=16, pady=(2, 0))

        return header

    def criar_navbar(self, ativo):
        navbar = ctk.CTkFrame(self.tela, fg_color=COR_CARTAO, corner_radius=0, height=66,
                               border_width=1, border_color=COR_BORDA)
        navbar.pack(side="bottom", fill="x")
        navbar.pack_propagate(False)
        navbar.grid_rowconfigure(0, weight=1)

        itens = [
            ("home", "🏠", "Início", self.mostrar_home),
            ("add", "➕", "Novo", self.mostrar_cadastro_medicamento),
            ("notif", "🔔", "Avisos", self.mostrar_notificacoes),
            ("hist", "📜", "Histórico", self.mostrar_historico),
        ]

        for col, (chave, icone, label, comando) in enumerate(itens):
            navbar.grid_columnconfigure(col, weight=1)
            cor_texto = COR_PRIMARIA if chave == ativo else COR_TEXTO_SECUNDARIO
            item = ctk.CTkButton(
                navbar, text=f"{icone}\n{label}", command=comando,
                fg_color="transparent", hover_color=COR_PRIMARIA_CLARA,
                text_color=cor_texto, font=F_BOTAO_NAV, corner_radius=10,
            )
            item.grid(row=0, column=col, sticky="nsew", padx=2, pady=6)

        return navbar

    def conteudo_scrollavel(self, **kwargs):
        frame = ctk.CTkScrollableFrame(
            self.tela, fg_color=COR_FUNDO, scrollbar_button_color=COR_BORDA, **kwargs
        )
        frame.pack(side="top", fill="both", expand=True)
        return frame

    def cartao(self, parent, **kwargs):
        return ctk.CTkFrame(
            parent, fg_color=COR_CARTAO, corner_radius=14,
            border_width=1, border_color=COR_BORDA, **kwargs
        )

    def badge(self, parent, texto, cor_fundo, cor_texto):
        return ctk.CTkLabel(
            parent, text=texto, font=F_PEQUENA, text_color=cor_texto,
            fg_color=cor_fundo, corner_radius=8, padx=8, pady=2,
        )

    # ------------------------------------------------------------------
    # Tela: Login / Cadastro de usuário (PB01)
    # ------------------------------------------------------------------
    def mostrar_login(self):
        self.limpar_tela()

        topo = ctk.CTkFrame(self.tela, fg_color=COR_PRIMARIA, corner_radius=0, height=160)
        topo.pack(side="top", fill="x")
        topo.pack_propagate(False)

        ctk.CTkLabel(topo, text="💊", font=(FONTE_APP, 42)).pack(pady=(34, 0))
        ctk.CTkLabel(
            topo, text="MedLembrete", font=F_TITULO_APP, text_color="white",
        ).pack()
        ctk.CTkLabel(
            topo, text="Seus remédios, no horário certo.",
            font=F_TEXTO_SEC, text_color=COR_PRIMARIA_CLARA,
        ).pack(pady=(2, 0))

        corpo = ctk.CTkFrame(self.tela, fg_color=COR_FUNDO)
        corpo.pack(side="top", fill="both", expand=True, padx=20, pady=16)

        abas = ctk.CTkTabview(
            corpo, fg_color=COR_CARTAO, segmented_button_fg_color=COR_FUNDO,
            segmented_button_selected_color=COR_PRIMARIA,
            segmented_button_selected_hover_color=COR_PRIMARIA_HOVER,
            segmented_button_unselected_color=COR_FUNDO,
            text_color=COR_TEXTO, corner_radius=14,
        )
        abas.pack(fill="both", expand=True)
        abas.add("Entrar")
        abas.add("Cadastrar")

        # --- Aba Entrar ---
        aba_entrar = abas.tab("Entrar")
        usuarios = self.sistema.listar_usuarios()

        if not usuarios:
            ctk.CTkLabel(
                aba_entrar, text="Nenhum usuário cadastrado ainda.\nUse a aba 'Cadastrar'.",
                font=F_TEXTO, text_color=COR_TEXTO_SECUNDARIO, justify="center",
            ).pack(pady=40)
        else:
            ctk.CTkLabel(aba_entrar, text="Selecione seu usuário", font=F_SUBTITULO,
                          text_color=COR_TEXTO).pack(anchor="w", padx=16, pady=(20, 8))

            opcoes = {f"{u.nome}  ({u.email})": u.email for u in usuarios}
            var_usuario = ctk.StringVar(value=list(opcoes.keys())[0])

            ctk.CTkOptionMenu(
                aba_entrar, values=list(opcoes.keys()), variable=var_usuario,
                fg_color=COR_FUNDO, button_color=COR_PRIMARIA,
                button_hover_color=COR_PRIMARIA_HOVER, text_color=COR_TEXTO,
                dropdown_fg_color=COR_CARTAO, width=260,
            ).pack(padx=16, fill="x")

            def entrar():
                self.usuario_atual = self.sistema.usuarios_por_email[opcoes[var_usuario.get()]]
                self.mostrar_home()

            ctk.CTkButton(
                aba_entrar, text="Entrar", command=entrar, height=42,
                fg_color=COR_PRIMARIA, hover_color=COR_PRIMARIA_HOVER,
                font=F_SUBTITULO, corner_radius=10,
            ).pack(padx=16, pady=20, fill="x")

        # --- Aba Cadastrar ---
        aba_cadastrar = abas.tab("Cadastrar")

        ctk.CTkLabel(aba_cadastrar, text="Crie sua conta", font=F_SUBTITULO,
                      text_color=COR_TEXTO).pack(anchor="w", padx=16, pady=(16, 8))

        entry_nome = ctk.CTkEntry(aba_cadastrar, placeholder_text="Nome completo", height=40)
        entry_nome.pack(padx=16, pady=6, fill="x")

        entry_email = ctk.CTkEntry(aba_cadastrar, placeholder_text="E-mail", height=40)
        entry_email.pack(padx=16, pady=6, fill="x")

        entry_telefone = ctk.CTkEntry(aba_cadastrar, placeholder_text="Telefone", height=40)
        entry_telefone.pack(padx=16, pady=6, fill="x")

        def cadastrar():
            nome = entry_nome.get().strip()
            email = entry_email.get().strip()
            telefone = entry_telefone.get().strip()

            if not nome or not email:
                messagebox.showerror("Campos obrigatórios", "Nome e e-mail são obrigatórios.")
                return

            try:
                usuario = self.sistema.cadastrar_usuario(nome=nome, email=email, telefone=telefone)
                self.usuario_atual = usuario
                self.salvar()
                self.mostrar_home()
            except EmailJaCadastradoError as exc:
                messagebox.showerror("E-mail já cadastrado", str(exc))

        ctk.CTkButton(
            aba_cadastrar, text="Cadastrar", command=cadastrar, height=42,
            fg_color=COR_PRIMARIA, hover_color=COR_PRIMARIA_HOVER,
            font=F_SUBTITULO, corner_radius=10,
        ).pack(padx=16, pady=20, fill="x")

    # ------------------------------------------------------------------
    # Tela: Início — lista de medicamentos (PB07 / PB14)
    # ------------------------------------------------------------------
    def mostrar_home(self):
        self.limpar_tela()
        usuario = self.usuario_atual

        header = self.criar_cabecalho(f"Olá, {usuario.nome.split()[0]} 👋", "Seus medicamentos de hoje")

        # Botão "Sair" no canto do cabeçalho
        btn_sair = ctk.CTkButton(
            header, text="Sair", width=54, height=28, corner_radius=8,
            fg_color=COR_PRIMARIA_HOVER, hover_color="#0A6B5F",
            font=F_PEQUENA, command=self.sair,
        )
        btn_sair.place(relx=1.0, x=-16, y=18, anchor="ne")

        self.criar_navbar("home")

        content = self.conteudo_scrollavel()

        if not usuario.medicamentos:
            vazio = self.cartao(content)
            vazio.pack(fill="x", padx=16, pady=20)
            ctk.CTkLabel(
                vazio, text="🗒️\n\nVocê ainda não tem medicamentos cadastrados.\n"
                             "Toque em '➕ Novo' para adicionar o primeiro.",
                font=F_TEXTO, text_color=COR_TEXTO_SECUNDARIO, justify="center",
            ).pack(pady=24, padx=16)

        medicamentos = sorted(
            usuario.medicamentos, key=lambda m: m.horarios[0] if m.horarios else "99:99"
        )

        for med in medicamentos:
            card = self.cartao(content)
            card.pack(fill="x", padx=16, pady=8)

            topo = ctk.CTkFrame(card, fg_color="transparent")
            topo.pack(fill="x", padx=14, pady=(12, 4))

            ctk.CTkLabel(topo, text=f"💊  {med.nome}", font=F_SUBTITULO,
                          text_color=COR_TEXTO).pack(side="left")

            if med.tipo:
                self.badge(topo, med.tipo, COR_PRIMARIA_CLARA, COR_PRIMARIA_HOVER).pack(side="right")

            info = ctk.CTkFrame(card, fg_color="transparent")
            info.pack(fill="x", padx=14, pady=(0, 6))

            partes_info = []
            if med.dosagem:
                partes_info.append(f"Dosagem: {med.dosagem}")
            if med.quantidade_disponivel is not None:
                partes_info.append(f"Restam: {med.quantidade_disponivel}")
            if partes_info:
                ctk.CTkLabel(info, text="  •  ".join(partes_info), font=F_TEXTO_SEC,
                              text_color=COR_TEXTO_SECUNDARIO).pack(anchor="w")

            if med.quantidade_disponivel is not None and med.quantidade_disponivel <= 3:
                aviso = self.badge(card, "⚠️ Estoque acabando — reponha em breve",
                                    COR_ERRO_BG, COR_ERRO)
                aviso.pack(anchor="w", padx=14, pady=(0, 8))

            if not med.horarios:
                ctk.CTkLabel(card, text="Nenhum horário configurado.", font=F_TEXTO_SEC,
                              text_color=COR_TEXTO_SECUNDARIO).pack(anchor="w", padx=14, pady=(0, 12))
            else:
                for horario in med.horarios:
                    agendamento = self.servico.obter_ou_criar_agendamento(med, horario, date.today())
                    linha = ctk.CTkFrame(card, fg_color="transparent")
                    linha.pack(fill="x", padx=14, pady=4)

                    if agendamento.status == Agendamento.TOMADO:
                        self.badge(
                            linha, f"✅ {horario} — tomado às {agendamento.horario_confirmacao}",
                            COR_TOMADO_BG, COR_TOMADO,
                        ).pack(side="left")
                    else:
                        self.badge(linha, f"⏳ {horario} — pendente", COR_PENDENTE_BG, COR_PENDENTE).pack(side="left")

                        def marcar_tomado(med=med, horario=horario):
                            ag = self.servico.obter_ou_criar_agendamento(med, horario, date.today())
                            ag.confirmar(datetime.now().strftime("%H:%M"))
                            if med.quantidade_disponivel is not None and med.quantidade_disponivel > 0:
                                med.quantidade_disponivel -= 1
                            self.salvar()
                            self.mostrar_home()

                        ctk.CTkButton(
                            linha, text="Marquei como tomado", height=26, corner_radius=8,
                            fg_color=COR_PRIMARIA, hover_color=COR_PRIMARIA_HOVER,
                            font=F_PEQUENA, command=marcar_tomado,
                        ).pack(side="right")

                # espaço inferior do card
                ctk.CTkLabel(card, text="", height=4).pack()

    # ------------------------------------------------------------------
    # Tela: Cadastrar medicamento (PB03 / PB07)
    # ------------------------------------------------------------------
    def mostrar_cadastro_medicamento(self):
        self.limpar_tela()
        self.criar_cabecalho("Novo medicamento", "Cadastre um remédio e seus horários",
                              on_voltar=self.mostrar_home)

        self.criar_navbar("add")

        content = self.conteudo_scrollavel()
        card = self.cartao(content)
        card.pack(fill="x", padx=16, pady=16)

        ctk.CTkLabel(card, text="Nome do medicamento", font=F_TEXTO_SEC,
                      text_color=COR_TEXTO_SECUNDARIO).pack(anchor="w", padx=16, pady=(16, 2))
        entry_nome = ctk.CTkEntry(card, placeholder_text="Ex: Amoxicilina", height=40)
        entry_nome.pack(fill="x", padx=16)

        ctk.CTkLabel(card, text="Dosagem", font=F_TEXTO_SEC,
                      text_color=COR_TEXTO_SECUNDARIO).pack(anchor="w", padx=16, pady=(14, 2))
        entry_dosagem = ctk.CTkEntry(card, placeholder_text="Ex: 500 mg", height=40)
        entry_dosagem.pack(fill="x", padx=16)

        ctk.CTkLabel(card, text="Tipo de uso", font=F_TEXTO_SEC,
                      text_color=COR_TEXTO_SECUNDARIO).pack(anchor="w", padx=16, pady=(14, 2))
        seg_tipo = ctk.CTkSegmentedButton(
            card, values=list(Medicamento.TIPOS_VALIDOS),
            selected_color=COR_PRIMARIA, selected_hover_color=COR_PRIMARIA_HOVER,
            unselected_color=COR_FUNDO, text_color=COR_TEXTO,
        )
        seg_tipo.set(Medicamento.TIPOS_VALIDOS[0])
        seg_tipo.pack(fill="x", padx=16)

        ctk.CTkLabel(card, text="Quantidade disponível", font=F_TEXTO_SEC,
                      text_color=COR_TEXTO_SECUNDARIO).pack(anchor="w", padx=16, pady=(14, 2))
        entry_quantidade = ctk.CTkEntry(card, placeholder_text="Ex: 20", height=40)
        entry_quantidade.pack(fill="x", padx=16)

        ctk.CTkLabel(card, text="Horários (separados por vírgula)", font=F_TEXTO_SEC,
                      text_color=COR_TEXTO_SECUNDARIO).pack(anchor="w", padx=16, pady=(14, 2))
        entry_horarios = ctk.CTkEntry(card, placeholder_text="Ex: 08:00, 20:00", height=40)
        entry_horarios.pack(fill="x", padx=16, pady=(0, 16))

        def salvar():
            nome = entry_nome.get().strip()
            dosagem = entry_dosagem.get().strip()
            tipo = seg_tipo.get()
            quantidade_str = entry_quantidade.get().strip()
            horarios_str = entry_horarios.get().strip()

            quantidade = None
            if quantidade_str:
                try:
                    quantidade = int(quantidade_str)
                except ValueError:
                    messagebox.showerror("Quantidade inválida", "Informe um número inteiro para a quantidade.")
                    return

            try:
                medicamento = Medicamento(
                    nome=nome or None, dosagem=dosagem or None, tipo=tipo,
                    quantidade_disponivel=quantidade,
                )
            except NomeObrigatorioError as exc:
                messagebox.showerror("Nome obrigatório", str(exc))
                return

            self.usuario_atual.adicionar_medicamento(medicamento)

            horarios_invalidos = []
            for horario in [h.strip() for h in horarios_str.split(",") if h.strip()]:
                try:
                    medicamento.configurar_horario(horario)
                except HorarioInvalidoError:
                    horarios_invalidos.append(horario)

            if horarios_invalidos:
                messagebox.showwarning(
                    "Horário(s) inválido(s)",
                    "Os seguintes horários não foram registrados (use o formato HH:MM):\n"
                    + ", ".join(horarios_invalidos),
                )

            self.salvar()
            messagebox.showinfo("Sucesso", f"Medicamento '{medicamento.nome}' cadastrado!")
            self.mostrar_home()

        ctk.CTkButton(
            content, text="💾  Salvar medicamento", command=salvar, height=44,
            fg_color=COR_PRIMARIA, hover_color=COR_PRIMARIA_HOVER,
            font=F_SUBTITULO, corner_radius=10,
        ).pack(fill="x", padx=16, pady=(0, 20))

    # ------------------------------------------------------------------
    # Tela: Notificações (PB12)
    # ------------------------------------------------------------------
    def mostrar_notificacoes(self):
        self.limpar_tela()
        self.criar_cabecalho("Notificações", "Simule a data/hora para testar os lembretes",
                              on_voltar=self.mostrar_home)

        self.criar_navbar("notif")

        content = self.conteudo_scrollavel()

        card = self.cartao(content)
        card.pack(fill="x", padx=16, pady=16)

        ctk.CTkLabel(
            card, text="O app verifica, com base na data/hora informadas, quais "
                       "medicamentos devem gerar lembrete agora — tudo processado "
                       "localmente, sem internet.",
            font=F_TEXTO_SEC, text_color=COR_TEXTO_SECUNDARIO, justify="left",
            wraplength=300,
        ).pack(padx=16, pady=(16, 12), anchor="w")

        linha = ctk.CTkFrame(card, fg_color="transparent")
        linha.pack(fill="x", padx=16, pady=(0, 16))

        col_data = ctk.CTkFrame(linha, fg_color="transparent")
        col_data.pack(side="left", fill="x", expand=True, padx=(0, 6))
        ctk.CTkLabel(col_data, text="Data (DD/MM/AAAA)", font=F_PEQUENA,
                      text_color=COR_TEXTO_SECUNDARIO).pack(anchor="w")
        entry_data = ctk.CTkEntry(col_data, height=38)
        entry_data.insert(0, date.today().strftime("%d/%m/%Y"))
        entry_data.pack(fill="x")

        col_hora = ctk.CTkFrame(linha, fg_color="transparent")
        col_hora.pack(side="left", fill="x", expand=True, padx=(6, 0))
        ctk.CTkLabel(col_hora, text="Hora (HH:MM)", font=F_PEQUENA,
                      text_color=COR_TEXTO_SECUNDARIO).pack(anchor="w")
        entry_hora = ctk.CTkEntry(col_hora, height=38)
        entry_hora.insert(0, datetime.now().strftime("%H:%M"))
        entry_hora.pack(fill="x")

        resultado_frame = ctk.CTkFrame(content, fg_color="transparent")
        resultado_frame.pack(fill="x", padx=16)

        def verificar():
            for widget in resultado_frame.winfo_children():
                widget.destroy()

            data_str = entry_data.get().strip()
            hora_str = entry_hora.get().strip()

            try:
                data_simulada = datetime.strptime(data_str, "%d/%m/%Y").date()
                hora, minuto = hora_str.split(":")
                data_hora = datetime.combine(
                    data_simulada,
                    datetime.min.time().replace(hour=int(hora), minute=int(minuto)),
                )
            except (ValueError, AttributeError):
                messagebox.showerror(
                    "Data/hora inválida",
                    "Use o formato DD/MM/AAAA para a data e HH:MM para a hora.",
                )
                return

            notificacoes = self.servico.verificar_medicamentos_agendados(self.sistema, data_hora)

            if not notificacoes:
                aviso = self.cartao(resultado_frame)
                aviso.pack(fill="x", pady=8)
                ctk.CTkLabel(
                    aviso, text="🔕  Nenhuma notificação para este horário.",
                    font=F_TEXTO, text_color=COR_TEXTO_SECUNDARIO,
                ).pack(padx=14, pady=14)
            else:
                for notificacao in notificacoes:
                    item = self.cartao(resultado_frame)
                    item.pack(fill="x", pady=8)
                    ctk.CTkLabel(
                        item, text=f"🔔  {notificacao.mensagem}",
                        font=F_TEXTO, text_color=COR_TEXTO, wraplength=290, justify="left",
                    ).pack(padx=14, pady=14, anchor="w")

        ctk.CTkButton(
            content, text="🔔  Verificar agora", command=verificar, height=44,
            fg_color=COR_PRIMARIA, hover_color=COR_PRIMARIA_HOVER,
            font=F_SUBTITULO, corner_radius=10,
        ).pack(fill="x", padx=16, pady=(0, 16))

    # ------------------------------------------------------------------
    # Tela: Histórico (PB14 / PB15)
    # ------------------------------------------------------------------
    def mostrar_historico(self):
        self.limpar_tela()
        self.criar_cabecalho("Histórico", "Administrações registradas",
                              on_voltar=self.mostrar_home)

        self.criar_navbar("hist")

        content = self.conteudo_scrollavel()

        registros = []
        for med in self.usuario_atual.medicamentos:
            for agendamento in med.agendamentos:
                registros.append((med, agendamento))

        registros.sort(key=lambda r: (r[1].data, r[1].horario))

        if not registros:
            vazio = self.cartao(content)
            vazio.pack(fill="x", padx=16, pady=20)
            ctk.CTkLabel(
                vazio, text="📭\n\nAinda não há histórico de administração.",
                font=F_TEXTO, text_color=COR_TEXTO_SECUNDARIO, justify="center",
            ).pack(pady=24, padx=16)

        for med, agendamento in registros:
            card = self.cartao(content)
            card.pack(fill="x", padx=16, pady=8)

            topo = ctk.CTkFrame(card, fg_color="transparent")
            topo.pack(fill="x", padx=14, pady=(12, 4))

            ctk.CTkLabel(topo, text=f"💊 {med.nome}", font=F_SUBTITULO,
                          text_color=COR_TEXTO).pack(side="left")

            if agendamento.status == Agendamento.TOMADO:
                self.badge(topo, "Tomado", COR_TOMADO_BG, COR_TOMADO).pack(side="right")
            else:
                self.badge(topo, "Pendente", COR_PENDENTE_BG, COR_PENDENTE).pack(side="right")

            detalhes = (
                f"Data: {agendamento.data.strftime('%d/%m/%Y')}   •   "
                f"Programado: {agendamento.horario}"
            )
            if agendamento.horario_confirmacao:
                detalhes += f"\nConfirmado às: {agendamento.horario_confirmacao}"

            ctk.CTkLabel(card, text=detalhes, font=F_TEXTO_SEC,
                          text_color=COR_TEXTO_SECUNDARIO, justify="left").pack(
                anchor="w", padx=14, pady=(0, 12)
            )

    # ------------------------------------------------------------------
    def sair(self):
        self.usuario_atual = None
        self.mostrar_login()


if __name__ == "__main__":
    app = MedLembreteApp()
    app.mainloop()
