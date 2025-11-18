# ============================================================================
# Anthony Herrera
# ============================================================================
# Lista para almacenar errores semánticos
semantic_errors = []

# Tabla de símbolos global
symbol_table = {}
function_table = {}

# Contexto actual (para saber si estamos en loop, función, etc.)
context = {
    "in_loop": False,
    "in_function": None,  # None o nombre de la función actual
    "return_type": None,  # Tipo de retorno esperado
}


# UTILIDADES COMPARTIDAS
def add_error(line, message):
    """Agrega un error semántico a la lista"""
    error = f"Línea {line}: {message}"
    semantic_errors.append(error)
    print(f"❌ {error}")


def get_expression_type(node):
    """Retorna el tipo de una expresión del AST"""
    if isinstance(node, tuple):
        if node[0] == "literal":
            value = node[1]
            if isinstance(value, bool):
                return "bool"
            elif isinstance(value, int):
                return "i32"
            elif isinstance(value, float):
                return "f64"
            elif isinstance(value, str):
                if len(value) == 1:
                    return "char"
                return "String"
        elif node[0] == "binop":
            # Operadores aritméticos retornan el tipo de los operandos
            # Operadores booleanos retornan bool
            operator = node[1]
            if operator in ["+", "-", "*", "/", "%"]:
                return get_expression_type(node[2])  # Tipo del operando izquierdo
            elif operator in ["==", "!=", "<", ">", "<=", ">=", "&&", "||"]:
                return "bool"
        elif node[0] == "unop":
            if node[1] == "!":
                return "bool"
        # Agregar más casos según sea necesario
    return None


def check_variable_declaration(node, line=0):
    """
    Regla 1: Verifica que las variables no se declaren dos veces en el mismo scope
    Regla 2: Verifica tipos en asignaciones
    """
    # var_decl = ("var_decl", name, type, value, is_mut)
    if node[0] == "var_decl":
        name = node[1]
        declared_type = node[2]
        value = node[3]
        is_mut = node[4]

        # Verificar si ya está declarada
        if name in symbol_table:
            add_error(line, f"Variable '{name}' ya fue declarada previamente")
            return

        # Si tiene valor inicial, verificar tipo
        if value is not None and declared_type is not None:
            value_type = get_expression_type(value)
            if value_type and value_type != declared_type:
                add_error(
                    line,
                    f"Tipo incompatible: se esperaba '{declared_type}' pero se obtuvo '{value_type}'",
                )

        # Agregar a tabla de símbolos
        symbol_table[name] = {
            "type": declared_type,
            "mutable": is_mut,
            "initialized": value is not None,
        }


def check_variable_usage(node, line=0):
    """
    Verifica que las variables estén declaradas antes de usarse
    """
    if isinstance(node, str):
        # Es un ID
        if node not in symbol_table:
            add_error(line, f"Variable '{node}' no ha sido declarada")
            return False
    return True


def check_assignment(node, line=0):
    """
    Verifica asignaciones: variable debe existir, ser mutable, y tipos compatibles
    """
    # assign = ("assign", name, operator, value)
    if node[0] == "assign":
        name = node[1]
        operator = node[2]
        value = node[3]

        # Verificar que la variable exista
        if name not in symbol_table:
            add_error(line, f"No se puede asignar a '{name}': variable no declarada")
            return

        var_info = symbol_table[name]

        # Verificar que sea mutable (si no es la primera asignación)
        if not var_info["mutable"] and var_info["initialized"]:
            add_error(
                line,
                f"No se puede asignar a '{name}': variable no es mutable (use 'mut')",
            )
            return

        # Verificar tipos
        value_type = get_expression_type(value)
        if var_info["type"] and value_type:
            if operator == "=":
                if var_info["type"] != value_type:
                    add_error(
                        line,
                        f"Tipo incompatible en asignación: '{name}' es '{var_info['type']}' pero se asigna '{value_type}'",
                    )
            else:  # +=, -=, *=, /=, %=
                if var_info["type"] not in ["i32", "f64"]:
                    add_error(
                        line,
                        f"Operador '{operator}' no válido para tipo '{var_info['type']}'",
                    )
                if value_type not in ["i32", "f64"]:
                    add_error(
                        line,
                        f"Operador '{operator}' requiere valor numérico, se obtuvo '{value_type}'",
                    )

        # Marcar como inicializada
        var_info["initialized"] = True


# ============================================================================
# ANÁLISIS SEMÁNTICO - Paul Perdomo
# ============================================================================
def check_data_structures(node, line=0):
    # Paul Perdomo: Vectores y Arrays
    if node[0] == "vector" or node[0] == "array":
        elements = node[1]
        if len(elements) > 0:
            first_type = get_expression_type(elements[0])
            for i, elem in enumerate(elements[1:], 1):
                elem_type = get_expression_type(elem)
                if elem_type and first_type and elem_type != first_type:
                    add_error(
                        line,
                        f"Tipo inconsistente en {'vector' if node[0] == 'vector' else 'array'}: elemento {i} es '{elem_type}', se esperaba '{first_type}'",
                    )

    # Paul Perdomo: Acceso a Arrays
    elif node[0] == "array_access":
        array_name = node[1]
        index = node[2]

        if isinstance(array_name, str):
            check_variable_usage(array_name, line)

        index_type = get_expression_type(index)
        if index_type and index_type != "i32":
            add_error(
                line, f"Índice de array debe ser entero (i32), se obtuvo '{index_type}'"
            )

    # Paul Perdomo: Acceso a Tuplas
    elif node[0] == "tuple_access":
        tuple_name = node[1]
        index = node[2]
        check_variable_usage(tuple_name, line)


def check_boolean_conditions(node, line=0):
    # Paul Perdomo: Validar condiciones en if/while
    if node[0] in ["if", "while"]:
        condition = node[1]
        condition_type = get_expression_type(condition)

        if condition_type and condition_type != "bool":
            add_error(
                line,
                f"Condición en '{node[0]}' debe ser booleana, se obtuvo '{condition_type}'",
            )


# ============================================================================
# ANÁLISIS SEMÁNTICO - Danilo Drouet
# ============================================================================
def check_function_declaration(node, line=0):
    """
    Registra funciones en la tabla de funciones
    """
    # func_decl = ("func_decl", name, params, return_type, body)
    if node[0] == "func_decl":
        name = node[1]
        params = node[2]
        return_type = node[3]
        body = node[4]

        # Verificar si ya está declarada
        if name in function_table:
            add_error(line, f"Función '{name}' ya fue declarada previamente")
            return

        # Registrar función
        param_types = [p[2] for p in params]  # p = ("param", name, type)
        function_table[name] = {"params": param_types, "return_type": return_type}

        # Analizar el cuerpo en contexto de función
        old_context = context.copy()
        context["in_function"] = name
        context["return_type"] = return_type

        # Agregar parámetros a tabla de símbolos temporal
        for param in params:
            param_name = param[1]
            param_type = param[2]
            symbol_table[param_name] = {
                "type": param_type,
                "mutable": False,
                "initialized": True,
            }

        # Analizar cuerpo
        analyze_node(body, line)

        # Restaurar contexto
        context.update(old_context)


def check_function_call(node, line=0):
    """
    Regla 1: Verifica llamadas a funciones
    """
    # func_call = ("func_call", name, args)
    if node[0] == "func_call":
        name = node[1]
        args = node[2]

        # Verificar que la función existe
        if name not in function_table:
            add_error(line, f"Función '{name}' no ha sido declarada")
            return

        func_info = function_table[name]

        # Verificar número de argumentos
        if len(args) != len(func_info["params"]):
            add_error(
                line,
                f"Función '{name}' espera {len(func_info['params'])} argumentos, se recibieron {len(args)}",
            )
            return

        # Verificar tipos de argumentos
        for i, (arg, expected_type) in enumerate(zip(args, func_info["params"])):
            arg_type = get_expression_type(arg)
            if arg_type and expected_type and arg_type != expected_type:
                add_error(
                    line,
                    f"Argumento {i+1} de '{name}': se esperaba '{expected_type}', se obtuvo '{arg_type}'",
                )


def check_control_flow(node, line=0):
    """
    Regla 2: Verifica contexto de break, continue y return
    """
    if node[0] == "break" or node[0] == "continue":
        if not context["in_loop"]:
            add_error(line, f"'{node[0]}' solo puede usarse dentro de un loop")

    elif node[0] == "return":
        if context["in_function"] is None:
            add_error(line, "'return' solo puede usarse dentro de una función")
            return

        return_value = node[1] if len(node) > 1 else None
        expected_type = context["return_type"]

        if expected_type is None and return_value is not None:
            add_error(
                line, f"Función '{context['in_function']}' no debe retornar un valor"
            )
        elif expected_type is not None and return_value is None:
            add_error(
                line,
                f"Función '{context['in_function']}' debe retornar un valor de tipo '{expected_type}'",
            )
        elif expected_type is not None and return_value is not None:
            return_type = get_expression_type(return_value)
            if return_type and return_type != expected_type:
                add_error(
                    line,
                    f"Tipo de retorno incorrecto: se esperaba '{expected_type}', se obtuvo '{return_type}'",
                )


# FUNCIÓN PRINCIPAL
def analyze_node(node, line=0):
    """Analiza recursivamente un nodo del AST"""
    if node is None or not isinstance(node, tuple):
        return

    node_type = node[0]

    # Anthony Herrera - Variables y asignaciones
    if node_type == "var_decl":
        check_variable_declaration(node, line)
    elif node_type == "assign" or node_type == "assign_index":
        check_assignment(node, line)

    # Paul Perdomo - Estructuras de datos y condiciones
    elif node_type in ["vector", "array", "array_access", "tuple_access"]:
        check_data_structures(node, line)
    elif node_type in ["if", "while"]:
        check_boolean_conditions(node, line)
        # Cambiar contexto para loops
        if node_type == "while":
            old_in_loop = context["in_loop"]
            context["in_loop"] = True
            analyze_node(node[2], line)  # Analizar cuerpo
            context["in_loop"] = old_in_loop

    # Danilo Drouet - Funciones y control de flujo
    elif node_type == "func_decl":
        check_function_declaration(node, line)
    elif node_type == "func_call":
        check_function_call(node, line)
    elif node_type in ["return", "break", "continue"]:
        check_control_flow(node, line)

    # For loops (Paul Perdomo)
    elif node_type == "for":
        old_in_loop = context["in_loop"]
        context["in_loop"] = True
        # Agregar variable de iteración a tabla de símbolos
        iter_var = node[1]
        symbol_table[iter_var] = {"type": "i32", "mutable": False, "initialized": True}
        analyze_node(node[3], line)  # Analizar cuerpo
        context["in_loop"] = old_in_loop

    # Analizar recursivamente
    elif node_type == "program":
        for stmt in node[1]:
            analyze_node(stmt, line)
    elif node_type == "block":
        for stmt in node[1]:
            analyze_node(stmt, line)

    # Expresiones
    elif node_type == "binop":
        analyze_node(node[2], line)
        analyze_node(node[3], line)
    elif node_type == "unop":
        analyze_node(node[2], line)


def analyze(ast):
    """Función principal del análisis semántico"""
    global semantic_errors, symbol_table, function_table
    semantic_errors = []
    symbol_table = {}
    function_table = {}

    analyze_node(ast)

    return semantic_errors
