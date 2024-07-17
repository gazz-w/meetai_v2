import streamlit as st
from dotenv import load_dotenv, find_dotenv
import openai
import os

# Carregar a API Key do arquivo .env
load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")

openai.api_key = api_key

# TAB GRAVAR REUNIAO =================


def tab_grava_reuniao():
    st.markdown('tab_gravar')


# TAB SELECAO REUNIAO =================
def tab_selecao_reuniao():
    st.markdown('tab_selecao_reuniao')

# OPENAI =================


def trancreve_audio(caminho_audio, language='pt', response_format='text'):
    with open(caminho_audio, 'rb') as arquivo_audio:
        transcricao = openai.audio.transcriptions.create(
            model='whisper-1',
            language=language,
            response_format=response_format,
            file=arquivo_audio,
        )
    return transcricao


def chat_openai(
    mensagem,
    modelo='gpt-3.5-turbo',
):
    mensagens = [{'role': 'user', 'content': mensagem}]

    resposta = openai.chat.completions.create(
        model=modelo,
        messages=mensagens,
    )
    return resposta

# MAIN ================


def main():
    st.header("Bem-vindo ao meetAI", divider=True)
    tab_gravar, tab_selecao = st.tabs(
        ['Gravar reunião', 'Ver transcrições salvas'])
    with tab_gravar:
        tab_grava_reuniao()
    with tab_selecao:
        tab_selecao_reuniao()


if __name__ == "__main__":
    main()
