import os
import time
from datalab_sdk import DatalabClient

# 1. Inicializa o cliente (ele busca automaticamente a variável de ambiente DATALAB_API_KEY)
client = DatalabClient(api_key="m_8iuB3p5gJPPUfpgRPRiHXBVH5VxUI08wZuxXBf_Lg")


# 2. Inicia a execução do seu Pipeline específico
print("Iniciando o processamento do documento...")

file_name = "4.cid_11_en_reduzido.pdf"
FILE_PATH = "./documentos curados/" + file_name

execution = client.run_pipeline(
    pipeline_id="pl_tyVkrjzHc6it",
    version=1,
    file_path=FILE_PATH,
)

print(execution)
print(f"Pipeline iniciado! ID de Execução: {execution.execution_id}")

# 3. Loop para monitorar (Poll) até o processamento terminar
while True:
    status_response = client.get_pipeline_execution(execution.execution_id)
    status = status_response.status
    print(f"Status atual: {status}")
    
    if status == "completed":
        print("Processamento concluído com sucesso!")
        break
    elif status == "failed":
        raise Exception("O processamento do pipeline falhou.")
        
    time.sleep(5)  # Aguarda 5 segundos antes de checar novamente

# 4. Baixar e salvar os resultados (incluindo imagens extraídas)
# O SDK da Datalab organiza as imagens renomeadas dentro do diretório de saída
OUTPUT_DIRECTORY = "./resultado_pipeline" + file_name
os.makedirs(OUTPUT_DIRECTORY, exist_ok=True)

# Coleta os arquivos gerados e salva no disco
# Se o seu pipeline incluiu o passo de conversão (Marker/Chandra), as imagens estarão aqui
result = client.get_step_result(execution.execution_id, step_index=1)
print(f"Result {result}")
print(f"File download URL {client.get_file_download_url()}")
      
print(f"Pronto! Suas imagens renomeadas e arquivos estão salvos em: {os.path.abspath(OUTPUT_DIRECTORY)}")

with open(OUTPUT_DIRECTORY, "w") as file:
    file.
