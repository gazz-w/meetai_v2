import streamlit as st
from dotenv import load_dotenv, find_dotenv
import openai
import os
from pathlib import Path
from datetime import datetime
import time
from moviepy.editor import VideoFileClip
import tempfile


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
load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")

# carrega a api key no streamlit
# api_key = st.secrets["OPENAI_API_KEY"]

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
        '(Opcional) Digite aqui as correções das palavras erradas', key='input_video')
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

# ajustar o código nesse local


def tab_transcreve_audio():
    st.subheader("Transcrição de Áudio")

    prompt_input = st.text_input(
        '(Opcional) Digite aqui as correções das palavras erradas', key='input_audio')
    arquivo_audio = st.file_uploader('Selecione o arquivo de audio', type=[
                                     'mp3', 'wav', 'ogg', 'mpga'])
    if arquivo_audio and not hasattr(st.session_state, 'audio_transcrito'):

        # salva os arquivos temporariamente
        with open(ARQUIVO_AUDIO_TEMP, mode='wb') as audio_file:
            audio_file.write(arquivo_audio.read())

        # faz a transcrição utilizando a nova função
        transcricao = transcreve_audio(ARQUIVO_AUDIO_TEMP, prompt_input)

        st.write(transcricao)

        # transcricao = openai.audio.transcriptions.create(
        # model='whisper-1',
        # language='pt',
        # response_format='text',
        # file=arquivo_audio,
        # prompt=prompt_input
        # )
        # st.write(transcricao)

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
        resumo_path = pasta_reuniao / 'resumo.txt'
        resumo = ler_arquivo(resumo_path)

        if not resumo:
            prompt_personalizado = st.text_area(
                "Insira as instruções de como a ata da reunião transcrita deve ser gerada:")
            if st.button('Gerar ata'):
                prompt_formatado = f"{prompt_personalizado}\n\n#### {transcricao} ####"
                resumo = def_gerar_resumo(pasta_reuniao, prompt_formatado)
                salva_arquivo(resumo_path, resumo)
                resumo = ler_arquivo(resumo_path)
                # resumo = ler_arquivo(pasta_reuniao / 'resumo.txt')
                # gerar_resumo = st.button(
                # 'Gerar resumo', on_click=def_gerar_resumo, args=(pasta_reuniao,), key='gerar_resumo')
                # resumo = ler_arquivo(pasta_reuniao / 'resumo.txt')

        if resumo:
            st.markdown(f'### Ata: \n{resumo}')
            st.download_button(label="Baixar ata", data=resumo,
                               file_name='ata_reuniao.txt', mime='text/plain')

        st.markdown(f'## {titulo}')
        # st.markdown(f'{resumo}')
        st.divider()
        st.markdown(f' ### Transcrição:\n {transcricao}')
        st.download_button(label='Baixar transcrição', data=transcricao,
                           file_name='transcricao.txt', mime='text/plain')  # botão baixar reunião


# OPENAI =================

def transcreve_audio(caminho_audio, prompt):
    def read_in_chunks(file_object, chunk_size=23 * 1024 * 1024):
        """Generator to read a file in chunks of 23MB."""
        while True:
            data = file_object.read(chunk_size)
            if not data:
                break
            yield data

    transcricao = ""

    with open(caminho_audio, 'rb') as arquivo_audio:
        for chunk in read_in_chunks(arquivo_audio):
            with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as temp_chunk:
                temp_chunk.write(chunk)
                temp_file_path = temp_chunk.name

            # Carrega o arquivo temporário para a API do Whisper
            with open(temp_file_path, 'rb') as temp_audio_file:
                response = openai.audio.transcriptions.create(
                    model='whisper-1',
                    language='pt',
                    response_format='text',
                    file=temp_audio_file,
                    prompt=prompt,
                )
                transcricao += response

            # Remove o arquivo temporário após o uso
            os.remove(temp_file_path)

    return transcricao

# def transcreve_audio(caminho_audio, prompt):
   # with open(caminho_audio, 'rb') as arquivo_audio:
    # transcricao = openai.audio.transcriptions.create(
    # model='whisper-1',
    # language='pt',
    # response_format='text',
    # file=arquivo_audio,
    # prompt=prompt,
    #  )
  #  return transcricao


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
