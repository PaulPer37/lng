
// Danilo Drouet - Calculadora

fn sumar(a: i32, b: i32) -> i32 {
    return a + b;
}

fn restar(a: i32, b: i32) -> i32 {
    return a - b;
}

fn multiplicar(a: i32, b: i32) -> i32 {
    return a * b;
}

fn dividir(a: i32, b: i32) -> i32 {
    if b == 0 {
        println!("Error: División por cero");
        return 0;
    } else {
        return a / b;
    }
}

fn main() {
    let x = 10;
    let y = 5;
    
    let suma_result = sumar(x, y);
    let resta_result = restar(x, y);
    let mult_result = multiplicar(x, y);
    let div_result = dividir(x, y);
    
    println!("Suma:", suma_result);
    println!("Resta:", resta_result);
    println!("Multiplicación:", mult_result);
    println!("División:", div_result);
}