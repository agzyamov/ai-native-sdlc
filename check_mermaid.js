#!/usr/bin/env node

const fs = require('fs');

const filePath = process.argv[2] || './PM_Framework.md';
const content = fs.readFileSync(filePath, 'utf8');

// Extract mermaid code - support both GitHub (```mermaid) and Azure DevOps (::: mermaid) syntax
const mermaidRegex = /(?:```mermaid|::: mermaid)\n([\s\S]*?)(?:```|:::)/g;
let match;

console.log('🔍 Checking Mermaid syntax in:', filePath);
console.log('━'.repeat(60));

while ((match = mermaidRegex.exec(content)) !== null) {
    const diagram = match[1];
    const lines = diagram.split('\n');
    
    console.log(`\n📊 Found diagram with ${lines.length} lines`);
    console.log(`First line: ${lines[0]}`);
    
    // Check line 9 specifically (from error message)
    if (lines.length >= 9) {
        console.log(`\n❌ Line 9: ${lines[8]}`);
        
        // Check for issues
        if (lines[8].includes('mindmap')) {
            console.log('⚠️  ERROR: Found "mindmap" where "graph TD" expected');
        }
    }
    
    // Look for mixed diagram types
    lines.forEach((line, idx) => {
        if (line.trim().match(/^(mindmap|graph|flowchart)/)) {
            console.log(`Line ${idx + 1}: Diagram type found: ${line.trim()}`);
        }
    });
}

console.log('\n' + '━'.repeat(60));
