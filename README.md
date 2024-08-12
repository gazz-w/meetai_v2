
# pt-br: meetAI - Transcrição e Resumo de Reuniões

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
   - Caso deseje subir no streamlit é necessário criar a adicionar a key no "Secrets" do streamlit.
   - Atenção na linha 50 do `app.py` para descomentar a configuração da key conforme utilização.

3. **Execução:**
   - Execute o comando `streamlit run seu_arquivo.py` para iniciar a aplicação.
   - Acesse a aplicação através do navegador no endereço indicado pelo Streamlit.

## Estrutura do Projeto

- **Transcrição e Resumo:** A aplicação divide-se em abas para transcrição de áudio, vídeo e visualização das transcrições salvas.
- **Armazenamento:** As transcrições e resumos são salvos em pastas específicas dentro do projeto, permitindo fácil acesso e organização.

## Contribuições

Contribuições são bem-vindas! Para contribuir, por favor, crie um fork do repositório, faça suas alterações e envie um Pull Request.

---------------------------------------------------------------------------------------------------------------------------------------------------------


# en-us: meetAI - Meeting Transcription and Summarization

meetAI is a Streamlit-based application that leverages the OpenAI API to transcribe and summarize meetings. The application allows users to upload audio and video files, transcribe spoken content, and generate a summary of key points discussed, agreements made, and actions to be taken using GPT-4.

## Features
- Audio and Video Transcription: Upload audio files (mp3, wav, ogg, mpga) and video files (mp4) for transcription.
- Summary Generation: Uses GPT-4 to generate a structured summary of the meeting, including key points discussed, agreements made, and actions to be taken.
- Meeting Storage and Review: Transcriptions and summaries are saved and can be accessed for future review.

## Technologies Used
- Streamlit: For creating the user interface.
- OpenAI API: For audio transcription and summary generation using GPT-4.
- Python: The programming language used to develop the application.
- dotenv: For managing environment variables.

## How to Use

Installation
1. Install all necessary dependencies by running:
   pip install -r requirements.txt

Configuration
1. Create a .env file at the root of the project and add your OpenAI API key:
   OPENAI_API_KEY=your_openai_api_key
2. If you plan to deploy the application on Streamlit, make sure to add the API key to the "Secrets" section in Streamlit.
3. Pay attention to line 50 in app.py to uncomment the API key configuration according to your usage.

Execution
1. Run the application with the following command:
   streamlit run your_file.py
2. Access the application through the web browser at the address provided by Streamlit.

## Project Structure
- Transcription and Summarization: The application is divided into tabs for audio transcription, video transcription, and viewing saved transcriptions.
- Storage: Transcriptions and summaries are saved in specific folders within the project, allowing for easy access and organization.

## Contributions
Contributions are welcome! To contribute, please fork the repository, make your changes, and submit a Pull Request.
