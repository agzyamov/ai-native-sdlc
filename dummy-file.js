// This is a dummy JavaScript file for testing the AI code review workflow
// It contains some intentional issues for the AI to review

function calculateSum(a, b) {
    // Missing input validation
    return a + b;
}

function processArray(arr) {
    // Potential null/undefined issue
    for (let i = 0; i < arr.length; i++) {
        console.log(arr[i]);
    }
}

// Unused variable
const unusedVar = "This variable is never used";

// Function with potential division by zero
function divide(x, y) {
    return x / y; // No check for y === 0
}

// Export without proper error handling
module.exports = {
    calculateSum,
    processArray,
    divide
};