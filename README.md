# Conversor de Vídeo para GIF

Este projeto é uma aplicação web em Flask que permite converter vídeos (MP4, AVI, MOV, MKV, WMV) de até 3 minutos e 300MB para GIF, com escolha de resolução e redimensionamento automático.

## Funcionalidades
- Upload de vídeo via navegador
- Conversão para GIF usando FFmpeg
- Limite de duração: 3 minutos
- Limite de tamanho: 300MB
- Escolha de resolução do GIF
- Suporte a Windows, Linux e macOS
## Resoluções disponíveis e explicações

Você pode escolher entre as seguintes resoluções para o GIF gerado:

- **320x180** (baixo, rápido para carregar)
- **360x240** (comum em previews)
- **480x270** (padrão SD widescreen)
- **640x360** (HD leve, boa qualidade sem arquivos grandes)
- **800x450** (HD intermediário)
- **854x480** (SD 16:9, usado em vídeos online)
- **960x540** (qHD, qualidade superior)
- **1280x720** (HD, arquivos grandes, menos usado para GIFs)

## Pré-requisitos
- Python 3.8+
- FFmpeg instalado e disponível no PATH
- pip (gerenciador de pacotes Python)

## Instalação

### Windows
1. Instale o Python: https://www.python.org/downloads/
2. Instale o FFmpeg:
   - Recomenda-se usar o [Chocolatey](https://chocolatey.org/install):
     - Chocolatey é um gerenciador de pacotes para Windows. Para instalar o Chocolatey, execute o comando abaixo no PowerShell (como Administrador):
       ```powershell
       Set-ExecutionPolicy Bypass -Scope Process -Force; [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072; iex ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))
       ```
     - Após instalar o Chocolatey, instale o FFmpeg:
       ```powershell
       choco install ffmpeg
       ```
   - Ou baixe manualmente: https://ffmpeg.org/download.html
   - Adicione o diretório `bin` do FFmpeg ao PATH do sistema.
3. Clone o projeto e instale as dependências:
   ```powershell
   git clone <repo-url>
   cd conversor-video-gif
   python -m venv venv
   venv\Scripts\activate
   pip install -r requirements.txt
   ```

### Linux
1. Instale o Python e pip (geralmente já instalados)
2. Instale o FFmpeg:
   ```bash
   sudo apt update
   sudo apt install ffmpeg python3-pip
   ```
3. Clone o projeto e instale as dependências:
   ```bash
   git clone <repo-url>
   cd conversor-video-gif
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

### macOS
1. Instale o Python: https://www.python.org/downloads/
2. Instale o FFmpeg via Homebrew:
   ```bash
   brew install ffmpeg
   ```
3. Clone o projeto e instale as dependências:
   ```bash
   git clone <repo-url>
   cd conversor-video-gif
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

## Como usar
1. Execute a aplicação:
   ```bash
   # Ative o ambiente virtual se necessário
   python app.py
   ```
2. Acesse [http://127.0.0.1:5000](http://127.0.0.1:5000) no navegador
3. Faça upload do vídeo e aguarde o download do GIF

## Observações
- O FFmpeg precisa estar disponível no PATH do sistema.
- O limite de tamanho e duração pode ser ajustado em `app.py`.
- O GIF gerado é baixado automaticamente após a conversão.

## Estrutura do projeto
```
conversor-video-gif/
├── app.py
├── requirements.txt
├── templates/
│   └── index.html
├── static/
├── uploads/
└── README.md
```

## Licença
MIT
