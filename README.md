# TermIA — Terminal Inteligente

**Entrega Parcial + Integração com IA + Interface Gráfica**

**Disciplina:** ECOI26 — Compiladores  
**Professor:** Walter Aoiama Nagai  
**Alunos:** Gabriel Pereira Barcellos Sacramento, Rhuan Pablo Malta Lage, Ueld Judah Nunes Nóbrega

---

## 🎯 Visão Geral

O **TermIA** é um terminal interativo desenvolvido para a disciplina de **Compiladores**, cujo objetivo é aplicar os conceitos teóricos de:

* Análise léxica (*lexer*)
* Análise sintática (*parser*)
* Árvores sintáticas abstratas (AST)
* Integração com execuções semânticas (runtime)

Culminando em um shell funcional que também utiliza uma **API externa de Inteligência Artificial** para executar comandos como análise, resumo e explicação de código.

### Implementações Atuais

* Lexer robusto, com suporte a **strings multilinha**, aspas internas e blocos `"""..."""`
* Parser totalmente integrado ao lexer e à gramática EBNF
* Runtime para comandos de SO e IA
* Interface gráfica completa em **Tkinter**, com comportamento semelhante a um terminal UNIX

---

## 🧩 Estrutura do Projeto

```
TermIA/
├─ README.md                  # Este documento
├─ grammar.ebnf               # Gramática formal usada na modelagem
├─ termia_gui.py              # Interface gráfica Tkinter
├─ termia/
│  ├─ __init__.py
│  ├─ tokens.py               # Lexer (PLY)
│  ├─ parser.py               # Parser (PLY)
│  ├─ ast.py                  # Representação da AST
│  └─ runtime.py              # Execução dos comandos (SO + IA)
└─            

---

## ⚙️ Requisitos

* **Python 3.10+**
* **PLY (Python Lex-Yacc)**:
  ```bash
  pip install ply
  ```
* **Requests** (para integrar com API de IA):
  ```bash
  pip install requests
  ```
* Compatível com Windows, Linux, macOS

---

## 🚀 Execução

### Via Terminal

```bash
python -m termia.main_demo
```

### Via Interface Gráfica

```bash
python termia_gui.py
```

---

## 🧠 Comandos Implementados

A gramática do TermIA suporta dois grupos principais:

* **Comandos de Sistema Operacional**
* **Comandos de Inteligência Artificial (`ia`)**

---

## 🔹 Comandos de Sistema Operacional

### 1. `ls`

Lista arquivos de um diretório.

**Uso:**
```
ls
ls <path>
```

**Regras:**
* `<path>` é opcional
* Quando omitido, lista o diretório atual
* Caminhos são validados dentro da sandbox definida pelo runtime

---

### 2. `mkdir`

Cria um novo diretório.

**Uso:**
```
mkdir <nome>
```

**Regras:**
* `<nome>` é obrigatório
* Pode conter letras, números, `.`, `_`, `-`

---

### 3. `cd`

Altera o diretório atual.

**Uso:**
```
cd
cd <path>
```

**Regras:**
* Se omitido: volta para o diretório base
* Aceita caminhos relativos, absolutos e nomes simples

---

### 4. `exit`

Encerra o TermIA.

```
exit
```

Sem argumentos.

---

## 🔹 Comandos de Inteligência Artificial (`ia`)

Os comandos IA utilizam uma **API externa** (estilo ChatGPT) para responder perguntas, resumir textos e explicar códigos.

Todos seguem a forma:
```
ia <subcomando> <conteúdo>
```

---

### 1. `ia ask`

Faz uma pergunta direta à IA.

**Uso:**
```
ia ask "<pergunta>"
ia ask """pergunta multilinha"""
```

**Entrada aceita:**
* Strings simples (`"texto"`)
* Strings multilinha (`"""..."""`)
* Aspas internas via escape (`\"`)

---

### 2. `ia summarize`

Solicita um resumo de qualquer texto.

**Uso:**
```
ia summarize "<texto>"
ia summarize """texto multilinha"""
```

**Formatos aceitos pelo lexer:**
* Texto com quebras de linha reais
* Aspas duplas internas
* Blocos usando três aspas

---

### 3. `ia codeexplain`

Pede para a IA explicar um trecho de código, arquivo ou texto bruto.

**Uso:**
```
ia codeexplain """código
multilinha
com aspas "internas"
e símbolos {} [] ()"""
```

**`<alvo>` pode ser:**
* **MSTRING** → `"""código bruto"""`

---

## 🧱 Funcionamento Interno

| Componente | Função | Destaques |
|------------|--------|-----------|
| **Lexer (`tokens.py`)** | Tokeniza entrada reconhecendo PATH, NAME, STRING e MSTRING | Permite multiline + aspas internas |
| **Parser (`parser.py`)** | Constrói AST via PLY-Yacc | Produções para todos os comandos do TermIA |
| **AST (`ast.py`)** | Estruturas dos comandos | Usa dicionários uniformes |
| **Runtime (`runtime.py`)** | Executa comandos de SO e IA | Integra API externa (ninja-apps) |
| **GUI (`termia_gui.py`)** | Interface de terminal em Tkinter | Estilo terminal moderno |

---

## 🖥️ Interface Gráfica (Tkinter)

A GUI fornece um ambiente que simula um terminal real.

### ✔ Características

* Temas escuros com cores de destaque
* Área de saída com scroll
* Campo de entrada responsivo
* Normalização automática de:
  * Aspas tortas (`" "`)
  * Caracteres irregulares da web
* Highlight de comandos, respostas e erros
* Envio via Enter ou botão
* Scroll automático
* Suporte TOTAL a multiline com `"""..."""`

### ✔ Exemplos de Uso

**Resumo multilinha:**
```
ia summarize """
Esse é um texto grande,
com várias linhas,
aspas "internas" e etc.
"""
```

**Explicar código:**
```
ia codeexplain """
def soma(a, b):
    return a + b
"""
```