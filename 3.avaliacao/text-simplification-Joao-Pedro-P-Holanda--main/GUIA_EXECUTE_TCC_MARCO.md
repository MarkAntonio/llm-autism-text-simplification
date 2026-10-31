# Guia de execução de `execute_tcc_marco.py`

Este guia explica como executar o script para calcular métricas dos documentos simplificados e como preparar os arquivos para evitar erros.

## 1. Preparar o ambiente

Execute os comandos a partir da raiz do repositório, isto é, da pasta que contém `execute_tcc_marco.py`, `pyproject.toml` e a pasta `data/`.

Com `uv`, instale as dependências do projeto:

```bash
uv sync
```

Depois, execute o script:

```bash
uv run python execute_tcc_marco.py
```

Se você já ativou um ambiente virtual e instalou as dependências nele, também pode executar:

```bash
python execute_tcc_marco.py
```

Os caminhos de entrada e saída usados pelo script são relativos à pasta atual. Por isso, execute-o na raiz do repositório.

## 2. Organizar os arquivos de entrada

O script procura recursivamente arquivos Markdown (`.md`) em:

```text
data/full_simplified_docs/
```

Organize os documentos por modelo, por exemplo:

```text
data/
├── full_simplified_docs/
│   └── llama_3_2_3B/
│       ├── 3.chunked_lei_13977_stripped.md
│       ├── 5.chunked_manual_dsm5_stripped.md
│       └── ...
└── full_original_docs/
    └── ...
```

Para cada Markdown simplificado que será avaliado, deve existir o arquivo `.conllu` correspondente, no mesmo diretório e com o mesmo nome-base:

```text
3.chunked_lei_13977_stripped.md
3.chunked_lei_13977_stripped.conllu
```

O extrator de métricas morfossintáticas lê o `.conllu` substituindo a extensão `.md` do caminho do Markdown. Se o par não existir ou tiver outro nome, a execução poderá falhar.

Além dos arquivos simplificados, o script atualmente verifica se existe pelo menos um arquivo `.conllu` em `data/full_original_docs/`. Essa verificação é feita mesmo quando o cálculo de métricas dos originais está comentado.

## 3. O que o script executa

Por padrão, `execute_tcc_marco.py`:

1. Localiza todos os arquivos `.md` em `data/full_simplified_docs/`, incluindo subpastas.
2. Exibe a lista de arquivos encontrados.
3. Executa `extract_morphosyntactic_metrics_simplified` sobre esses arquivos.
4. Grava as métricas em:

   ```text
   result/ud-pipe/generated-simplified.csv
   ```

As chamadas de métricas de legibilidade e de métricas para os documentos originais estão comentadas no script; portanto, não são executadas por padrão.

## 4. Identificação do modelo em `generated_with`

O campo `generated_with` é inferido a partir das partes do caminho do arquivo, especialmente do nome da pasta do modelo. As opções reconhecidas são definidas em `ModelOptions`, em `schema.py`. Para que o modelo seja identificado, o nome da pasta deve corresponder a uma dessas opções.

No código atual, `llama_3_2_3B` é uma das opções reconhecidas. Nomes de pasta diferentes das opções definidas, como variações de grafia, underscores ou capitalização, podem resultar em `generated_with` vazio no CSV. Confira e mantenha os nomes das pastas e as opções de `ModelOptions` consistentes.

No CSV, `model` representa o modelo usado pelo analisador UD, e não o modelo generativo. O modelo generativo, quando reconhecido pelo caminho, aparece em `generated_with`.

## 5. Identificadores e nomes dos documentos

O nome do documento (`name`) vem do nome do arquivo sem extensão. O identificador (`id`) é inferido pelo código a partir do prefixo numérico seguido de ponto, quando presente. Por exemplo:

```text
3.chunked_lei_13977_stripped.md
```

produz o nome `3.chunked_lei_13977_stripped` e o identificador `3`.

## 6. Verificações antes de executar

- [ ] Estou executando o comando na raiz do repositório.
- [ ] Existe pelo menos um arquivo `.md` em `data/full_simplified_docs/`.
- [ ] Cada `.md` a ser avaliado tem um `.conllu` correspondente no mesmo diretório.
- [ ] Existe pelo menos um `.conllu` em `data/full_original_docs/`, conforme a verificação atual do script.
- [ ] O nome da pasta do modelo coincide com uma opção em `ModelOptions`, se eu precisar preencher `generated_with`.
- [ ] O diretório `result/` é gravável.

## 7. Comportamento do arquivo de resultados

O arquivo `result/ud-pipe/generated-simplified.csv` é aberto em modo de escrita (`w`) pela configuração atual do pipeline. Portanto, uma nova execução substitui os resultados anteriores desse arquivo. Copie ou renomeie o CSV antes de executar novamente se precisar conservar uma versão anterior.

## 8. Mensagens de erro úteis

- **“Nenhum arquivo .md encontrado em ./data”**: não há Markdown em `data/full_simplified_docs/` (ou o comando foi executado a partir de outra pasta).
- **Falha ao abrir um `.conllu`**: verifique se o arquivo existe ao lado do `.md` correspondente e se ambos têm o mesmo nome-base.
- **`generated_with` vazio**: o nome da pasta do modelo não corresponde a nenhuma opção configurada em `ModelOptions`.
- **Erro sobre arquivos originais**: o script exige ao menos um `.conllu` em `data/full_original_docs/`, embora essa entrada não seja usada pela chamada ativa de métricas simplificadas.

