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
from moviepy.editor import VideoFileClip

PASTA_ARQUIVOS = Path(__file__).parent / 'arquivos'
PASTA_ARQUIVOS.mkdir(exist_ok=True)
PATAS_TEMP = Path(__file__).parent / 'temp'
PATAS_TEMP.mkdir(exist_ok=True)
ARQUIVO_AUDIO_TEMP = PATAS_TEMP / 'audio_temp.mp3'
ARQUIVO_VIDEO_TEMP = PATAS_TEMP / 'video_temp.mp4'


# Carregar a API Key do arquivo .env
load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")

openai.api_key = api_key


def salva_arquivo(caminho_arquivo, conteudo):
    with open(caminho_arquivo, 'w') as f:
        f.write(conteudo)


def ler_arquivo(caminho_arquivo):
    if caminho_arquivo.exists():
        with open(caminho_arquivo) as f:
            return f.read()
    else:
        return ''


def listar_reunioes():
    lista_reunioes = PASTA_ARQUIVOS.glob('*')
    lista_reunioes = list(lista_reunioes)
    lista_reunioes.sort(reverse=True)
    reunioes_dict = {}

    for pasta_reuniao in lista_reunioes:
        data_reuniao = pasta_reuniao.stem
        ano, mes, dia, hora, min, seg = data_reuniao.split('_')
        reunioes_dict[data_reuniao] = f'{dia}/{mes}/{ano} {hora}:{min}:{seg}'
        titulo = ler_arquivo(pasta_reuniao / 'titulo.txt')
        if titulo != '':
            reunioes_dict[data_reuniao] += f' - {titulo}'
    return reunioes_dict


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

    ultima_transcricao = time.time()
    audio_completo = pydub.AudioSegment.empty()
    audio_chunk = pydub.AudioSegment.empty()
    transcricao = ''

    while True:
        if webrtx_ctx.audio_receiver:
            try:
                frames_de_audio = webrtx_ctx.audio_receiver.get_frames(
                    timeout=1)
            except queue.Empty:
                time.sleep(0.1)
                continue

            audio_completo = adiciona_chunk_audio(
                frames_de_audio, audio_completo)
            audio_chunk = adiciona_chunk_audio(frames_de_audio, audio_chunk)

            if len(audio_chunk) > 0:
                audio_completo.export(
                    pasta_reuniao / 'audio.mp3', format='mp3')
                agora = time.time()
                if agora - ultima_transcricao > 5:  # 5 segundos pode ser maior no futuro
                    ultima_transcricao = agora
                    audio_chunk.export(pasta_reuniao / 'audio_temp.mp3')
                    transcricao_chunck = transcreve_audio(
                        pasta_reuniao / 'audio_temp.mp3')
                    transcricao += transcricao_chunck
                    salva_arquivo(pasta_reuniao /
                                  'transcricao.txt', transcricao)
                    container.markdown(transcricao)

                    audio_chunk = pydub.AudioSegment.empty()

        else:
            break


# TAB SELECAO REUNIAO =================
def tab_selecao_reuniao():
    reunioes_dict = listar_reunioes()

    if len(reunioes_dict) == 0:
        st.markdown('Nenhuma reunião gravada')
        return
    reuniao_selecionada = st.selectbox(
        'selecione a reunião', list(reunioes_dict.values()))
    st.divider()
    reuniao_data = [k for k, v in reunioes_dict.items() if v ==
                    reuniao_selecionada][0]
    pasta_reuniao = PASTA_ARQUIVOS / reuniao_data
    if not (pasta_reuniao / 'titulo.txt').exists():
        st.markdown('Adicione um titulo')
        titulo_reuniao = st.text_input(
            'Titulo da reunião', key='titulo_reuniao_tab_selecao')
        st.button('Salvar titulo',
                  on_click=salvar_titulo,
                  args=(pasta_reuniao, titulo_reuniao), key='salvar_titulo_tab_selecao')
    else:
        titulo = ler_arquivo(pasta_reuniao / 'titulo.txt')
        st.markdown(f'##{titulo}')
        transcricao = ler_arquivo(pasta_reuniao / 'transcricao.txt')
        st.markdown(f'Transcrição: {transcricao}')


def salvar_titulo(pasta_reuniao, titulo):
    salva_arquivo(pasta_reuniao / 'titulo.txt', titulo)

# TAB AUDIO =================


def tab_transcreve_audio():
    st.markdown('tab_audio')
    prompt_input = st.text_input(
        '(Opicional) Digite aqui as correções das palavras erradas', key='input_audio')
    arquivo_audio = st.file_uploader('Selecione o arquivo de audio')
    if not arquivo_audio is None:
        transcricao = openai.audio.transcriptions.create(
            model='whisper-1',
            language='pt',
            response_format='text',
            file=arquivo_audio,
            prompt=prompt_input
        )
        st.write(transcricao)

# TAB VIDEO =================


def print_test():
    st.write('teste botão')


def tab_transcreve_video():
    prompt_input = st.text_input(
        '(Opicional) Digite aqui as correções das palavras erradas', key='input_video')
    arquivo_video = st.file_uploader('Selecione o arquivo de video')
    if not arquivo_video is None:
        with open(ARQUIVO_VIDEO_TEMP, mode='wb') as video_f:
            video_f.write(arquivo_video.read())
        moviepy_video = VideoFileClip(str(ARQUIVO_VIDEO_TEMP))
        moviepy_video.audio.write_audiofile(str(ARQUIVO_AUDIO_TEMP))

        transcricao = transcreve_audio(ARQUIVO_AUDIO_TEMP, prompt_input)

        st.write(transcricao)
        pasta_reuniao2 = PASTA_ARQUIVOS / datetime.now().strftime('%Y_%m_%d_%H_%M_%S')
        pasta_reuniao2.mkdir()
        salva_arquivo(pasta_reuniao2 / 'transcricao.txt', transcricao)
        if not (pasta_reuniao2 / 'titulo.txt').exists():
            st.divider()
            st.markdown('### Adicione um titulo')
            titulo_reuniao = st.text_input(
                'Titulo da reunião', key='titulo_reuniao_tab_video')
            st.button('Salvar titulo', key='salvar_titulo_tab_video',
                      on_click=salvar_titulo,
                      args=(pasta_reuniao2, titulo_reuniao))


# OPENAI =================


def transcreve_audio(caminho_audio, prompt):
    with open(caminho_audio, 'rb') as arquivo_audio:
        transcricao = openai.audio.transcriptions.create(
            model='whisper-1',
            language='pt',
            response_format='text',
            file=arquivo_audio,
            prompt=prompt,
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
    tab_gravar, tab_selecao, tab_audio, tab_video = st.tabs(
        ['Gravar reunião', 'Ver transcrições salvas', 'audio', 'video'])
    with tab_gravar:
        tab_grava_reuniao()
    with tab_selecao:
        tab_selecao_reuniao()
    with tab_audio:
        tab_transcreve_audio()
    with tab_video:
        tab_transcreve_video()


if __name__ == "__main__":
    main()
