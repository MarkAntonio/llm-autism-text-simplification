# O que é um arquivo .conllu?

Um arquivo **.conllu** é um formato de texto puro baseado em tabulações utilizado em linguística computacional para armazenar **anotações anotadas de texto**. Ele é o formato padrão do projeto **Universal Dependencies (UD)**, que busca criar anotações morfossintáticas e de dependência consistentes para múltiplos idiomas.

### 📋 Estrutura do Arquivo

O formato utiliza codificação UTF-8 e organiza o texto em três tipos de linhas:
1. **Comentários:** Começam com `#` e contêm metadados (como o texto original ou ID da sentença).
2. **Palavras (Anotações):** Linhas com **10 colunas** separadas por tabulações (`\t`), onde cada linha representa um token.
3. **Linhas em branco:** Uma linha vazia que separa uma sentença da outra.

---

### 🗂️ As 10 Colunas Padrão

Cada linha de palavra precisa conter exatamente 10 campos. Caso um campo não possua informação, utiliza-se um sublinhado (`_`):

| ID | Nome da Coluna | Descrição | Exemplo (*gato*) |
| :--- | :--- | :--- | :--- |
| **1** | **ID** | Índice da palavra (começa em 1) ou intervalo para múltiplos tokens. | `2` |
| **2** | **FORM** | Palavra original ou sinal de pontuação como aparece no texto. | `gato` |
| **3** | **LEMMA** | O lema ou forma canônica/dicionário da palavra. | `gato` |
| **4** | **UPOS** | Classe gramatical universal (*Universal Part-of-Speech tag*). | `NOUN` |
| **5** | **XPOS** | Classe gramatical específica do idioma/corpus (opcional). | `_` |
| **6** | **FEATS** | Lista de características morfológicas (gênero, número, tempo, etc.). | `Gender=Masc\|Number=Sing` |
| **7** | **HEAD** | O ID da palavra da qual esta depende (0 se for a raiz da frase). | `3` |
| **8** | **DEPREL** | Relação de dependência universal com a palavra mãe. | `nsubj` (sujeito nominal) |
| **9** | **DEPS** | Relações de dependência secundárias (grafo aprimorado). | `_` |
| **10** | **MISC** | Qualquer outra anotação ou metadado adicional. | `SpaceAfter=No` |

---

### 📝 Exemplo Prático

Abaixo está a representação da frase *"O gato dorme."* formatada em `.conllu`:

```text
# text = O gato dorme.
1   O       o       DET     _   Definite=Def|Gender=Masc|Number=Sing|PronType=Art   2   det     _   _
2   gato    gato    NOUN    _   Gender=Masc|Number=Sing                             3   nsubj   _   _
3   dorme   dormir  VERB    _   Mood=Ind|Number=Sing|Person=3|Tense=Pres|VerbForm=Fin 0   root    _   SpaceAfter=No
4   .       .       PUNCT   _   _                                                   3   punct   _   _
```

---

### 🛠️ Aplicações Principais
* **Treinamento de Modelos de IA:** Utilizado para treinar analisadores sintáticos (*parsers*), etiquetadores (*taggers*) e ferramentas de Processamento de Linguagem Natural (PLN).
* **Padronização Interlinguística:** Permite que pesquisadores apliquem os mesmos algoritmos e análises gramaticais em mais de 100 idiomas diferentes de forma unificada.

---

### 🔗 Fontes e Referências
* **CoNLL-U Format Documentation:** [Universal Dependencies - CoNLL-U Format](https://universaldependencies.org)
* **Universal Dependencies Project:** [Universal Dependencies Official Website](https://universaldependencies.org)

