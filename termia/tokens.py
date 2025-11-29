import ply.lex as lex

tokens = (
    "LS", "MKDIR", "CD", "EXIT",
    "IA", "ASK", "SUMMARIZE", "CODEEXPLAIN",
    "STRING", "MSTRING", "PATH", "NAME","HELP",
)

reserved = {
    "ls": "LS",
    "mkdir": "MKDIR",
    "cd": "CD",
    "exit": "EXIT",
    "ia": "IA",
    "ask": "ASK",
    "summarize": "SUMMARIZE",
    "codeexplain": "CODEEXPLAIN",
    "help": "HELP",
}

# ------------------------------------------------------------
# Estados do lexer
# ------------------------------------------------------------
states = (
    ("RAW", "exclusive"),   # para MSTRING
)

t_RAW_ignore = ' \t'


t_ignore = " \t"

# ------------------------------------------------------------
# Início de MSTRING: detecta """ e entra em estado RAW
# ------------------------------------------------------------
def t_start_MSTRING(t):
    r'"""'
    t.lexer.raw_buffer = []
    t.lexer.push_state("RAW")
    return None

# ------------------------------------------------------------
# Coleta tudo dentro do estado RAW
# ------------------------------------------------------------
def t_RAW_end(t):
    r'"""'
    t.lexer.pop_state()
    t.value = "".join(t.lexer.raw_buffer)
    t.type = "MSTRING"
    return t

def t_RAW_text(t):
    r'(.|\n)'
    t.lexer.raw_buffer.append(t.value)

def t_RAW_error(t):
    t.lexer.raw_buffer.append(t.value)
    t.lexer.skip(1)

# ------------------------------------------------------------
# STRING normal com escapes
# ------------------------------------------------------------
def t_STRING(t):
    r'"([^"\\]|\\.)*"'
    raw = t.value[1:-1]
    t.value = bytes(raw, "utf-8").decode("unicode_escape")
    return t

# ------------------------------------------------------------
# PATH
# ------------------------------------------------------------
def t_PATH(t):
    r'/[^\s"“”]+|[^\s"“”]+/[^\s"“”]+'
    return t

# ------------------------------------------------------------
# NAME ou palavra-chave
# ------------------------------------------------------------
def t_NAME(t):
    r'[\w\.\-]+'
    t.type = reserved.get(t.value, "NAME")
    return t

def t_newline(t):
    r'\n+'
    t.lexer.lineno += len(t.value)

def t_error(t):
    raise SyntaxError(
        f"Caractere inválido no lexer: '{t.value[0]}' na posição {t.lexpos}"
    )

def build_lexer(**kwargs):
    return lex.lex(**kwargs)
