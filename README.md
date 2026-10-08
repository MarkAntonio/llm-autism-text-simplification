# 🧩 llm-autism-text-simplification

> Plataforma para simplificação de textos sobre o Transtorno do Espectro Autista (TEA) em Linguagem Simples, cobrindo os eixos de legislação, saúde, educação e gestão administrativa utilizando inteligência artificial.

---

## 📌 Sobre o Projeto

Compreender direitos, laudos clínicos, diretrizes pedagógicas e procedimentos burocráticos sobre o autismo é, frequentemente, um desafio devido ao uso de termos técnicos e linguagem complexa.

O **SimplificaIA - Autismo** é um projeto focado em transformar esses conteúdos em textos acessíveis, claros e diretos em **Linguagem Simples (Plain Language)**. 

A proposta abrange tanto o desenvolvimento e uso de modelos de linguagem (LLMs) para realizar o processo de simplificação adaptada, quanto a **disponibilização direta dos textos já simplificados para os usuários finais** — incluindo pessoas autistas, familiares, educadores e profissionais da área.

---

## 🎯 Escopos de Atuação

Os textos e materiais do projeto estão divididos em 4 eixos fundamentais:

| Escopo | Foco do Conteúdo | Exemplos de Aplicação |
| :--- | :--- | :--- |
| ⚖️ **Jurídico / Leis** | Direitos, legislação, normas e garantias legais. | Leis de acessibilidade, prioridades, BPC/LOAS e carteiras de identificação (Ciptea). |
| 🏥 **Saúde** | Laudos, orientações clínicas, relatórios de terapias e diagnósticos. | Explicativa de termos técnicos em relatórios de Fonoaudiologia, Terapia Ocupacional e ABA. |
| 🎓 **Educação** | Direitos escolares, adaptações curriculares e pedagógicas. | Orientações sobre o Plano de Desenvolvimento Individualizado (PDI) e acompanhante escolar. |
| 🏢 **Administrativo** | Guias passo a passo para processos burocráticos e serviços. | Tutoriais de solicitação de benefícios, passes livres e emissão de documentos. |

---

## 💡 Objetivos Principais

* **Inclusão e Autonomia:** Garantir que a informação sobre direitos e cuidados esteja ao alcance de qualquer pessoa, sem barreiras linguísticas.
* **Geração Adaptada:** Empregar modelos de inteligência artificial (LLMs) com técnicas de reescrita focadas em clareza e manutenção do sentido original.
* **Acesso Direto ao Acervo:** Entregar uma base de dados pública com os textos originais e suas respetivas versões simplificadas prontas para leitura e download.

## 📁 Estrutura do Repositório

```

**A definir**

```

---

## 📐 Arquitetura do Pipeline

```text
[ Texto Original (Complexo) ]
            │
            ▼
┌──────────────────────────┐
│   Pré-processamento &    │ (Limpeza, estruturação, extração de texto)
│      Chunking            │
└───────────┬──────────────┘
            │
            ▼
┌──────────────────────────┐
│  LLM Engine + Prompting  │ (Aplicação das diretrizes de Linguagem Simples)
│  (RAG / Fine-tuning)     │
└───────────┬──────────────┘
            │
            ▼
┌──────────────────────────┐
│  Avaliação & Validação   │ (Métricas de legibilidade: Flesch, BERTScore, etc.)
└───────────┬──────────────┘
            │
            ▼
[ Texto Simplificado (Linguagem Simples) ] ──► Disponível no acervo
```

---

## 🚀 Como Começar

```

**A definir**

```


---

## 💡 Como Usar

```

**A definir**

```


---

## 🤝 Como Contribuir

Contribuições são super bem-vindas! Você pode ajudar de diversas formas:

- Revisando e sugerindo melhorias nos textos simplificados gerados.
- Contribuindo com novos documentos originais no diretório data/raw/.
- Aprimorando os prompts e técnicas de engenharia de IA na pasta src/llm/.

> entre em contato pelo meu email: tech.marcosantos@gmail.com ou pelo linkedin ([https://www.linkedin.com/in/techmarcosantos/](https://www.linkedin.com/in/techmarcosantos/))

---
💙 Agradecimentos e Impacto

Projeto desenvolvido com o compromisso de promover a inclusão, a acessibilidade à informação e a autonomia de pessoas autistas, suas famílias e profissionais das áreas de saúde, educação e direito.

## 📄 Licença e Uso

Este projeto tem caráter informativo, educacional e social. Todo o acervo simplificado disponibilizado visa facilitar o acesso democrático à informação de qualidade.
