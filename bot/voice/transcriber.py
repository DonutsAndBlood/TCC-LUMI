import speech_recognition as sr

def transcribe_audio(caminho_arquivo):
    recognizer  = sr.Recognizer()

    print(caminho_arquivo)

    try:
        with sr.AudioFile(caminho_arquivo) as source:
            audio = recognizer.record(source)

        texto = recognizer.recognize_google(audio, language="pt-BR");
        return texto
    
    except sr.UnknownValueError:
        print("Não consegui entender o áudio.")
        return None
    except sr.RequestError as e:
        print(f"Erro ao solicitar resultados do serviço de reconhecimento de fala: {e}")
        return None
    except Exception as e:
        print(f"Ocorreu um erro inesperado: {e}")
        return None

    