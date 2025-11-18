"""
Utilidades compartidas para el analizador de Rust.
Contiene funciones para logging y manejo de archivos.
"""

import os
import datetime


def save_syntax_log(github_user, errors):
    """
    Guarda los errores sintácticos en un archivo de log con el formato especificado.

    Args:
        github_user (str): Usuario de GitHub para el nombre del archivo
        errors (list): Lista de mensajes de error

    Returns:
        str: Ruta del archivo de log generado
    """
    logs_dir = "logs/parser"
    if not os.path.exists(logs_dir):
        os.makedirs(logs_dir)

    now = datetime.datetime.now()
    filename = f"{logs_dir}/sintactico-{github_user}-{now.strftime('%d%m%Y-%Hh%M')}.txt"

    with open(filename, "w", encoding="utf-8") as f:
        f.write(f"=== LOG DE ANÁLISIS SINTÁCTICO ===\n")
        f.write(f"Usuario: {github_user}\n")
        f.write(f"Fecha: {now.strftime('%d/%m/%Y')}\n")
        f.write(f"Hora: {now.strftime('%H:%M:%S')}\n")
        f.write(f"Total de errores: {len(errors)}\n")
        f.write(f"=" * 50 + "\n\n")

        if errors:
            for i, error in enumerate(errors, 1):
                f.write(f"{i}. {error}\n")
        else:
            f.write("✓ No se encontraron errores sintácticos.\n")

        f.write("\n" + "=" * 50 + "\n")
        f.write("Análisis completado exitosamente.\n")

    return filename


def save_lexer_log(github_user, tokens, errors_text, source_file):
    """
    Guarda el log del análisis léxico.

    Args:
        github_user (str): Usuario de GitHub para el nombre del archivo
        tokens (list): Lista de tokens reconocidos
        errors_text (str): Texto de errores capturados
        source_file (str): Nombre del archivo fuente analizado

    Returns:
        str: Ruta del archivo de log generado
    """
    logs_dir = "logs/lexer"
    if not os.path.exists(logs_dir):
        os.makedirs(logs_dir)

    now = datetime.datetime.now()
    filename = f"{logs_dir}/lexico-{github_user}-{now.day:02d}-{now.month:02d}-{now.year}-{now.hour:02d}h{now.minute:02d}.txt"

    with open(filename, "w", encoding="utf-8") as f:
        f.write(f"LEXICO LOG - file: {source_file}\n")
        f.write(f"Generated: {now.isoformat()}\n")
        f.write(f"User: {github_user}\n")
        f.write("=" * 60 + "\n\n")
        f.write("TOKENS\n")
        f.write("-" * 60 + "\n")

        if tokens:
            for t in tokens:
                f.write(
                    f"LINE {t.lineno:4d} | TYPE: {t.type:12s} | POS: {t.lexpos:6d} | VALUE: {repr(t.value)}\n"
                )
        else:
            f.write("No tokens recognized.\n")

        f.write("\n" + "-" * 60 + "\n\n")
        f.write("ERRORS / LEXER OUTPUT\n")
        f.write("-" * 60 + "\n")

        if errors_text.strip():
            f.write(errors_text)
        else:
            f.write("No errors reported by lexer (t_error did not print anything).\n")

    return filename


def save_semantic_log(github_user, errors, symbol_table, function_table):
    """
    Guarda el log del análisis semántico con el formato especificado.

    Args:
        github_user (str): Usuario de GitHub para el nombre del archivo
        errors (list): Lista de errores semánticos
        symbol_table (dict): Tabla de símbolos del análisis
        function_table (dict): Tabla de funciones del análisis

    Returns:
        str: Ruta del archivo de log generado
    """
    logs_dir = "logs/semantic"
    if not os.path.exists(logs_dir):
        os.makedirs(logs_dir)

    now = datetime.datetime.now()
    filename = f"{logs_dir}/semantico-{github_user}-{now.strftime('%d%m%Y-%Hh%M')}.txt"

    with open(filename, "w", encoding="utf-8") as f:
        f.write(f"=== LOG DE ANÁLISIS SEMÁNTICO ===\n")
        f.write(f"Usuario: {github_user}\n")
        f.write(f"Fecha: {now.strftime('%d/%m/%Y')}\n")
        f.write(f"Hora: {now.strftime('%H:%M:%S')}\n")
        f.write(f"Total de errores: {len(errors)}\n")
        f.write(f"=" * 50 + "\n\n")

        if errors:
            for i, error in enumerate(errors, 1):
                f.write(f"{i}. {error}\n")
        else:
            f.write("✓ No se encontraron errores semánticos.\n\n")

            f.write("TABLA DE SÍMBOLOS\n")
            f.write("-" * 50 + "\n")
            if symbol_table:
                for var, info in symbol_table.items():
                    f.write(f"  {var}: {info}\n")
            else:
                f.write("  (vacía)\n")

            f.write("\nTABLA DE FUNCIONES\n")
            f.write("-" * 50 + "\n")
            if function_table:
                for func, info in function_table.items():
                    f.write(f"  {func}: {info}\n")
            else:
                f.write("  (vacía)\n")

        f.write("\n" + "=" * 50 + "\n")
        f.write("Análisis completado exitosamente.\n")

    return filename
