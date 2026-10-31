from pathlib import Path


def limpar_nomes_arquivos(diretorio, termo_extra):
  caminho = Path(diretorio)

  if not caminho.exists() or not caminho.is_dir():
    print(f"O diretório '{diretorio}' não foi encontrado.")
    return

  # Termos que serão removidos dos nomes dos arquivos
  termos_para_remover = ["", termo_extra]

  contador = 0
  for arquivo in caminho.iterdir():
    if arquivo.is_file():
      nome_antigo = arquivo.name
      nome_novo = nome_antigo

      # Remove cada termo da lista
      for termo in termos_para_remover:
        if termo:
          # Substitui o termo por vazio
          nome_novo = nome_novo.replace(termo, "")

      # Limpeza básica para evitar espaços duplos deixados pela remoção
      nome_novo = nome_novo.replace("  ", " ").strip()

      # Se o nome mudou, realiza a renomeação
      if nome_novo != nome_antigo:
        novo_caminho = arquivo.with_name(nome_novo)
        arquivo.rename(novo_caminho)
        print(f"Renomeado: {nome_antigo} -> {nome_novo}")
        contador += 1

  print(f"\nProcesso concluído! Total de arquivos renomeados: {contador}")


# --- EXEMPLO DE USO ---
# Substitua pelo caminho da sua pasta e pelo termo extra que deseja remover
DIRETORIO_ALVO = "/home/marco-santos/Documents/1.Pré-pcc/3.Execução/2.code/3.avaliacao/text-simplification-Joao-Pedro-P-Holanda--main/data/full_simplified_docs/llama-3.2-3B-Instruct-guff"
TERMO_ADICIONAL = "chunked_"

limpar_nomes_arquivos(DIRETORIO_ALVO, TERMO_ADICIONAL)