import google.generativeai as genai
import os
import gradio
import time
import mimetypes

from google.api_core.exceptions import InvalidArgument
from special_tools import atualizar_status_pedido, gerar_cupom_desconto, registrar_reclamacao

# Configurar a chave da API
genai.configure(api_key=os.environ["GEMINI_API_KEY"])

# Definir o prompt inicial
base_prompt = (
    "Você é uma assistente de atendimento ao cliente personalizado."
    "Você tem acesso a funcões que realizam tarefas específicas, como: "
    "Atualizar o status de um pedido"
    "Gerar um cupom de desconto"
    "Chame as funções quando achar que deve, mas nunca exponha o código delas. "
    "Assuma que a pessoa é amigável e ajude-a a entender o que aconteceu se algo der errado "
    "ou se você precisar de mais informações. Não esqueça de, de fato, chamar as funções."
    )

# Criar o modelo com o prompt inicial
model = genai.GenerativeModel(
    model_name="gemini-1.5-flash",
    tools=[atualizar_status_pedido, gerar_cupom_desconto, registrar_reclamacao],
    system_instruction=base_prompt,
)

# Inicializar o chat
chat = model.start_chat(
    enable_automatic_function_calling=True,
)

def assemble_prompt(message):
    prompt = [message["text"]]
    uploaded_files = upload_files(message)
    prompt.extend(uploaded_files)
    return prompt

def is_valid_file(file_path):
    mime_type, _ = mimetypes.guess_type(file_path)
    # Aceitar apenas imagens ou PDFs
    return mime_type and (mime_type.startswith('image/') or mime_type == 'application/pdf')
    
def upload_files(message):
    uploaded_files = []
    if "files" in message and message["files"]:
        for file_path in message["files"]:
            if not is_valid_file(file_path):
                raise ValueError("Tipo de arquivo não suportado. Por favor, envie um arquivo de imagem ou PDF.")
            uploaded_file = genai.upload_file(file_path)
            start_time = time.time()
            while uploaded_file.state.name == "PROCESSING":
                time.sleep(5)
                uploaded_file = genai.get_file(uploaded_file.name)
                if time.time() - start_time > 60:  # Timeout após 1 minuto
                    raise TimeoutError("O processamento do arquivo demorou mais do que o esperado.")
            uploaded_files.append(uploaded_file)
    return uploaded_files

def gradio_wrapper(message, _history):
    try:
        prompt = assemble_prompt(message)
        response = chat.send_message(prompt)
    except (InvalidArgument, TimeoutError, ValueError) as e:
        response = handle_error(e)
    except Exception as e:
        response = handle_unexpected_error(e)
    return response.text

def handle_error(e):
    return chat.send_message("Desculpe, o tipo de arquivo enviado não é suportado. Por favor, envie um arquivo de imagem ou PDF.")


def handle_unexpected_error(e):
    return chat.send_message(f"Ocorreu um erro inesperado. Por favor, tente novamente mais tarde. Erro: {str(e)}")

# Crie e lance a interface do chat com suporte a arquivos
chat_interface = gradio.ChatInterface(
   fn=gradio_wrapper,
   title="Assistente de Atendimento ao Cliente",
   multimodal=True
)

# Inicie a interface
chat_interface.launch()
