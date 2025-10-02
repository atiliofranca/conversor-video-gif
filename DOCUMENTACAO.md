# Documentação Técnica - Conversor de Vídeo para GIF

## Visão Geral
Este projeto é uma aplicação web desenvolvida em Python utilizando o framework Flask. Ele permite ao usuário converter vídeos de diversos formatos para GIF, com opções de resolução e restrições de duração e tamanho.

## Tecnologias Utilizadas
- **Python 3.8+**
- **Flask**: Framework web para backend
- **FFmpeg**: Ferramenta de linha de comando para manipulação de vídeos
- **Werkzeug**: Utilitário para segurança de nomes de arquivos
- **HTML/CSS/JS**: Interface web

## Estrutura do Projeto
```
conversor-video-gif/
├── app.py                # Backend Flask
├── main.py               # (Opcional) Ponto de entrada alternativo
├── requirements.txt      # Dependências Python
├── templates/
│   └── index.html        # Interface web
├── static/               # Arquivos estáticos (CSS, JS, imagens)
├── uploads/              # Armazenamento temporário de vídeos enviados
├── README.md             # Instruções gerais
├── DOCUMENTACAO.md       # Documentação técnica
```

## Fluxo de Funcionamento
1. **Upload do vídeo**: O usuário seleciona um arquivo de vídeo e a resolução desejada na interface web.
2. **Validação**: O backend verifica extensão, tamanho (até 300MB) e duração (até 3 minutos).
3. **Conversão**: O vídeo é processado pelo FFmpeg, gerando um GIF na resolução escolhida.
4. **Download**: O GIF convertido é disponibilizado para download automático.

## Principais Componentes
### Backend (app.py)
- **Configuração do Flask**: Define limites de tamanho, pasta de uploads e inicializa o app.
- **Funções utilitárias**:
  - `allowed_file(filename)`: Verifica se a extensão é permitida.
  - `get_video_duration(filename)`: Obtém a duração do vídeo via FFmpeg.
  - `convert_to_gif(...)`: Executa a conversão usando FFmpeg CLI, gerando paleta e GIF.
- **Rotas**:
  - `/`: Renderiza a página principal.
  - `/upload`: Recebe o vídeo, valida, converte e retorna o GIF.
- **Tratamento de erros**: Respostas JSON para erros de validação e limites.

### Frontend (templates/index.html)
- **Formulário de upload**: Permite seleção de vídeo e resolução.
- **Barra de progresso**: Exibe status da conversão.
- **Explicações de resolução**: Ajuda o usuário a escolher o melhor formato.

## Dependências
- Listadas em `requirements.txt`. Instale com:
  ```bash
  pip install -r requirements.txt
  ```
- FFmpeg deve estar instalado e disponível no PATH do sistema.


## Pontos Importantes da Linha de Código

- Todos os uploads são salvos em diretório temporário usando `tempfile.gettempdir()`, evitando acúmulo de arquivos.
- O limite de duração do vídeo (3 minutos) é verificado pela função `get_video_duration`, que utiliza o FFmpeg para obter metadados.
- A conversão para GIF utiliza dois comandos FFmpeg: um para gerar a paleta de cores e outro para criar o GIF com filtro de paleta, garantindo melhor qualidade.
- O backend aceita múltiplas resoluções, recebidas via formulário e aplicadas diretamente nos comandos FFmpeg.
- O tratamento de erros retorna respostas JSON claras para o frontend, facilitando integração e depuração.
- O campo `MAX_CONTENT_LENGTH` limita uploads a 300MB, protegendo o servidor contra arquivos grandes.
- O nome do arquivo GIF gerado inclui timestamp para evitar conflitos e sobrescritas.
- O frontend está centralizado e oferece explicações para cada resolução disponível, melhorando a experiência do usuário.
- Recomenda-se uso apenas em ambiente de desenvolvimento.

