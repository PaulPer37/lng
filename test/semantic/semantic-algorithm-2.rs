// Danilo Drouet

fn main() {
    // ERROR 1: Usar variable no declarada
    let total = precio + 100;
    
    // ERROR 2: Asignar a variable inmutable
    let contador = 0;
    contador = 5;
    
    // ERROR 3: Tipo incompatible en declaración
    let edad: i32 = 25.5;
    
    // ERROR 4: Condición no booleana en if
    let numero = 10;
    if numero {
        println!("Esto está mal");
    }
    
    // ERROR 5: Llamar función no declarada
    let resultado = calcular(5, 10);
    
    // ERROR 6: Array con tipos inconsistentes
    let datos = [1, 2, 3.14, 4, 5];
    
    // ERROR 7: Índice de array no entero
    let valores = [10, 20, 30];
    let item = valores[1.5];
    
    // ERROR 8: Break fuera de loop
    break;
    
    // Función correcta para referencia
    let suma_correcta = sumar(3, 7);
}

// Función declarada correctamente
fn sumar(a: i32, b: i32) -> i32 {
    return a + b;
}

// ERROR 9: Número incorrecto de argumentos
fn probar() {
    let res = sumar(5);
}

// ERROR 10: Tipo de retorno incorrecto
fn dividir(a: i32, b: i32) -> i32 {
    return 3.14;
}