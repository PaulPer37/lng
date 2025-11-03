// Paul Perdomo
let mut contador = 0;
let x = 42;
let y = 3.1415;
let z = 0.0;
let name = "Juan \"Pérez\"";       
let single = 'a';
let esc_char = '\n';
let bad_char = '@';                 
fn suma(a: i32, b: i32) -> i32 {
    return a + b;
}

fn main() {
    println!("Iniciando programa, contador = {}", contador);
    contador += 1;
    if contador >= 10 {
        print("límite alcanzado");
    } else {
        // probar comentarios de línea
        /* comentario multilínea
           con salto de línea y texto complejo: 1234 /= != && || -> { } */
        for i in [1, 2, 3] {
            // operaciones aritméticas y asignaciones compuestas
            x = x + i;
            x -= 1;
            y *= 2.0;
            z /= 1.0;
            let v = vec![1, 2, 3];
            let b = true;
            let f = false;
            if b && !f || (i == 2) {
                println!("condición verdadera: i = {}", i);
            }
        }
    }

    // expresiones con comparadores
    if x == 100 {
        println!("x es 100");
    } else if x != 100 {
        println!("x no es 100");
    }

    // probar operador flecha y dos puntos
    let func = fn(a: i32) -> i32 { return a * 2; };
    let map_val: i32 = func(5);

    // caso con floats e integers mezclados
    let mix = 10 + 2.5 * 3 - 1 % 2;
}