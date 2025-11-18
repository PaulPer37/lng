//Paul Perdomo

// Función auxiliar definida antes de ser llamada
fn suma(a: i32, b: i32) -> i32 {
    return a + b;
}

fn main() {
    // 1. Declaración de variables
    // Agregamos 'mut' porque se modifican más abajo (Requerido por check_assignment)
    let mut contador = 0;
    let mut x = 42;
    let mut y = 3.1415;
    let mut z = 10.0;
    
    // Tipos estáticos
    let name = "Juan Perez";       
    let single = 'a';
    let esc_char = '\n';
    
    println!("Iniciando programa");
    println!(contador);

    // 2. Modificación de variable mutable
    contador += 1; 
    
    // 3. Control de flujo
    if contador >= 10 {
        print!("limite alcanzado");
    } else {
        // Estructura Array (Verificado por Paul Perdomo)
        let arr = [1, 2, 3];

        // Loop For con Scope propio
        for i in 0..3 {
            // Operaciones aritméticas con reasignación
            // x debe ser mutable para esto
            x = x + i;
            x -= 1;
            
            // Operaciones de punto flotante
            y *= 2.0;
            z /= 1.0;

            // Estructura Vector (Verificado por Paul Perdomo)
            let v = vec![1, 2, 3];
            
            let b = true;
            let f = false;
            
            // Condiciones booleanas complejas (Verificado por Paul Perdomo)
            if b && !f || i == 2 {
                println!("condicion verdadera");
                println!(i);
            }
        }
    }

    // 4. Expresiones con comparadores
    if x == 100 {
        println!("x es 100");
    } else {
        // CORREGIDO: '!==' no es válido en tu semantic.py, se usa '!='
        if x != 100 {
            println!("x no es 100");
        }
    }

    // 5. Llamada a función (Verificado por Danilo Drouet)
    // Verifica tipos de argumentos (i32, i32) y retorno
    let result = suma(5, 10);

    // 6. Precedencia de operadores
    let mix = 10 + 2 * 3 - 1 % 2;
}