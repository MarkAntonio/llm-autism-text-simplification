import os
from datalab_sdk import DatalabClient, ConvertOptions

# O cliente puxa automaticamente a variável de ambiente DATALAB_API_KEY
client = DatalabClient(api_key="m_8iuB3p5gJPPUfpgRPRiHXBVH5VxUI08wZuxXBf_Lg")

options = ConvertOptions(
    mode="balanced", # fast | balanced | accurate (tables, etc)
    disable_image_captions=True, # Faz com que o modelo não gere descrição para imagens
    extras="extract_links"  # Extrai e insere o link no markdown.
)



# 10.file_name = "10.cadernos-pedagogicos-pneei-vol-6-completo" OK
file_name = "7.BENEFÍCIO DE PRESTAÇÃO CONTINUADA DE ASSISTÊNCIA SOCIAL (BPC-LOAS)"
docs_folder = "/home/marco.santos/Documentos/0.Pessoal/1.Pré-pcc/5.Execução/documentos curados/"

FILE_PATH = docs_folder + file_name + ".pdf"
OUTPUT_PATH = docs_folder + "markdown/" + file_name + "/"


print(" Iniciando conversão...")
# Executa a conversão. Você pode escolher os formatos: "markdown", "html" ou "json"

os.makedirs(OUTPUT_PATH, exist_ok=True)

response = client.convert(
    file_path=FILE_PATH,
    save_output = OUTPUT_PATH+file_name,
    options=options
)
print(f"RESPONSE: {response}")

# # Verifica se a conversão foi bem-sucedida e baixa o arquivo
# if response.success:
#     # O SDK já traz o conteúdo convertido diretamente na resposta
#     conteudo_convertido = response.markdown
    
#     # Salva o arquivo baixado localmente no seu computador
#     with open(arquivo_saida, "w", encoding="utf-8") as f:
#         f.write(conteudo_convertido)
        
#     print(f"Sucesso! Arquivo convertido e salvo em: {arquivo_saida}")
# else:
#     print(f"Falha na conversão: {response.error}")
