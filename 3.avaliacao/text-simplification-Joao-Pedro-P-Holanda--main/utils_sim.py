import re
import numpy as np
from typing import List, Dict, Tuple
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import traceback

# -------------------------------------------------------------------
# 1) Tentativa de importar Ulysses / segmentador jurídico
# -------------------------------------------------------------------
try:
    import segmentador
    HAS_ULYSSES = True
except Exception as e:
    traceback.print_exception(e)
    HAS_ULYSSES = False


# -------------------------------------------------------------------
# 2) Utilitários básicos
# -------------------------------------------------------------------
def normalize_spaces(text: str) -> str:
    if not text:
        return ""
    text = re.sub(r"\r\n?", "\n", text)
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n\s*\n+", "\n\n", text)
    return text.strip()


def split_sentences_generic(text: str) -> List[str]:
    """
    Quebra em frases via regex. Funciona bem para textos corridos.
    """
    if not text:
        return []
    text = normalize_spaces(text)
    chunks = re.split(r"(?<=[.!?])\s+|\n+", text)
    return [c.strip() for c in chunks if c and c.strip()]


def split_paragraphs(text: str) -> List[str]:
    """
    Quebra em parágrafos.
    """
    if not text:
        return []
    text = normalize_spaces(text)
    paragraphs = re.split(r"\n\s*\n+", text)
    return [p.strip() for p in paragraphs if p and p.strip()]


def split_legal_blocks(text: str) -> List[str]:
    """
    Segmentação jurídica geral:
    - Artigo
    - Parágrafo
    - Inciso
    - Alínea
    """
    if not text:
        return []

    text = normalize_spaces(text)
    # divide considerando marcadores legais
    parts = re.split(
        r"(?=(?:Art\.|Artigo|§|Parágrafo|Parag\.|Inciso|Item|Alínea|Inc\.) )",
        text,
    )

    blocks = []
    for p in parts:
        p = p.strip()
        if p:
            blocks.append(p)

    # fallback se não encontrou nada útil
    if len(blocks) == 1 and len(text) > 200:
        return split_sentences_generic(text)

    return blocks


def split_administrative_blocks(text: str) -> List[str]:
    """
    Documento administrativo: prioriza parágrafos e headings.
    """
    if not text:
        return []

    text = normalize_spaces(text)

    # separa por títulos/headers
    parts = re.split(r"(?m)^(?:[A-ZÁÉÍÓÚÃÕÂÊÔÇ0-9][^\\n]{0,120})\s*$", text)
    blocks = []
    for p in parts:
        p = p.strip()
        if p:
            blocks.append(p)

    if len(blocks) == 1:
        # se não encontrar cabeçalhos, usa parágrafos
        return split_paragraphs(text)

    return blocks


def read_stripped_markdown_file(path: Path) -> str:
    with open(path, "r", encoding="utf-8") as file:
        text = "".join(file.readlines())

    return text


def split_medical_blocks(text: str) -> List[str]:
    """
    Texto médico: primeiro tenta paragrafos, depois sentenças.
    """
    if not text:
        return []

    text = normalize_spaces(text)

    paragraphs = split_paragraphs(text)
    if len(paragraphs) > 1:
        return paragraphs

    return split_sentences_generic(text)


# -------------------------------------------------------------------
# 3) Ulysses wrapper
# -------------------------------------------------------------------
def ulysses_segment(text: str) -> List[str]:
    """
    Adaptador para o segmentador Ulysses, se existir.
    """
    if not HAS_ULYSSES:
        return split_legal_blocks(text)

    try:
        # ajuste conforme o pacote real do seu projeto
        # algumas implementações usam BERTSegmenter() e chamam instância.
        # outras usam função direta.
        
        seg = segmentador.BERTSegmenter(
            uri_model="./cache/models/4_layer_6000_vocab_size_bert_v3",
            uri_tokenizer="./cache/tokenizers/6000_subword_tokenizer",
            local_files_only=True,
            device="cpu",
        )
        result = seg(text)
        if isinstance(result, list):
            return [r.strip() for r in result if r and r.strip()]
        if isinstance(result, str):
            return split_legal_blocks(result)
    except Exception as e:
        traceback.print_exception(e)

    return split_legal_blocks(text)


# -------------------------------------------------------------------
# 4) Escolha do segmentador por tipo de documento
# -------------------------------------------------------------------
def choose_segmenter(file_path: str, text: str) -> List[str]:

    if file_path in {
        "data/full_original_docs/3.lei_13977_stripped.md",
        "data/full_simplified_docs/gemma-4-E2B-it-qat-q4.0-gguf/3.lei_13977_stripped.md",
        "data/full_simplified_docs/llama-3.2-3B-Instruct-guff/3.lei_13977_stripped.md",
        "data/full_simplified_docs/qwen2.5-7b-instruct-q4_k_m-gguf/3.lei_13977_stripped.md"}:
        if HAS_ULYSSES: 
            return ulysses_segment(text)
        else:
            print("Warning: o segmentador Ulysses não foi carrregado corretamente, o método split_legal_blocks por Regex será utlizado")
            split_legal_blocks(text)
            

    if file_path in {
        "data/full_original_docs/7.LOAS_stripped.md",
        "data/full_simplified_docs/gemma-4-E2B-it-qat-q4.0-gguf/7.LOAS_stripped.md",
        "data/full_simplified_docs/llama-3.2-3B-Instruct-guff/7.LOAS_stripped.md",
        "data/full_simplified_docs/qwen2.5-7b-instruct-q4_k_m-gguf/7.LOAS_stripped.md"
    }:
        return split_administrative_blocks(text)

    if file_path in {
        "data/full_original_docs/5.manual_dsm5_stripped.md",
        "data/full_simplified_docs/gemma-4-E2B-it-qat-q4.0-gguf/5.manual_dsm5_stripped.md",
        "data/full_simplified_docs/llama-3.2-3B-Instruct-guff/5.manual_dsm5_stripped.md",
        "data/full_simplified_docs/qwen2.5-7b-instruct-q4_k_m-gguf/5.manual_dsm5_stripped.md"
    }:
        return split_medical_blocks(text)

    # default: texto corrido / genérico
    raise Exception("O caminho não foi encontrado")


# -------------------------------------------------------------------
# 5) Similaridade semântica
# -------------------------------------------------------------------
def compute_similarity_score(
    text_a: str,
    text_b: str,
    doc_type: str = "generic",
    # model_name: str = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2",
    # model_name: str = "./cache/models/legal_sroberta_v1",
    #  model_name: str = "BAAI/bge-m3",
    model_name: str = "tardellirs/embeddinggemma-pt-br"
) -> float:
    """
    Retorna um score entre 0 e 1.
    """
    
    chunks_a = choose_segmenter(doc_type, text_a)
    chunks_b = choose_segmenter(doc_type, text_b)
    print("NUMBER OF ORIGINAL CHUNKS: ", len(chunks_a))
    print("NUMBER OF SIMPLIFIED CHUNKS: ", len(chunks_b))

    if not chunks_a and not chunks_b:
        return 0.0
    if not chunks_a or not chunks_b:
        return 0.0

    model = SentenceTransformer(model_name)
    emb_a = model.encode(
        chunks_a,
        convert_to_numpy=True,
        normalize_embeddings=True,
        show_progress_bar=False,
    )
    emb_b = model.encode(
        chunks_b,
        convert_to_numpy=True,
        normalize_embeddings=True,
        show_progress_bar=False,
    )

    sim_matrix = cosine_similarity(emb_a, emb_b)

    weights_a = np.array([len(c.split()) for c in chunks_a], dtype=float)
    weights_b = np.array([len(c.split()) for c in chunks_b], dtype=float)

    max_a = sim_matrix.max(axis=1)
    max_b = sim_matrix.max(axis=0)

    orig_to_simp = float(np.average(max_a, weights=weights_a))
    simp_to_orig = float(np.average(max_b, weights=weights_b))

    if orig_to_simp + simp_to_orig == 0:
        return 0.0

    # Média Harmônica
    return float(
        2 * orig_to_simp * simp_to_orig / (orig_to_simp + simp_to_orig)
    )


# -------------------------------------------------------------------
# 6) Exemplo de uso
# -------------------------------------------------------------------
if __name__ == "__main__":
    print(choose_segmenter("data/full_original_docs/3.lei_13977_stripped.md", read_stripped_markdown_file("data/full_original_docs/3.lei_13977_stripped.md")))
#     original = """
# Presidência da RepúblicaSecretaria-GeralSubchefia para Assuntos Jurídicos

# LEI Nº 13.977, DE 8 DE JANEIRO DE 2020

# Altera a Lei nº 12.764, de 27 de dezembro de 2012 (Lei Berenice Piana), e a Lei nº 9.265, de 12 de fevereiro de 1996, para instituir a Carteira de Identificação da Pessoa com Transtorno do Espectro Autista (Ciptea), e dá outras providências.

# Down

# O PRESIDENTE DA REPÚBLICA Faço saber que o Congresso Nacional decreta e eu sanciono a seguinte Lei:

# Art. 1º Esta Lei, denominada “Lei Romeo Mion”, altera a Lei nº 12.764, de 27 de dezembro de 2012 (Lei Berenice Piana), e a Lei nº 9.265, de 12 de fevereiro de 1996 (Lei da Gratuidade dos Atos de Cidadania), para criar a Carteira de Identificação da Pessoa com Transtorno do Espectro Autista (Ciptea), de expedição gratuita.

# Art. 2º A Lei nº 12.764, de 27 de dezembro de 2012 \(Lei Berenice Piana\), passa a vigorar com as seguintes alterações:

# “Art. 1º .....
# .....

# § 3º Os estabelecimentos públicos e privados referidos na Lei nº 10.048, de 8 de novembro de 2000, poderão valer-se da fita quebra-cabeça, símbolo mundial da conscientização do transtorno do espectro autista, para identificar a prioridade devida às pessoas com transtorno do espectro autista.” (NR)

# “Art. 3º .....
# .....

# § 1º .....

# § 2º (VETADO).” (NR)

# “Art. 3º-A. É criada a Carteira de Identificação da Pessoa com Transtorno do Espectro Autista (Ciptea), com vistas a garantir atenção integral, pronto atendimento e prioridade no atendimento e no acesso aos serviços públicos e privados, em especial nas áreas de saúde, educação e assistência social.

# § 1º A Ciptea será expedida pelos órgãos responsáveis pela execução da Política Nacional de Proteção dos Direitos da Pessoa com Transtorno do Espectro Autista dos Estados, do Distrito Federal e dos Municípios, mediante requerimento, acompanhado de relatório médico, com indicação do código da Classificação Estatística Internacional de Doenças e Problemas Relacionados à Saúde (CID), e deverá conter, no mínimo, as seguintes informações:

# nome completo, filiação, local e data de nascimento, número da carteira de identidade civil, número de inscrição no Cadastro de Pessoas Físicas (CPF), tipo sanguíneo, endereço residencial completo e número de telefone do identificado;

# fotografia no formato 3 (três) centímetros (cm) x 4 (quatro) centímetros (cm) e assinatura ou impressão digital do identificado;

# nome completo, documento de identificação, endereço residencial, telefone e e-mail do responsável legal ou do cuidador;

# identificação da unidade da Federação e do órgão expedidor e assinatura do dirigente responsável.

# § 2º Nos casos em que a pessoa com transtorno do espectro autista seja imigrante detentor de visto temporário ou de autorização de residência, residente fronteiriço ou solicitante de refúgio, deverá ser apresentada a Cédula de Identidade de Estrangeiro (CIE), a Carteira de Registro Nacional Migratório (CRNM) ou o Documento Provisório de Registro Nacional Migratório (DPRNM), com validade em todo o território nacional.

# § 3º A Ciptea terá validade de 5 (cinco) anos, devendo ser mantidos atualizados os dados cadastrais do identificado, e deverá ser revalidada com o mesmo número, de modo a permitir a contagem das pessoas com transtorno do espectro autista em todo o território nacional.

# § 4º Até que seja implementado o disposto no caput deste artigo, os órgãos responsáveis pela execução da Política Nacional de Proteção dos Direitos da Pessoa com Transtorno do Espectro Autista deverão trabalhar em conjunto com os respectivos responsáveis pela emissão de documentos de identificação, para que sejam incluídas as necessárias informações sobre o transtorno do espectro autista no Registro Geral (RG) ou, se estrangeiro, na Carteira de Registro Nacional Migratório (CRNM) ou na Cédula de Identidade de Estrangeiro (CIE), válidos em todo o território nacional.”

# Art. 3º O caput do art. 1º da Lei nº 9.265, de 12 de fevereiro de 1996 \(Lei da Gratuidade dos Atos de Cidadania\), passa a vigorar acrescido do seguinte inciso VII:

# “Art. 1º ..... 
# .....

# o requerimento e a emissão de documento de identificação específico, ou segunda via, para pessoa com transtorno do espectro autista.” (NR)

# Art. 4º (VETADO).

# Art. 5º Esta Lei entra em vigor na data de sua publicação.

# Brasília, 8 de janeiro de 2020; 199º da Independência e 132º da República.

# JAIR MESSIAS BOLSONARO 
# Marcelo Henrique Teixeira Dias 
# Onyx Lorenzoni 
# Antonio Carlos Paiva Futuro

# Este texto não substitui o publicado no DOU de 9.1.2020

# \
#     """
#     simplified = """
#  A imagem fornecida não contém texto.Presidência da República
# Secretaria-Geral
# Subchefia para Assuntos Jurídicos

# Lei nº 13.977, de 8 de janeiro de 2020.

# Esta lei altera a Lei nº 12.764, de 27 de dezembro de 2012 (Lei Berenice Piana) e a Lei nº 9.265, de 12 de fevereiro de 1996. A lei cria a Carteira de Identificação da Pessoa com Transtorno do Espectro Autista (Ciptea). A carteira será gratuita.

# O Presidente da República informa que o Congresso Nacional decreta e sanciona esta lei.

# Art. 1º Esta lei, chamada Lei Romeo Mion, altera a Lei nº 12.764, de 27 de dezembro de 2012 (Lei Berenice Piana) e a Lei nº 9.265, de 12 de fevereiro de 1996 (Lei da Gratuidade dos Atos de Cidadania). A lei cria a Carteira de Identificação da Pessoa com Transtorno do Espectro Autista (Ciptea). A carteira será gratuita.

# Art. 2º A Lei nº 12.764, de 27 de dezembro de 2012 (Lei Berenice Piana) passa a ter as seguintes mudanças:

# “Art. 1º .....
# .....
# § 3º Os estabelecimentos públicos e privados da Lei nº 10.048, de 8 de novembro de 2000, podem usar a fita quebra-cabeça. Essa fita é um símbolo mundial que conscientiza sobre o transtorno do espectro autista. Ela ajuda a identificar a prioridade para pessoas com esse transtorno.”

# “Art. 3º .....
# .....
# § 1º .....
# § 2º (VETADO).”

# “Art. 3º-A. É criada a Carteira de Identificação da Pessoa com Transtorno do Espectro Autista (Ciptea). Ela garante atenção total, atendimento rápido e prioridade no acesso a serviços públicos e privados. Isso é especialmente importante nas áreas de saúde, educação e assistência social.

# § 1º Os órgãos responsáveis pela Política Nacional de Proteção dos Direitos da Pessoa com Transtorno do Espectro Autista dos Estados, do Distrito Federal e dos Municípios expedem a Ciptea. Eles fazem isso mediante pedido. O pedido deve ter um relatório médico. O relatório deve indicar o código da Classificação Estatística Internacional de Doenças e Problemas Relacionados à Saúde (CID). A carteira deve ter, no mínimo, as seguintes informações:

# nome completo, filiação, local e data de nascimento, número da carteira de identidade civil, número de inscrição no Cadastro de Pessoas Físicas (CPF), tipo sanguíneo, endereço completo e telefone da pessoa identificada.
# uma foto no tamanho de 3 centímetros por 4 centímetros e a assinatura ou impressão digital da pessoa.
# nome completo, documento de identificação, endereço, telefone e e-mail do responsável legal ou cuidador.
# a identificação da unidade da Federação e do órgão que emitiu a carteira, e a assinatura do chefe responsável.

# § 2º Se a pessoa com transtorno do espectro autista for imigrante com visto temporário ou autorização de residência, residente fronteiriço ou solicitante de refúgio, ela deve apresentar a Cédula de Identidade de Estrangeiro (CIE), a Carteira de Registro Nacional Migratório (CRNM) ou o Documento Provisório de Registro Nacional Migratório (DPRNM). Esses documentos devem ter validade em todo o país.

# § 3º A Ciptea tem validade de 5 anos. Os dados cadastrais da pessoa devem ser atualizados. A carteira deve ser revalidada com o mesmo número. Isso permite contar as pessoas com transtorno do espectro autista em todo o território nacional.

# § 4º Até que a lei diga o contrário, os órgãos responsáveis pela Política Nacional de Proteção dos Direitos da Pessoa com Transtorno do Espectro Autista devem trabalhar juntos com os responsáveis pela emissão de documentos de identificação. Eles devem incluir as informações sobre o transtorno do espectro autista no Registro Geral (RG) ou, se for estrangeiro, na Carteira de Registro Nacional Migratório (CRNM) ou na Cédula de Identidade de Estrangeiro (CIE), que são válidos em todo o país.”

# Art. 3º A Lei nº 9.265, de 12 de fevereiro de 1996, passa a incluir uma nova regra no artigo 1º (inciso VII):

# VII – É gratuito solicitar e emitir um documento de identificação específico para pessoas com transtorno do espectro autista (TEA), incluindo a emissão da segunda via desse documento.

# Art. 4º Este artigo foi vetado, ou seja, não foi aprovado e não faz parte da lei.

# Art. 5º Esta lei entra em vigor na data de sua publicação.

# Brasília, 8 de janeiro de 2020.

# Assinaturas das autoridades responsáveis pela lei:

# Jair Messias Bolsonaro
# Marcelo Henrique Teixeira Dias
# Onyx Lorenzoni
# Antonio Carlos Paiva Futuro

# Observação: Este texto é uma versão simplificada. O texto oficial da lei foi publicado no Diário Oficial da União em 9 de janeiro de 2020.
#     """

#     score = compute_similarity_score(
#         original,
#         simplified,
#         doc_type="legal",
#         model_name="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2",
#     )

#     print(f"score legal: {score:.4f}")