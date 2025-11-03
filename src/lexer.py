import ply.lex as lex

reserved = {
    "let": "LET",
    "mut": "MUT",
    "if": "IF",
    "else": "ELSE",
    "while": "WHILE",
    "for": "FOR",
    "in": "IN",
    "fn": "FN",
    "return": "RETURN",
    "true": "TRUE",
    "false": "FALSE",
    "print": "PRINT",
    "println": "PRINTLN",
    "vec": "VEC",
    "break": "BREAK",
    "continue": "CONTINUE",
}

tokens = [
    "INTEGER",
    "FLOAT",
    "STRING",
    "CHAR",
    "ID",
    "PLUS",
    "MINUS",
    "MULTIPLY",
    "DIVIDE",
    "MODULO",
    "ASSIGN",
    "PLUS_ASSIGN",
    "MINUS_ASSIGN",
    "MULT_ASSIGN",
    "DIV_ASSIGN",
    "MOD_ASSIGN",
    "EQUAL",
    "NOT_EQUAL",
    "LESS_THAN",
    "GREATER_THAN",
    "LESS_EQUAL",
    "GREATER_EQUAL",
    "AND",
    "OR",
    "NOT",
    "ARROW",
    "SEMICOLON",
    "COMMA",
    "LBRACE",
    "RBRACE",
    "LPAREN",
    "RPAREN",
    "LBRACKET",
    "RBRACKET",
    "COLON",
] + list(reserved.values())

t_PLUS = r"\+"
t_MINUS = r"-"
t_MULTIPLY = r"\*"
t_DIVIDE = r"/"
t_MODULO = r"%"

t_PLUS_ASSIGN = r"\+\="
t_MINUS_ASSIGN = r"-\="
t_MULT_ASSIGN = r"\*\="
t_DIV_ASSIGN = r"/\="
t_MOD_ASSIGN = r"%\="

t_ASSIGN = r"="

t_EQUAL = r"=="
t_NOT_EQUAL = r"!="
t_LESS_EQUAL = r"<="
t_GREATER_EQUAL = r">="
t_LESS_THAN = r"<"
t_GREATER_THAN = r">"

t_AND = r"&&"
t_OR = r"\|\|"
t_NOT = r"!"

t_ARROW = r"->"

t_SEMICOLON = r";"
t_COMMA = r","
t_LBRACE = r"\{"
t_RBRACE = r"\}"
t_LPAREN = r"\("
t_RPAREN = r"\)"
t_LBRACKET = r"\["
t_RBRACKET = r"\]"
t_COLON = r":"

string_escape = r'(\\.|[^"\\])*'
char_escape = r"(\\.|[^'\\])"


def t_STRING(t):
    r'"' + string_escape + r'"'
    t.value = t.value[1:-1]
    return t


def t_CHAR(t):
    r"'" + char_escape + r"'"
    inner = t.value[1:-1]
    t.value = inner
    return t


def t_FLOAT(t):
    r"([0-9]+\.[0-9]+)"
    t.value = float(t.value)
    return t


def t_INTEGER(t):
    r"([0-9]+)"
    t.value = int(t.value)
    return t


def t_ID(t):
    r"[a-zA-Z_][a-zA-Z0-9_]*"
    t.type = reserved.get(t.value, "ID")
    return t

# Paul Perdomo
def t_COMMENT_SINGLE(t):
    r'//[^\n]*'
    t.lexer.lineno += 1
    pass

def t_COMMENT_MULTI(t):
    r'/\\*[\\s\\S]*?\\*/'
    t.lexer.lineno += t.value.count('\\n')
    pass

t_ignore = ' \t\r'
