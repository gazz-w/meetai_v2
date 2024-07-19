import streamlit as st
from dotenv import load_dotenv, find_dotenv
import openai
import os
from streamlit_webrtc import WebRtcMode, webrtc_streamer
from pathlib import Path
from datetime import datetime
import time
import queue
import pydub

PASTA_ARQUIVOS = Path(__file__).parent / 'arquivos'
PASTA_ARQUIVOS.mkdir(exist_ok=True)

# Carregar a API Key do arquivo .env
load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")

openai.api_key = api_key


# TAB GRAVAR REUNIAO =================

def adiciona_chunk_audio(frames_de_audio, audio_chunk):
    for frame in frames_de_audio:
        sound = pydub.AudioSegment(
            data=frame.to_ndarray().tobytes(),
            sample_width=frame.format.bytes,
            frame_rate=frame.sample_rate,
            channels=len(frame.layout.channels),
        )

        audio_chunk += sound
    return audio_chunk


def tab_grava_reuniao():
    st.markdown('tab_gravar')
    webrtx_ctx = webrtc_streamer(
        key="recebe_audio",
        mode=WebRtcMode.SENDONLY,
        audio_receiver_size=1024,
        media_stream_constraints={"video": False, "audio": True},
    )

    if not webrtx_ctx.state.playing:
        st.markdown('Não está rodando')
        return

    container = st.empty()
    container.markdown('Comece a falar')
    pasta_reuniao = PASTA_ARQUIVOS / datetime.now().strftime('%Y_%m_%d_%H_%M_%S')
    pasta_reuniao.mkdir()
    audio_chunk = pydub.AudioSegment.empty()

    while True:
        if webrtx_ctx.audio_receiver:
            container.markdown('Gravando audio...')
            try:
                frames_de_audio = webrtx_ctx.audio_receiver.get_frames(
                    timeout=1)
            except queue.Empty:
                time.sleep(0.1)
                continue

            audio_chunk = adiciona_chunk_audio(frames_de_audio, audio_chunk)

            if len(audio_chunk) > 0:
                audio_chunk.export(
                    pasta_reuniao / 'audio_temp.mp3', format='mp3')

        else:
            break


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
