# Projeto LUMI - TCC

Projeto realizado para Trabalho de Conclusão de Curso, um sistema de comunicação em tempo real entre Discord e página Web com recurso de acessibilidade de Libras para pessoas com deficiência.

## Índice

- [Índice](#índice)
- [Funcionalidades](#funcionalidades)
- [Arquitetura do Projeto](#arquitetura-do-projeto)
- [Pré-requisitos](#pré-requisitos)
- [Instalação](#instalação)
  - [Bot e Websocket (Python)](#bot-e-websocket-python)
  - [Aplicação Web (Next.js)](#aplicação-web-nextjs)
- [Execução](#execução)
  - [Iniciar o Bot do Discord](#iniciar-o-bot-do-discord)
  - [Iniciar a Aplicação Web](#iniciar-a-aplicação-web)
- [Como Funciona](#como-funciona)
  - [Fluxo de Voz para Texto](#fluxo-de-voz-para-texto)
  - [Implementação Socket.IO](#implementação-socketio)
- [Integração VLibras](#integração-vlibras)
- [Configuração](#configuração)
  - [Configuração do Bot](#configuração-do-bot)
  - [Configuração da Web](#configuração-da-web)
- [Solução de Problemas](#solução-de-problemas)

## Funcionalidades

- Bot para Discord com processamento de voz
- Transmissão de transcrições de texto em tempo real para a Web via Socket.IO
- Integração com widget VLibras para acessibilidade
- Interface Web em Next.js para receber as transcrições e exibi-las em Libras

## Arquitetura do Projeto

```text
Voz no Discord → Bot LUMI (Python) → Servidor Socket.IO (Python) → Aplicação Web (Next.js) → Widget VLibras
```

## Pré-requisitos

- Python 3.12+
- Node.js 18+
- UV (gerenciador de pacotes Python)
- Git
- Token de bot do Discord
- GPU com suporte a CUDA/ROCm (opcional para aceleração de IA, ROCm disponível apenas no Linux)

## Instalação

É possível obter o projeto baixando o arquivo ZIP ou clonando o repositório do GitHub.

### Bot e Websocket (Python)

1. Navegue até a pasta do bot:

   ```bash
   cd src/lumi-bot/
   ```

2. Crie e configure o arquivo .env:

   ```bash
   cp .env.example .env
   ```

3. Instale as dependências, incluindo a versão do PyTorch de acordo com seu hardware:
   - **Para CPU apenas**:

      ```bash
      uv sync --extra cpu
      ```

   - **Para GPU NVIDIA (CUDA 12.8)**:

      ```bash
      uv sync --extra cu128
      ```

   - **Para GPU AMD (ROCm 6.3)**:

      ```bash
      uv sync --extra rocm
      ```

### Aplicação Web (Next.js)

1. Navegue até a pasta da aplicação web:

   ```bash
   cd ../lumi-web/
   ```

2. Crie e configure o arquivo .env:

   ```bash
   cp .env.example .env
   ```

3. Instale as dependências usando npm:

   ```bash
   npm install
   ```

## Execução

### Iniciar o Bot do Discord

```bash
cd src/lumi-bot/
uv run .
```

### Iniciar a Aplicação Web

```bash
cd src/lumi-web/
npm run dev
```

## Como Funciona

### Fluxo de Voz para Texto

1. Algum usuário presente em um canal de voz ativa o Bot
2. Usuários conversam no canal de voz do Discord
3. Bot captura os áudios e processa usando a biblioteca Whisper
4. O Whisper gera transcrições dos áudios de cada usuário
5. As transcrições são enviadas via Socket.IO para aplicação web
6. Aplicação web exibe transcrições em tempo real
7. Widget VLibras exibe a transcrição em Libras

### Implementação Socket.IO

- Servidor Socket.IO é executado junto do Bot do Discord
- Aplicação web se conecta ao servidor na porta configurada
- Bot envia transcrições por meio do evento `transcript`
- Aplicação web recebe os eventos e atualiza a lista de transcrições

## Integração VLibras

A aplicação web inclui o widget VLibras para fornecer:

- Tradução para Língua Brasileira de Sinais
- Recursos de acessibilidade para deficientes auditivos
- Atualizações em tempo real do conteúdo transcrito

## Configuração

### Configuração do Bot

Edite `src/lumi-bot/.env`:

```properties
DISCORD_TOKEN=seu_token_do_bot
API_PORT=3001
```

### Configuração da Web

Edite `src/lumi-web/.env`:

```properties
NEXT_PUBLIC_SOCKET_IO_URL=ws://localhost:3001
```

## Solução de Problemas

- Rode a aplicação Python com `ENV=development` para ver informações de debug
- Verifique se ambas as aplicações estão em execução e nenhum erro ocorreu
- Confira se as portas não estão em uso e ambos `.env` estão utilizando as mesmas portas
- Verifique se o bot foi adicionado ao servidor do Discord
- Certifique-se que todas dependências foram instaladas corretamente
- Para problemas com PyTorch, verifique se instalou a versão correta para seu hardware
