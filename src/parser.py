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

    line = p.lineno(1)  # Obtener número de línea del token LET
    
    # let x;
    if len(p) == 4:
        p[0] = ("var_decl", p[2], None, None, False, line)

    # let mut x;
    elif len(p) == 5:
        p[0] = ("var_decl", p[3], None, None, True, line)

    # let x = expr; O let x: tipo;
    elif len(p) == 6:
        if p[3] == ":":
            # let x: tipo;
            p[0] = ("var_decl", p[2], p[4], None, False, line)
        else:
            # let x = expr;
            p[0] = ("var_decl", p[2], None, p[4], False, line)

    # let mut x = expr; O let mut x: tipo;
    elif len(p) == 7:
        if p[4] == ":":
            # let mut x: tipo;
            p[0] = ("var_decl", p[3], p[5], None, True, line)
        else:
            # let mut x = expr;
            p[0] = ("var_decl", p[3], None, p[5], True, line)

    # let x: tipo = expr;
    elif len(p) == 8:
        p[0] = ("var_decl", p[2], p[4], p[6], False, line)

    # let mut x: tipo = expr;
    else:  # len(p) == 9
        p[0] = ("var_decl", p[3], p[5], p[7], True, line)


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

    line = p.lineno(1)  # Línea del ID o array_access
    
    if len(p) == 5:
        # Distinguir entre asignación a variable o array
        if isinstance(p[1], str):
            p[0] = ("assign", p[1], p[2], p[3], line)
        else:
            p[0] = ("assign_index", p[1], p[3], line)


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


# EXPRESIONES PRIMARIAS - Paul Perdomo
def p_expression_primary(p):
    """expression : INTEGER
    | FLOAT
    | STRING
    | CHAR
    | TRUE
    | FALSE
    | ID
    | array_access
    | tuple_access
    | function_call
    | vector_literal
    | array_literal
    | tuple_literal
    | LPAREN expression RPAREN"""
    if len(p) == 2:
        if isinstance(p[1], tuple):
            p[0] = p[1]
        else:
            p[0] = ("literal", p[1])
    else:
        p[0] = p[2]


def p_expression_statement(p):
    """expression_statement : expression SEMICOLON"""
    p[0] = ("expr_stmt", p[1])


# ESTRUCTURAS DE DATOS - Paul Perdomo (Vector)
def p_vector_literal(p):
    """vector_literal : VEC NOT LBRACKET expression_list RBRACKET
    | VEC NOT LBRACKET RBRACKET"""
    line = p.lineno(1)
    if len(p) == 6:
        p[0] = ("vector", p[4], line)
    else:
        p[0] = ("vector", [], line)


def p_expression_list(p):
    """expression_list : expression_list COMMA expression
    | expression"""
    if len(p) == 4:
        p[0] = p[1] + [p[3]]
    else:
        p[0] = [p[1]]


# ESTRUCTURAS DE DATOS - Paul Perdomo (Array)
def p_array_literal(p):
    """array_literal : LBRACKET expression_list RBRACKET
    | LBRACKET RBRACKET"""
    line = p.lineno(1)
    if len(p) == 4:
        p[0] = ("array", p[2], line)
    else:
        p[0] = ("array", [], line)


def p_array_access(p):
    """array_access : ID LBRACKET expression RBRACKET
    | array_access LBRACKET expression RBRACKET"""
    line = p.lineno(2)  # Línea del LBRACKET
    p[0] = ("array_access", p[1], p[3], line)


# ESTRUCTURAS DE DATOS - Paul Perdomo (Tupla)
def p_tuple_literal(p):
    """tuple_literal : LPAREN expression_list COMMA RPAREN
    | LPAREN expression COMMA expression RPAREN"""
    line = p.lineno(1)
    if len(p) == 5:
        p[0] = ("tuple", p[2], line)
    else:
        p[0] = ("tuple", [p[2], p[4]], line)


def p_tuple_access(p):
    """tuple_access : ID PERIOD INTEGER"""
    line = p.lineno(1)
    p[0] = ("tuple_access", p[1], p[3], line)


# IMPRESIÓN - Paul Perdomo
def p_print_statement(p):
    """print_statement : PRINT NOT LPAREN print_args RPAREN SEMICOLON
    | PRINTLN NOT LPAREN print_args RPAREN SEMICOLON
    | PRINT LPAREN print_args RPAREN SEMICOLON
    | PRINTLN LPAREN print_args RPAREN SEMICOLON"""
    line = p.lineno(1)
    if len(p) == 7:
        # Con NOT (!) - es macro de Rust
        p[0] = ("print", p[1], p[4], True, line)
    else:
        # Sin NOT - es función normal
        p[0] = ("print", p[1], p[3], False, line)


def p_print_args(p):
    """print_args : expression_list
    | empty"""
    p[0] = p[1] if p[1] else []


# ESTRUCTURAS DE CONTROL - IF/ELSE - Paul Perdomo
def p_if_statement(p):
    """if_statement : IF expression block
    | IF expression block ELSE block
    | IF expression block ELSE if_statement"""
    line = p.lineno(1)
    if len(p) == 4:
        p[0] = ("if", p[2], p[3], None, line)
    else:
        p[0] = ("if", p[2], p[3], p[5], line)


# ESTRUCTURAS DE CONTROL - WHILE - Paul Perdomo
def p_while_statement(p):
    """while_statement : WHILE expression block"""
    line = p.lineno(1)
    p[0] = ("while", p[2], p[3], line)


# ESTRUCTURAS DE CONTROL - FOR - Danilo Drouet
def p_for_statement(p):
    """for_statement : FOR ID IN range_expression block
    | FOR ID IN expression block"""
    line = p.lineno(1)
    p[0] = ("for", p[2], p[4], p[5], line)


def p_range_expression(p):
    """range_expression : expression PERIOD PERIOD expression"""
    p[0] = ("range", p[1], p[4])


# BLOQUE DE CÓDIGO - Danilo Drouet
def p_block(p):
    """block : LBRACE statement_list RBRACE
    | LBRACE RBRACE"""
    if len(p) == 4:
        p[0] = ("block", p[2])
    else:
        p[0] = ("block", [])


# DECLARACIÓN DE FUNCIONES - Danilo Drouet
def p_function_declaration(p):
    """function_declaration : FN ID LPAREN parameter_list RPAREN block
    | FN ID LPAREN parameter_list RPAREN ARROW type_annotation block
    | FN ID LPAREN RPAREN block
    | FN ID LPAREN RPAREN ARROW type_annotation block"""

    line = p.lineno(1)  # Línea del token FN
    
    # fn name() { ... }
    if len(p) == 6:
        p[0] = ("func_decl", p[2], [], None, p[5], line)

    # fn name(params) { ... }
    elif len(p) == 7:
        p[0] = ("func_decl", p[2], p[4], None, p[6], line)

    # fn name() -> type { ... }
    elif len(p) == 8:
        p[0] = ("func_decl", p[2], [], p[6], p[7], line)

    # fn name(params) -> type { ... }
    else:  # len(p) == 9
        p[0] = ("func_decl", p[2], p[4], p[7], p[8], line)


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


# LLAMADA A FUNCIÓN - Danilo Drouet
def p_function_call(p):
    """function_call : ID LPAREN argument_list RPAREN
    | ID LPAREN RPAREN"""
    line = p.lineno(1)
    if len(p) == 5:
        p[0] = ("func_call", p[1], p[3], line)
    else:
        p[0] = ("func_call", p[1], [], line)


def p_argument_list(p):
    """argument_list : expression_list"""
    p[0] = p[1]


# RETURN - Danilo Drouet
def p_return_statement(p):
    """return_statement : RETURN expression SEMICOLON
    | RETURN SEMICOLON"""
    line = p.lineno(1)
    if len(p) == 4:
        p[0] = ("return", p[2], line)
    else:
        p[0] = ("return", None, line)


# BREAK Y CONTINUE - Danilo Drouet
def p_break_statement(p):
    """break_statement : BREAK SEMICOLON"""
    line = p.lineno(1)
    p[0] = ("break", line)


def p_continue_statement(p):
    """continue_statement : CONTINUE SEMICOLON"""
    line = p.lineno(1)
    p[0] = ("continue", line)


# REGLA VACÍA - Danilo Drouet
def p_empty(p):
    """empty :"""
    pass


# MANEJO DE ERRORES SINTÁCTICOS - Anthony Herrera
def p_error(p):
    if p:
        # Calcular el número de línea real contando saltos de línea
        lines_before = p.lexer.lexdata[: p.lexpos].count("\n")
        line_number = lines_before + 1

        # Encontrar la columna en la línea actual
        line_start = p.lexer.lexdata.rfind("\n", 0, p.lexpos) + 1
        column = p.lexpos - line_start + 1

        error_msg = f"Error de sintaxis en línea {line_number}, columna {column}: token inesperado '{p.value}'"
        syntax_errors.append(error_msg)
    else:
        error_msg = "Error de sintaxis: fin de archivo inesperado"
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