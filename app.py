import streamlit as st
from dotenv import load_dotenv, find_dotenv
import openai
import os
from pathlib import Path
from datetime import datetime
import time
from moviepy.editor import VideoFileClip

PASTA_ARQUIVOS = Path(__file__).parent / 'arquivos'
PASTA_ARQUIVOS.mkdir(exist_ok=True)
PATAS_TEMP = Path(__file__).parent / 'temp'
PATAS_TEMP.mkdir(exist_ok=True)
ARQUIVO_AUDIO_TEMP = PATAS_TEMP / 'audio_temp.mp3'
ARQUIVO_VIDEO_TEMP = PATAS_TEMP / 'video_temp.mp4'

# Prompt utilizado para gerar o resumo ===================

PROMPT = ''' 
Faça um resumo do texto delimitado por ####
O texto é a transcrição de uma reunião.
O resumo deve contar com os principais assuntos abordados.
o resumo deve estar em texto corrido.
No final deve ser apresentado todos os acrodos/combinados e ações a serem tomadas.
Apresentação do texto deve ser no formato de bullet points.

formato final:

## Resumo reunião:
- escrever aqui o resumo.

## Acordos/combinados da Reunião:
- acordo 1:
- acordo 2:
- acordo 3:

## Ações a serem tomadas:
- ação 1:
- ação 2:
- ação 3:

## Conclusao:
- escrever aqui a conclusão da reunião.



####{}#### '''

# # Carregar a API Key do arquivo .env
# load_dotenv()
# api_key = os.getenv("OPENAI_API_KEY")

# carrega a api key no streamlit
api_key = st.secrets["OPENAI_API_KEY"]

openai.api_key = api_key

# Funções auxiliares =================


def salvar_titulo(pasta_reuniao, titulo):
    salva_arquivo(pasta_reuniao / 'titulo.txt', titulo)


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

# TAB VIDEO =================


def print_test():
    st.write('teste botão')


def tab_transcreve_video():
    st.subheader("Transcrição de Vídeo")

    # Input para correção de palavras erradas
    prompt_input = st.text_input(
        '(Opicional) Digite aqui as correções das palavras erradas', key='input_video')
    arquivo_video = st.file_uploader('Selecione o arquivo de video', type=[
                                     'mp4', 'avi', 'mov', 'wmv'])

    # IF para o arquivo de vídeo enviado e não ter sido processado (não ter o state video_transcrito)
    if arquivo_video and not hasattr(st.session_state, 'video_transcrito'):
        with open(ARQUIVO_VIDEO_TEMP, mode='wb') as video_f:
            video_f.write(arquivo_video.read())

        # Extrai o audio do video e salva em um arquivo temporário
        moviepy_video = VideoFileClip(str(ARQUIVO_VIDEO_TEMP))
        moviepy_video.audio.write_audiofile(str(ARQUIVO_AUDIO_TEMP))

        # transcreve o audio e mostra a transcrição
        transcricao = transcreve_audio(ARQUIVO_AUDIO_TEMP, prompt_input)

        st.write(transcricao)

        # cria pasta e salvar os arquivos
        pasta_reuniao2 = PASTA_ARQUIVOS / datetime.now().strftime('%Y_%m_%d_%H_%M_%S')
        pasta_reuniao2.mkdir()
        salva_arquivo(pasta_reuniao2 / 'transcricao.txt', transcricao)

        st.success('Transcrição salva com sucesso')
        time.sleep(4)
        # if not (pasta_reuniao2 / 'titulo.txt').exists():
        st.divider()

        # Salva os resultados no state para não precisar processar novamente
        st.session_state.video_transcrito = True
        st.session_state.transcricao = transcricao

    elif hasattr(st.session_state, 'transcricao'):
        mostrar_transcricao = st.write(st.session_state.transcricao)
        mostrar_transcricao
        if st.button('Limpar ', key='limpar_video') and arquivo_video is None:
            # Deleta os estados (state) temporários
            del st.session_state['transcricao']
            del st.session_state['video_transcrito']
            arquivo_video = None
            st.rerun()
        else:
            st.error('Antes de limpar, remova o arquivo')

# TAB AUDIO =================


def tab_transcreve_audio():
    st.subheader("Transcrição de Áudio")

    prompt_input = st.text_input(
        '(Opicional) Digite aqui as correções das palavras erradas', key='input_audio')
    arquivo_audio = st.file_uploader('Selecione o arquivo de audio', type=[
                                     'mp3', 'wav', 'ogg', 'mpga'])
    if arquivo_audio and not hasattr(st.session_state, 'audio_transcrito'):
        transcricao = openai.audio.transcriptions.create(
            model='whisper-1',
            language='pt',
            response_format='text',
            file=arquivo_audio,
            prompt=prompt_input
        )
        st.write(transcricao)

        # cria pasta para salvar os arquivos
        pasta_reuniao3 = PASTA_ARQUIVOS / datetime.now().strftime('%Y_%m_%d_%H_%M_%S')
        pasta_reuniao3.mkdir()
        salva_arquivo(pasta_reuniao3 / 'transcricao.txt', transcricao)
        st.success('Transcrição salva com sucesso')

        time.sleep(4)

        st.divider()

        # Salva os resultados no state para não precisar processar novamente
        st.session_state.audio_transcrito = True
        st.session_state.transcricao_audio = transcricao

    elif hasattr(st.session_state, 'transcricao_audio'):
        st.write(st.session_state.transcricao_audio)
        if st.button('Limpar', key='limpar_audio') and arquivo_audio is None:
            del st.session_state['transcricao_audio']
            del st.session_state['audio_transcrito']
            arquivo_audio = None
            st.rerun()
        else:
            st.error('Antes de limpar, remova o arquivo')


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
        if titulo_reuniao:
            st.button('Salvar titulo',
                      on_click=salvar_titulo,
                      args=(pasta_reuniao, titulo_reuniao), key='salvar_titulo_tab_selecao')
    else:
        titulo = ler_arquivo(pasta_reuniao / 'titulo.txt')
        transcricao = ler_arquivo(pasta_reuniao / 'transcricao.txt')
        resumo = ler_arquivo(pasta_reuniao / 'resumo.txt')
        if resumo == '':
            prompt_personalizado = st.text_area(
                    "Insira as instruções de como a ata da reunião transcrita deve ser gerada:")
            if st.button('Gerar ata'):
                prompt_formatado = f"{prompt_personalizado}\n\n#### {transcricao} ####"
                resumo = def_gerar_resumo(pasta_reuniao, prompt_formatado)
                resumo = ler_arquivo(pasta_reuniao / 'resumo.txt')
            # gerar_resumo = st.button(
                #'Gerar resumo', on_click=def_gerar_resumo, args=(pasta_reuniao,), key='gerar_resumo')
            #resumo = ler_arquivo(pasta_reuniao / 'resumo.txt')
        st.markdown(f'## {titulo}')
        st.markdown(f'{resumo}')
        st.divider()
        st.markdown(f' ### Transcrição:\n {transcricao}')


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


def def_gerar_resumo(pasta_reuniao, prompt_formatado):
    transcricao = ler_arquivo(pasta_reuniao / 'transcricao.txt')
    resumo = chat_openai(mensagem=prompt_formatado)
    salva_arquivo(pasta_reuniao / 'resumo.txt', resumo)
    return resumo


def chat_openai(mensagem, modelo='gpt-4o-mini'):
    mensagens = [{'role': 'user', 'content': mensagem}]

    resposta = openai.chat.completions.create(
        model=modelo,
        messages=mensagens,
    )
    contexto = resposta.choices[0].message.content
    # Retorna apenas o texto da resposta
    return contexto

# def chat_openai(
#     mensagem,
#     modelo='gpt-4o-mini',
# ):
#     mensagens = [{'role': 'user', 'content': mensagem}]

#     resposta = openai.chat.completions.create(
#         model=modelo,
#         messages=mensagens,
#     )
#     return resposta

# MAIN ================


def main():
    st.header("Bem-vindo ao meetAI", divider=True)
    tab_video, tab_audio, tab_selecao = st.tabs(
        ['Vídeo', 'Áudio', 'Ver transcrições salvas'])

    with tab_audio:
        tab_transcreve_audio()
    with tab_video:
        tab_transcreve_video()
    with tab_selecao:
        time.sleep(1)
        tab_selecao_reuniao()


if __name__ == "__main__":
    main()
