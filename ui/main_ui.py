import tkinter as tk
from tkinter import ttk, scrolledtext, filedialog, messagebox
import os
import sys
from datetime import datetime
import getpass
import contextlib
from io import StringIO

# Agregar el directorio src al path
HERE = os.path.dirname(os.path.abspath(__file__))
PARENT = os.path.dirname(HERE)
SRC = os.path.join(PARENT, "src")
if SRC not in sys.path:
    sys.path.insert(0, SRC)

import lexer as lexmod
import parser as parsemod
import semantic as semmod
import utils


class RustCompilerUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Rust Analyzer - Compilador")
        self.root.geometry("1200x700")
        self.root.configure(bg="#1e1e1e")
        
        # Variables
        self.current_file = None
        self.logs_dir = os.path.join(PARENT, "logs")
        
        # Crear carpeta de logs si no existe
        if not os.path.exists(self.logs_dir):
            os.makedirs(self.logs_dir)
        
        self.setup_ui()
        
    def setup_ui(self):
        # Frame principal
        main_frame = tk.Frame(self.root, bg="#1e1e1e")
        main_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Panel superior - Botones
        top_frame = tk.Frame(main_frame, bg="#2d2d30", height=50)
        top_frame.pack(fill=tk.X, pady=(0, 5))
        top_frame.pack_propagate(False)
        
        # Botones
        btn_style = {
            "bg": "#0e639c",
            "fg": "white",
            "activebackground": "#1177bb",
            "activeforeground": "white",
            "relief": tk.FLAT,
            "padx": 15,
            "pady": 8,
            "font": ("Segoe UI", 10)
        }
        
        tk.Button(top_frame, text="Abrir Archivo", command=self.open_file, **btn_style).pack(side=tk.LEFT, padx=5, pady=8)
        tk.Button(top_frame, text="Guardar", command=self.save_file, **btn_style).pack(side=tk.LEFT, padx=5, pady=8)
        tk.Button(top_frame, text="Analizar Léxico", command=self.analyze_lexer, **btn_style).pack(side=tk.LEFT, padx=5, pady=8)
        tk.Button(top_frame, text="Analizar Sintáctico", command=self.analyze_syntax, **btn_style).pack(side=tk.LEFT, padx=5, pady=8)
        tk.Button(top_frame, text="Analizar Semántico", command=self.analyze_semantic, **btn_style).pack(side=tk.LEFT, padx=5, pady=8)
        tk.Button(top_frame, text="Limpiar", command=self.clear_output, **btn_style).pack(side=tk.LEFT, padx=5, pady=8)
        
        # Panel de contenido
        content_frame = tk.Frame(main_frame, bg="#1e1e1e")
        content_frame.pack(fill=tk.BOTH, expand=True)
        
        # Panel izquierdo - Editor de código
        left_frame = tk.Frame(content_frame, bg="#1e1e1e")
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        editor_label = tk.Label(left_frame, text="Editor de Código", 
                               bg="#2d2d30", fg="white", 
                               font=("Segoe UI", 10, "bold"), 
                               anchor="w", padx=10, pady=5)
        editor_label.pack(fill=tk.X)
        
        # Editor con números de línea
        editor_container = tk.Frame(left_frame, bg="#1e1e1e")
        editor_container.pack(fill=tk.BOTH, expand=True, padx=(0, 5))
        
        # Números de línea
        self.line_numbers = tk.Text(editor_container, width=4, padx=3, takefocus=0,
                                    border=0, background="#1e1e1e", foreground="#858585",
                                    state="disabled", wrap="none", font=("Consolas", 10))
        self.line_numbers.pack(side=tk.LEFT, fill=tk.Y)
        
        # Editor de texto
        self.code_editor = scrolledtext.ScrolledText(
            editor_container,
            wrap=tk.NONE,
            bg="#1e1e1e",
            fg="#d4d4d4",
            insertbackground="white",
            selectbackground="#264f78",
            font=("Consolas", 10),
            relief=tk.FLAT,
            padx=5,
            pady=5
        )
        self.code_editor.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.code_editor.bind("<KeyRelease>", self.update_line_numbers)
        self.code_editor.bind("<MouseWheel>", self.on_scroll)
        
        # Panel derecho - Salida del análisis
        right_frame = tk.Frame(content_frame, bg="#1e1e1e", width=500)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        right_frame.pack_propagate(False)
        
        output_label = tk.Label(right_frame, text="Salida del Análisis", 
                               bg="#2d2d30", fg="white", 
                               font=("Segoe UI", 10, "bold"), 
                               anchor="w", padx=10, pady=5)
        output_label.pack(fill=tk.X)
        
        self.output_area = scrolledtext.ScrolledText(
            right_frame,
            wrap=tk.WORD,
            bg="#0c0c0c",
            fg="#cccccc",
            insertbackground="white",
            font=("Consolas", 9),
            relief=tk.FLAT,
            padx=10,
            pady=10
        )
        self.output_area.pack(fill=tk.BOTH, expand=True, padx=5, pady=(0, 5))
        
        # Configurar tags para colores
        self.output_area.tag_config("error", foreground="#f48771")
        self.output_area.tag_config("success", foreground="#4ec9b0")
        self.output_area.tag_config("info", foreground="#569cd6")
        self.output_area.tag_config("warning", foreground="#dcdcaa")
        
        # Cargar código de ejemplo
        self.load_example()
        self.update_line_numbers()
        
    def update_line_numbers(self, event=None):
        """Actualiza los números de línea"""
        self.line_numbers.config(state="normal")
        self.line_numbers.delete("1.0", "end")
        
        line_count = self.code_editor.get("1.0", "end-1c").count("\n") + 1
        line_numbers_string = "\n".join(str(i) for i in range(1, line_count + 1))
        self.line_numbers.insert("1.0", line_numbers_string)
        self.line_numbers.config(state="disabled")
        
    def on_scroll(self, event):
        """Sincroniza el scroll entre números de línea y editor"""
        self.line_numbers.yview_scroll(int(-1*(event.delta/120)), "units")
        return "break"
        
    def open_file(self):
        """Abre un archivo de código Rust"""
        filepath = filedialog.askopenfilename(
            title="Abrir archivo",
            filetypes=[("Rust files", "*.rs"), ("All files", "*.*")]
        )
        if filepath:
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    content = f.read()
                self.code_editor.delete('1.0', tk.END)
                self.code_editor.insert('1.0', content)
                self.current_file = filepath
                self.update_line_numbers()
                self.log_message(f"Archivo cargado: {os.path.basename(filepath)}", "info")
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo abrir el archivo:\n{str(e)}")
                
    def save_file(self):
        """Guarda el código actual"""
        if not self.current_file:
            filepath = filedialog.asksaveasfilename(
                title="Guardar archivo",
                defaultextension=".rs",
                filetypes=[("Rust files", "*.rs"), ("All files", "*.*")]
            )
            if not filepath:
                return
            self.current_file = filepath
            
        try:
            content = self.code_editor.get('1.0', 'end-1c')
            with open(self.current_file, 'w', encoding='utf-8') as f:
                f.write(content)
            self.log_message(f"Archivo guardado: {os.path.basename(self.current_file)}", "success")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo guardar el archivo:\n{str(e)}")
            
    def clear_output(self):
        """Limpia el área de salida"""
        self.output_area.delete('1.0', tk.END)
        
    def log_message(self, message, tag="info"):
        """Agrega un mensaje al área de salida"""
        self.output_area.insert(tk.END, message + "\n", tag)
        self.output_area.see(tk.END)
        
    def analyze_lexer(self):
        """Ejecuta el análisis léxico"""
        self.clear_output()
        code = self.code_editor.get('1.0', 'end-1c')
        
        if not code.strip():
            self.log_message("⚠ No hay código para analizar", "warning")
            return
            
        self.log_message("=" * 60, "info")
        self.log_message("ANÁLISIS LÉXICO", "info")
        self.log_message("=" * 60, "info")
        
        try:
            lexmod.lexer.lineno = 1
            err_capture = StringIO()
            tokens = []
            
            with contextlib.redirect_stdout(err_capture):
                lexmod.lexer.input(code)
                for tok in lexmod.lexer:
                    tokens.append(tok)
            
            user = getpass.getuser() or "anon"
            filename = os.path.basename(self.current_file) if self.current_file else "codigo.rs"
            
            logpath = utils.save_lexer_log(user, tokens, err_capture.getvalue(), filename, self.logs_dir)
            
            self.log_message(f"\n✓ Tokens reconocidos: {len(tokens)}", "success")
            self.log_message(f"✓ Log guardado en: {os.path.basename(logpath)}", "success")
            
            # Mostrar algunos tokens
            if tokens:
                self.log_message("\nPrimeros 10 tokens:", "info")
                for tok in tokens[:10]:
                    self.log_message(f"  {tok.type:12s} | Line {tok.lineno:3d} | {repr(tok.value)}")
                if len(tokens) > 10:
                    self.log_message(f"  ... y {len(tokens) - 10} tokens más")
                    
            errors = err_capture.getvalue()
            if errors.strip():
                self.log_message("\n⚠ Errores léxicos:", "error")
                self.log_message(errors, "error")
            else:
                self.log_message("\n✓ Sin errores léxicos", "success")
                
        except Exception as e:
            self.log_message(f"\n❌ Error durante análisis léxico: {str(e)}", "error")
            
    def analyze_syntax(self):
        """Ejecuta el análisis sintáctico"""
        self.clear_output()
        code = self.code_editor.get('1.0', 'end-1c')
        
        if not code.strip():
            self.log_message("⚠ No hay código para analizar", "warning")
            return
            
        self.log_message("=" * 60, "info")
        self.log_message("ANÁLISIS SINTÁCTICO", "info")
        self.log_message("=" * 60, "info")
        
        try:
            ast, errors = parsemod.parse_code(code)
            
            user = getpass.getuser() or "anon"
            logpath = utils.save_syntax_log(user, errors, self.logs_dir)
            
            if not errors:
                self.log_message("\n✓ Código analizado correctamente", "success")
                self.log_message(f"✓ Log guardado en: {os.path.basename(logpath)}", "success")
            else:
                self.log_message(f"\n✗ Se encontraron {len(errors)} errores sintácticos:", "error")
                for i, err in enumerate(errors, 1):
                    self.log_message(f"  {i}. {err}", "error")
                self.log_message(f"\n✓ Log guardado en: {os.path.basename(logpath)}", "success")
                
        except Exception as e:
            self.log_message(f"\n❌ Error durante análisis sintáctico: {str(e)}", "error")
            
    def analyze_semantic(self):
        """Ejecuta el análisis semántico"""
        self.clear_output()
        code = self.code_editor.get('1.0', 'end-1c')
        
        if not code.strip():
            self.log_message("⚠ No hay código para analizar", "warning")
            return
            
        self.log_message("=" * 60, "info")
        self.log_message("ANÁLISIS COMPLETO (Léxico + Sintáctico + Semántico)", "info")
        self.log_message("=" * 60, "info")
        
        try:
            # Primero sintáctico
            self.log_message("\n[1/3] Analizando sintaxis...", "info")
            ast, syntax_errors = parsemod.parse_code(code)
            
            if syntax_errors:
                self.log_message(f"✗ {len(syntax_errors)} errores sintácticos encontrados", "error")
                for err in syntax_errors[:5]:
                    self.log_message(f"  - {err}", "error")
                self.log_message("\n⚠ Análisis semántico omitido debido a errores sintácticos", "warning")
                return
                
            self.log_message("✓ Sintaxis correcta", "success")
            
            # Luego semántico
            self.log_message("\n[2/3] Analizando semántica...", "info")
            errors = semmod.analyze(ast)
            
            user = getpass.getuser() or "anon"
            logpath = utils.save_semantic_log(user, errors, semmod.symbol_table, 
                                             semmod.function_table, self.logs_dir)
            
            if not errors:
                self.log_message("\n✓ Análisis semántico completado sin errores", "success")
                self.log_message(f"✓ Variables declaradas: {len(semmod.symbol_table)}", "info")
                self.log_message(f"✓ Funciones declaradas: {len(semmod.function_table)}", "info")
                
                # Mostrar tablas
                if semmod.symbol_table:
                    self.log_message("\nTabla de Símbolos:", "info")
                    for var, info in list(semmod.symbol_table.items())[:5]:
                        self.log_message(f"  {var}: {info}")
                        
                if semmod.function_table:
                    self.log_message("\nTabla de Funciones:", "info")
                    for func, info in semmod.function_table.items():
                        self.log_message(f"  {func}: {info}")
            else:
                self.log_message(f"\n✗ Se encontraron {len(errors)} errores semánticos:", "error")
                for i, err in enumerate(errors, 1):
                    self.log_message(f"  {i}. {err}", "error")
                    
            self.log_message(f"\n✓ Log guardado en: {os.path.basename(logpath)}", "success")
            
        except Exception as e:
            self.log_message(f"\n❌ Error durante análisis semántico: {str(e)}", "error")
            import traceback
            self.log_message(traceback.format_exc(), "error")
            
    def load_example(self):
        """Carga un código de ejemplo"""
        example = """// Ejemplo de código Rust
fn main() {
    let x = 42;
    let mut y = 3.14;
    
    println!("Hola Mundo");
    
    if x > 10 {
        println!("x es mayor que 10");
    }
    
    let resultado = suma(5, 10);
}

fn suma(a: i32, b: i32) -> i32 {
    return a + b;
}"""
        self.code_editor.insert('1.0', example)


def main():
    root = tk.Tk()
    app = RustCompilerUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()