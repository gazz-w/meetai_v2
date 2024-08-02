
# meetAI - Transcrição e Resumo de Reuniões

meetAI é uma aplicação desenvolvida com Streamlit, que utiliza a API da OpenAI para transcrever e resumir reuniões. A aplicação permite o upload de arquivos de áudio e vídeo, transcreve o conteúdo falado e, utilizando a GPT-4, gera um resumo dos principais pontos discutidos, acordos/combinados e ações a serem tomadas.

## Funcionalidades

- **Transcrição de Áudio e Vídeo:** Upload de arquivos de áudio (mp3, wav, ogg, mpga) e vídeo (mp4) para transcrição.
- **Geração de Resumo:** Utiliza a GPT-4o-mini para gerar um resumo estruturado da reunião, incluindo os principais pontos discutidos, acordos/combinados e ações a serem tomadas.
- **Armazenamento e Seleção de Reuniões:** As transcrições e resumos são salvos e podem ser acessados para revisão.

## Tecnologias Utilizadas

- **Streamlit:** Para a criação da interface de usuário.
- **OpenAI API:** Para transcrição de áudio e geração de resumo com GPT-4o-mini.
- **Python:** Linguagem de programação utilizada para desenvolver a aplicação.
- **dotenv:** Para gerenciamento de variáveis de ambiente.

## Como Usar

1. **Instalação das Dependências:**
   - Instale todas as dependências necessárias utilizando `pip install -r requirements.txt`.

2. **Configuração:**
   - Crie um arquivo `.env` na raiz do projeto e adicione sua chave da API da OpenAI (`OPENAI_API_KEY`).

3. **Execução:**
   - Execute o comando `streamlit run seu_arquivo.py` para iniciar a aplicação.
   - Acesse a aplicação através do navegador no endereço indicado pelo Streamlit.

## Estrutura do Projeto

- **Transcrição e Resumo:** A aplicação divide-se em abas para transcrição de áudio, vídeo e visualização das transcrições salvas.
- **Armazenamento:** As transcrições e resumos são salvos em pastas específicas dentro do projeto, permitindo fácil acesso e organização.

## Contribuições

Contribuições são bem-vindas! Para contribuir, por favor, crie um fork do repositório, faça suas alterações e envie um Pull Request.


