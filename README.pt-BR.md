<div align="right">
  🇺🇸 <a href="README.md">English</a> | 🇧🇷 <strong>Português</strong>
</div>

# 🎵 Discord Music Bot

Um bot de música para o Discord desenvolvido em Python, com suporte a reprodução de áudio, playlists completas, filas e comandos de texto para controle de reprodução.

---

## 🚀 Funcionalidades

- Reprodução de áudio via YouTube, YouTube Music e URLs com extração via `yt-dlp` e `FFmpeg`
- Gerenciamento de fila de músicas e playlists (`play`, `skip`, `stop`, `jump`, `queue`, `pause`, `resume`)
- Estrutura modular utilizando Cogs do `discord.py`

---

## 🛠️ Pré-requisitos

- **Python 3.10+** (Recomendado 3.10 no servidor Ubuntu ou 3.14+ em ambiente de desenvolvimento local)
- **FFmpeg** instalado e adicionado ao `PATH` do sistema
- Token de bot criado no [Discord Developer Portal](https://discord.com/developers/applications)

---

## 📦 Instalação Local

1. **Clone o repositório:**
   ```bash
   git clone https://github.com/SeuUsuario/discord-music-bot.git
   ```

2. **Acesse a raiz do projeto:**
   ```bash
   cd discord-music-bot
   ```

3. **Crie e configure o arquivo `.env`:**
   A pasta `config/` já vem com o repositório. Você precisa criar o arquivo que vai armazenar suas credenciais dentro dela. 
   
   **No Linux / macOS (Terminal):**
   ```bash
   nano config/.env
   ```
   *(No nano, cole seu token, salve com `Ctrl + O`, `Enter` e saia com `Ctrl + X`)*.

   **No Windows (PowerShell):**
   ```powershell
   New-Item config\.env -ItemType File
   notepad config\.env
   ```
   *(Ou apenas clique com o botão direito na pasta `config` pelo PyCharm/VSCode e crie o arquivo).*

   Dentro do arquivo, adicione o token do seu bot gerado no Discord Developer Portal:
   ```text
   DISCORD_TOKEN=cole_seu_token_aqui
   ```

4. **Crie e ative o ambiente virtual:**
   Para manter as dependências isoladas, crie um ambiente virtual:
   
   **No Linux / macOS:**
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```
   
   **No Windows:**
   ```powershell
   python -m venv .venv
   .venv\Scripts\activate
   ```

5. **Instale as dependências:**
   Com o ambiente ativado, atualize o instalador e baixe os pacotes (mesmo comando para ambos):
   ```bash
   pip install --upgrade pip setuptools wheel
   pip install -r requirements.txt
   ```

6. **Configure os Cookies do YouTube (Obrigatório para o yt-dlp):**
   Para evitar bloqueios do YouTube (Erro 400), o bot precisa de um arquivo de autenticação. Siga o tutorial na seção **Como exportar o arquivo cookies.txt** abaixo e salve o arquivo gerado dentro da pasta `config/`.

7. **Inicie o bot:**
   ```bash
   python main.py
   ```

---

## 🍪 Como exportar o arquivo cookies.txt

O YouTube bloqueia requisições automatizadas do `yt-dlp` por padrão. Para contornar isso, o bot precisa simular um navegador real utilizando os cookies da sua sessão.

**Siga estes passos:**

1. Instale a extensão **Get cookies.txt LOCALLY** no seu navegador ([Chrome/Edge](https://chromewebstore.google.com/detail/get-cookiestxt-locally/cclelndahbckbenkjhflpocjadpjheoe) ou [Firefox](https://addons.mozilla.org/pt-BR/firefox/addon/cookies-txt/)).
2. Acesse o [YouTube](https://www.youtube.com/) e faça login.
   > ⚠️ **Aviso de Segurança:** É altamente recomendável criar e usar uma conta secundária ("conta fake") do Google apenas para o bot. Isso evita que sua conta principal sofra restrições do YouTube.
3. Com a aba do YouTube aberta e o login feito, clique no ícone da extensão no topo do navegador.
4. Clique no botão **Export** (ou certifique-se de exportar no formato *Netscape*).
5. Um arquivo de texto será baixado. Renomeie-o exatamente para `cookies.txt`.
6. Mova este arquivo para dentro da pasta **`config/`** no seu projeto (ficando `config/cookies.txt`).

---

## ⚙️ Estrutura do Projeto

```text
discord-music-bot/
├── .venv/               # Ambiente virtual isolado
├── cogs/                # Módulos e comandos do bot (ex: music.py)
├── config/              # Pasta de configurações locais
│   ├── .gitkeep         # Arquivo para manter a pasta no versionamento
│   ├── .env             # (Ignorado no Git) Variáveis de ambiente
│   └── cookies.txt      # (Ignorado no Git) Autenticação do YouTube
├── main.py              # Arquivo principal de inicialização
├── requirements.txt     # Lista de dependências
└── README.md            # Documentação do projeto
```