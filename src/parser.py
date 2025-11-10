import ply.yacc as yacc
from lexer import tokens

# Lista para almacenar errores sintácticos
syntax_errors = []

# Precedencia y asociatividad de operadores
precedence = (
    ("left", "OR"),
    ("left", "AND"),
    ("left", "EQUAL", "NOT_EQUAL"),
    ("left", "LESS_THAN", "GREATER_THAN", "LESS_EQUAL", "GREATER_EQUAL"),
    ("left", "PLUS", "MINUS"),
    ("left", "MULTIPLY", "DIVIDE", "MODULO"),
    ("right", "NOT"),
)


# MANEJO PROGRAMA PRINCIPAL - Anthony Herrera
def p_program(p):
    """program : statement_list"""
    p[0] = ("program", p[1])


def p_statement_list(p):
    """statement_list : statement_list statement
    | statement"""
    if len(p) == 3:
        p[0] = p[1] + [p[2]]
    else:
        p[0] = [p[1]]


def p_statement(p):
    """statement : variable_declaration
    | assignment
    | expression_statement
    | print_statement
    | if_statement
    | while_statement
    | for_statement
    | function_declaration
    | return_statement
    | break_statement
    | continue_statement
    | block"""
    p[0] = p[1]


# DECLARACIÓN DE VARIABLES - Anthony Herrera
def p_variable_declaration(p):
    """variable_declaration : LET ID SEMICOLON
    | LET MUT ID SEMICOLON
    | LET ID ASSIGN expression SEMICOLON
    | LET MUT ID ASSIGN expression SEMICOLON
    | LET ID COLON type_annotation SEMICOLON
    | LET MUT ID COLON type_annotation SEMICOLON
    | LET ID COLON type_annotation ASSIGN expression SEMICOLON
    | LET MUT ID COLON type_annotation ASSIGN expression SEMICOLON"""

    # let x;
    if len(p) == 4:
        p[0] = ("var_decl", p[2], None, None, False)

    # let mut x;
    elif len(p) == 5:
        p[0] = ("var_decl", p[3], None, None, True)

    # let x = expr; O let x: tipo;
    elif len(p) == 6:
        if p[3] == ":":
            # let x: tipo;
            p[0] = ("var_decl", p[2], p[4], None, False)
        else:
            # let x = expr;
            p[0] = ("var_decl", p[2], None, p[4], False)

    # let mut x = expr; O let mut x: tipo;
    elif len(p) == 7:
        if p[4] == ":":
            # let mut x: tipo;
            p[0] = ("var_decl", p[3], p[5], None, True)
        else:
            # let mut x = expr;
            p[0] = ("var_decl", p[3], None, p[5], True)

    # let x: tipo = expr;
    elif len(p) == 8:
        p[0] = ("var_decl", p[2], p[4], p[6], False)

    # let mut x: tipo = expr;
    else:  # len(p) == 9
        p[0] = ("var_decl", p[3], p[5], p[7], True)


def p_type_annotation(p):
    """type_annotation : ID
    | vector_type
    | array_type
    | tuple_type"""
    p[0] = p[1]


def p_vector_type(p):
    """vector_type : VEC LESS_THAN type_annotation GREATER_THAN"""
    p[0] = ("Vec", p[3])


def p_array_type(p):
    """array_type : LBRACKET type_annotation SEMICOLON INTEGER RBRACKET"""
    p[0] = ("Array", p[2], p[4])


def p_tuple_type(p):
    """tuple_type : LPAREN type_list RPAREN"""
    p[0] = ("Tuple", p[2])


def p_type_list(p):
    """type_list : type_list COMMA type_annotation
    | type_annotation"""
    if len(p) == 4:
        p[0] = p[1] + [p[3]]
    else:
        p[0] = [p[1]]


# ASIGNACIÓN - Anthony Herrera
def p_assignment(p):
    """assignment : ID ASSIGN expression SEMICOLON
    | ID PLUS_ASSIGN expression SEMICOLON
    | ID MINUS_ASSIGN expression SEMICOLON
    | ID MULT_ASSIGN expression SEMICOLON
    | ID DIV_ASSIGN expression SEMICOLON
    | ID MOD_ASSIGN expression SEMICOLON
    | array_access ASSIGN expression SEMICOLON"""

    if len(p) == 5:
        # Distinguir entre asignación a variable o array
        if isinstance(p[1], str):
            p[0] = ("assign", p[1], p[2], p[3])
        else:
            p[0] = ("assign_index", p[1], p[3])


# EXPRESIONES ARITMÉTICAS - Anthony Herrera
def p_expression_arithmetic(p):
    """expression : expression PLUS expression
    | expression MINUS expression
    | expression MULTIPLY expression
    | expression DIVIDE expression
    | expression MODULO expression"""
    p[0] = ("binop", p[2], p[1], p[3])


# EXPRESIONES BOOLEANAS - Anthony Herrera
def p_expression_boolean(p):
    """expression : expression EQUAL expression
    | expression NOT_EQUAL expression
    | expression LESS_THAN expression
    | expression GREATER_THAN expression
    | expression LESS_EQUAL expression
    | expression GREATER_EQUAL expression
    | expression AND expression
    | expression OR expression
    | NOT expression"""
    if len(p) == 4:
        p[0] = ("binop", p[2], p[1], p[3])
    else:
        p[0] = ("unop", p[1], p[2])


# MANEJO DE ERRORES SINTÁCTICOS - Anthony Herrera
def p_error(p):
    error_msg = f"Error de sintaxis en línea {p.lineno}, posición {p.lexpos}: token inesperado '{p.value}'"
    syntax_errors.append(error_msg)
    parser.errok()


parser = yacc.yacc()


def parse_code(code):
    """
    Analiza el código y retorna el AST y los errores
    """
    from lexer import lexer

    global syntax_errors
    syntax_errors = []

    result = parser.parse(code, lexer=lexer)

    return result, syntax_errors
# ESTRUCTURAS DE CONTROL - FOR - Danilo Drouet
# ============================================================================
def p_for_statement(p):
    """for_statement : FOR ID IN range_expression block
    | FOR ID IN expression block"""
    p[0] = ("for", p[2], p[4], p[5])


def p_range_expression(p):
    """range_expression : expression PERIOD PERIOD expression"""
    p[0] = ("range", p[1], p[4])


# ============================================================================
# BLOQUE DE CÓDIGO - Danilo Drouet
# ============================================================================
def p_block(p):
    """block : LBRACE statement_list RBRACE
    | LBRACE RBRACE"""
    if len(p) == 4:
        p[0] = ("block", p[2])
    else:
        p[0] = ("block", [])


# ============================================================================
# DECLARACIÓN DE FUNCIONES - Danilo Drouet
# ============================================================================
def p_function_declaration(p):
    """function_declaration : FN ID LPAREN parameter_list RPAREN block
    | FN ID LPAREN parameter_list RPAREN ARROW type_annotation block
    | FN ID LPAREN RPAREN block
    | FN ID LPAREN RPAREN ARROW type_annotation block"""

    # fn name() { ... } - 6 elementos: FN ID ( ) block
    if len(p) == 6:
        p[0] = ("func_decl", p[2], [], None, p[5])

    # fn name(params) { ... } - 7 elementos: FN ID ( params ) block
    elif len(p) == 7:
        p[0] = ("func_decl", p[2], p[4], None, p[6])

    # fn name() -> type { ... } - 8 elementos: FN ID ( ) -> type block
    elif len(p) == 8:
        p[0] = ("func_decl", p[2], [], p[6], p[7])

    # fn name(params) -> type { ... } - 9 elementos: FN ID ( params ) -> type block
    else:  # len(p) == 9
        p[0] = ("func_decl", p[2], p[4], p[7], p[8])


def p_parameter_list(p):
    """parameter_list : parameter_list COMMA parameter
    | parameter"""
    if len(p) == 4:
        p[0] = p[1] + [p[3]]
    else:
        p[0] = [p[1]]


def p_parameter(p):
    """parameter : ID COLON type_annotation"""
    p[0] = ("param", p[1], p[3])


# ============================================================================
# LLAMADA A FUNCIÓN - Danilo Drouet
# ============================================================================
def p_function_call(p):
    """function_call : ID LPAREN argument_list RPAREN
    | ID LPAREN RPAREN"""
    if len(p) == 5:
        p[0] = ("func_call", p[1], p[3])
    else:
        p[0] = ("func_call", p[1], [])


def p_argument_list(p):
    """argument_list : expression_list"""
    p[0] = p[1]


# ============================================================================
# RETURN - Danilo Drouet
# ============================================================================
def p_return_statement(p):
    """return_statement : RETURN expression SEMICOLON
    | RETURN SEMICOLON"""
    if len(p) == 4:
        p[0] = ("return", p[2])
    else:
        p[0] = ("return", None)


# ============================================================================
# BREAK Y CONTINUE - Danilo Drouet
# ============================================================================
def p_break_statement(p):
    """break_statement : BREAK SEMICOLON"""
    p[0] = ("break",)


def p_continue_statement(p):
    """continue_statement : CONTINUE SEMICOLON"""
    p[0] = ("continue",)


# ============================================================================
# REGLA VACÍA - Danilo Drouet
# ============================================================================
def p_empty(p):
    """empty :"""
    pass