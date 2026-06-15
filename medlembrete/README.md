# MedLembrete

Aplicativo de gestão e lembretes de medicamentos, voltado principalmente para
pacientes que precisam tomar remédios em horários específicos. Desenvolvido para a disciplina de
Engenharia de Software II.

## Funcionalidades da Sprint 1

| PBI   | Funcionalidade                                              |
|-------|-------------------------------------------------------------|
| PB01  | Cadastro de usuário                                         |
| PB03  | Cadastro de medicamento                                     |
| PB07  | Configuração de horário de administração do medicamento     |
| PB12  | Receber notificação para tomar medicamento                  |
| PB14  | Registro / confirmação de administração do medicamento      |

> Observação: o sistema roda inteiramente em memória/local, sem nenhuma
> chamada de rede, o que garante o funcionamento mesmo sem acesso à internet.

## Estrutura do projeto

```
medlembrete/
├── app.py                     # Interface (Streamlit) usada na demonstração
├── requirements.txt
├── src/
│   └── models.py               # Regras de negócio (modelos de domínio)
└── features/                   # Testes automatizados em BDD (Behave)
    ├── cadastro_usuario.feature
    ├── cadastro_medicamento.feature
    ├── configuracao_horario.feature
    ├── notificacao_medicamento.feature
    ├── registro_administracao.feature
    ├── environment.py
    └── steps/
        ├── steps_comuns.py
        ├── steps_usuario.py
        ├── steps_medicamento.py
        ├── steps_horario.py
        ├── steps_notificacao.py
        └── steps_administracao.py
```

## Como executar (Windows / Mac / Linux)

### 1. Pré-requisito: Python 3.10+

Baixe e instale o Python em https://www.python.org/downloads/ (no Windows,
marque a opção **"Add Python to PATH"** durante a instalação).

### 2. Instalar as dependências

Abra um terminal (cmd / PowerShell / terminal) na pasta do projeto e execute:

```bash
pip install -r requirements.txt
```

### 3. Rodar o aplicativo

```bash
streamlit run app.py
```

Isso abrirá automaticamente o aplicativo no navegador (geralmente em
`http://localhost:8501`).

### 4. Rodar os testes automatizados (BDD)

```bash
behave
```

O Behave executa todos os arquivos `.feature` em `features/` usando os
cenários e critérios de aceitação definidos com a equipe/cliente.

## Subindo o projeto para o GitHub (sem precisar instalar o Git)

1. Crie um repositório novo em https://github.com/new.
2. Na página do repositório recém-criado, clique em **"uploading an existing
   file"** (ou "Add file" → "Upload files").
3. Arraste a pasta `medlembrete` (ou os arquivos extraídos do `.zip`) para a
   área de upload.
4. Escreva uma mensagem de commit (ex: "Sprint 1 - histórias e implementação
   inicial") e clique em **"Commit changes"**.

Isso é suficiente para entregar o código no GitHub sem precisar instalar nada
adicional no Windows.
