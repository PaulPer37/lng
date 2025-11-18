

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
        function_table[name] = {
            'params': param_types,
            'return_type': return_type
        }
        
        # Analizar el cuerpo en contexto de función
        old_context = context.copy()
        context['in_function'] = name
        context['return_type'] = return_type
        
        # Agregar parámetros a tabla de símbolos temporal
        for param in params:
            param_name = param[1]
            param_type = param[2]
            symbol_table[param_name] = {
                'type': param_type,
                'mutable': False,
                'initialized': True
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
        if len(args) != len(func_info['params']):
            add_error(line, f"Función '{name}' espera {len(func_info['params'])} argumentos, se recibieron {len(args)}")
            return
        
        # Verificar tipos de argumentos
        for i, (arg, expected_type) in enumerate(zip(args, func_info['params'])):
            arg_type = get_expression_type(arg)
            if arg_type and expected_type and arg_type != expected_type:
                add_error(line, f"Argumento {i+1} de '{name}': se esperaba '{expected_type}', se obtuvo '{arg_type}'")


def check_control_flow(node, line=0):
    """
    Regla 2: Verifica contexto de break, continue y return
    """
    if node[0] == "break" or node[0] == "continue":
        if not context['in_loop']:
            add_error(line, f"'{node[0]}' solo puede usarse dentro de un loop")
    
    elif node[0] == "return":
        if context['in_function'] is None:
            add_error(line, "'return' solo puede usarse dentro de una función")
            return
        
        return_value = node[1] if len(node) > 1 else None
        expected_type = context['return_type']
        
        if expected_type is None and return_value is not None:
            add_error(line, f"Función '{context['in_function']}' no debe retornar un valor")
        elif expected_type is not None and return_value is None:
            add_error(line, f"Función '{context['in_function']}' debe retornar un valor de tipo '{expected_type}'")
        elif expected_type is not None and return_value is not None:
            return_type = get_expression_type(return_value)
            if return_type and return_type != expected_type:
                add_error(line, f"Tipo de retorno incorrecto: se esperaba '{expected_type}', se obtuvo '{return_type}'")


# ============================================================================
# FUNCIÓN PRINCIPAL DE ANÁLISIS
# ============================================================================

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
            old_in_loop = context['in_loop']
            context['in_loop'] = True
            analyze_node(node[2], line)  # Analizar cuerpo
            context['in_loop'] = old_in_loop
    
    # Danilo Drouet - Funciones y control de flujo
    elif node_type == "func_decl":
        check_function_declaration(node, line)
    elif node_type == "func_call":
        check_function_call(node, line)
    elif node_type in ["return", "break", "continue"]:
        check_control_flow(node, line)
    
    # For loops (Paul)
    elif node_type == "for":
        old_in_loop = context['in_loop']
        context['in_loop'] = True
        # Agregar variable de iteración a tabla de símbolos
        iter_var = node[1]
        symbol_table[iter_var] = {'type': 'i32', 'mutable': False, 'initialized': True}
        analyze_node(node[3], line)  # Analizar cuerpo
        context['in_loop'] = old_in_loop
    
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