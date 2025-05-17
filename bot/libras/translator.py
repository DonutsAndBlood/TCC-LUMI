from .client import traduzir_para_glosa, requisitar_video, checar_status, baixar_video
import time

def gerar_video_libras(texto, caminho_saida="video_libras.mp4"):
    glosa = traduzir_para_glosa(texto)
    id_video = requisitar_video(glosa)

    # Aguarda até estar pronto (pode ser assíncrono e com timeout)
    for _ in range(10):
        status = checar_status(id_video)
        if status["status"] == "DONE":
            return baixar_video(id_video, caminho_saida)
        time.sleep(2)

    raise Exception("Tempo de espera excedido para geração do vídeo.")
