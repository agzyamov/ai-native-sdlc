// Test file for AI code review workflow
// This file contains various code issues for testing

function buggyFunction(data) {
    // No null check - potential runtime error
    const result = data.map(item => {
        // Potential undefined access
        return item.value * 2;
    });
    
    // Memory leak potential - no cleanup
    const cache = {};
    for (let i = 0; i < 1000000; i++) {
        cache[i] = Math.random();
    }
    
    return result;
}

class Calculator {
    constructor() {
        // Missing initialization
    }
    
    // Method with no error handling
    divide(a, b) {
        return a / b; // Division by zero not handled
    }
    
    // Inefficient algorithm
    factorial(n) {
        if (n <= 1) return 1;
        return n * this.factorial(n - 1); // No memoization
    }
}

// Global variable pollution
var globalCounter = 0;

// Function with magic numbers
function processData(input) {
    // Magic numbers without explanation
    if (input.length > 100) {
        return input.slice(0, 50);
    }
    return input;
}

module.exports = { buggyFunction, Calculator, processData };