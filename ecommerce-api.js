// E-commerce API with intentional security and performance issues
// This file is designed to test the GitHub Copilot CLI code review

const express = require('express');
const mysql = require('mysql');

class ECommerceAPI {
    constructor() {
        // Hardcoded credentials - security issue
        this.db = mysql.createConnection({
            host: 'localhost',
            user: 'admin',
            password: 'password123',
            database: 'ecommerce'
        });
    }
    
    // SQL injection vulnerability
    async getUser(userId) {
        const query = `SELECT * FROM users WHERE id = ${userId}`;
        return new Promise((resolve, reject) => {
            this.db.query(query, (error, results) => {
                if (error) throw error;
                resolve(results[0]);
            });
        });
    }
    
    // No input validation or sanitization
    async createProduct(productData) {
        const { name, price, description } = productData;
        const query = `INSERT INTO products (name, price, description) VALUES ('${name}', ${price}, '${description}')`;
        
        // No error handling
        this.db.query(query);
        return { success: true };
    }
    
    // Inefficient database query - N+1 problem
    async getOrdersWithProducts(userId) {
        const orders = await this.getOrdersByUser(userId);
        
        for (let order of orders) {
            // This creates N+1 queries
            order.products = await this.getProductsByOrder(order.id);
        }
        
        return orders;
    }
    
    // Memory leak potential
    processLargeDataset(data) {
        const cache = new Map();
        
        // Never cleaned up
        for (let item of data) {
            cache.set(item.id, item);
        }
        
        // Missing return
    }
    
    // Synchronous file operations
    saveToFile(data, filename) {
        const fs = require('fs');
        try {
            // Blocking operation
            fs.writeFileSync(filename, JSON.stringify(data));
        } catch (error) {
            // Poor error handling
            console.log('Error saving file');
        }
    }
}

// Global variables
var userSessions = {};
var adminToken = 'super-secret-token';

// Exposed sensitive information
function debugInfo() {
    return {
        dbPassword: 'password123',
        apiKeys: ['key1', 'key2', 'key3'],
        internalPaths: ['/admin', '/debug', '/config']
    };
}

module.exports = ECommerceAPI;