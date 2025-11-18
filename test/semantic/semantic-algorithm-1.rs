// Anthony Herrera León

fn main() {
    // Error 1: Usar variable no declarada
    let resultado = x + 5;
    
    // Error 2: Asignar a variable no mutable
    let y = 10;
    y = 20;
    
    // Error 3: Tipos incompatibles
    let edad: i32 = true;
    
    // Error 4: Usar variable no declarada en condición
    if z > 10 {
        println!("Mayor");
    }
    
    // Error 5: Llamar función no declarada
    let suma = sumar(5, 10);
    
    // Error 6: Array con tipos inconsistentes
    let arr = [1, 2, 3.5, 4];
    
    // Error 7: Condición no booleana
    let num = 5;
    if num {
        println!("Error");
    }
    
    // Error 8: Índice no entero
    let datos = [1, 2, 3];
    let valor = datos[3.5];
}

// Error 9: Función con argumentos incorrectos
fn multiplicar(a: i32, b: i32) -> i32 {
    return a * b;
}

fn test() {
    // Error 10: Número incorrecto de argumentos
    let result = multiplicar(5);
    
    // Error 11: Tipo de argumento incorrecto
    let result2 = multiplicar("hola", 10);
}

// Error 12: Return fuera de función
return 5;

// Error 13: Break fuera de loop
fn otra_funcion() {
    break;
}

// Error 14: Tipo de retorno incorrecto
fn division(a: i32, b: i32) -> i32 {
    return 3.14;
}

// Error 15: Falta return en función con tipo de retorno
fn resta(a: i32, b: i32) -> i32 {
    let resultado = a - b;
}