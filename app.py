import google.generativeai as genai
import os
import gradio
import time

from google.api_core.exceptions import InvalidArgument

# configurar a chave da API
genai.configure(api_key=os.environ["GEMINI_API_KEY"])

# definir a o prompt inicial
base_prompt = ("Você é uma assistente de atendimento ao cliente.")

# criar o modelo com o prompt inicial
model = genai.GenerativeModel(
    model_name="gemini-1.5-flash",
    system_instruction=base_prompt,
)

# inicializar o chat
chat = model.start_chat()

def assemble_prompt(message):
   prompt = [message["text"]]
   uploaded_files = upload_files(message)
   prompt.extend(uploaded_files)
   return prompt
    
def upload_files(message):
    uploaded_files = []
    # print(type(message["files"]), message["files"])
    if "files" in message and message["files"]:
        for file_path in message["files"]:
            uploaded_file = genai.upload_file(file_path)
            start_time = time.time()
            while uploaded_file.state.name == "PROCESSING":
                time.sleep(5)
                uploaded_file = genai.get_file(uploaded_file.name)
                if time.time() - start_time > 60:
                    raise TimeoutError("O processamento do arquivo demorou mais do que o esperado.")
            uploaded_files.append(uploaded_file)
    return uploaded_files

def gradio_wrapper(message, _history):
   prompt = assemble_prompt(message)
   try:
       response = chat.send_message(prompt)
   except InvalidArgument as e:
       response = chat.send_message(
           f"O usuário te enviou um arquivo para você ler e obteve o erro: {e}. "
           "Pode explicar o que houve e dizer quais tipos de arquivos você "
           "dá suporte? Assuma que a pessoa não sabe programação e "
           "não quer ver o erro original. Explique de forma simples e concisa."
       )
   return response.text


# Crie e lance a interface do chat com suporte a arquivos
chat_interface = gradio.ChatInterface(
   fn=gradio_wrapper,
   title="Assistente de Atendimento ao Cliente",
   multimodal=True
)
# Inicie a interface
chat_interface.launch()