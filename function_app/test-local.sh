#!/bin/bash
# Quick test script for local Azure Function

set -e

echo "=== Azure Function Local Test ==="
echo ""

# Check if sample payload exists
SAMPLE="../specs/001-ado-github-spec/contracts/sample-ado-hook.json"
if [ ! -f "$SAMPLE" ]; then
    echo "❌ Sample payload not found: $SAMPLE"
    exit 1
fi

echo "📝 Sample payload:"
cat "$SAMPLE" | jq -r '.eventType, .resource.workItemId'
echo ""

# Test 1: Valid payload (should succeed if PATs are set)
echo "🧪 Test 1: Valid ADO hook payload"
curl -s -X POST http://localhost:7071/api/spec-dispatch \
  -H "Content-Type: application/json" \
  -d @"$SAMPLE" \
  -w "\nHTTP Status: %{http_code}\n"
echo ""

# Test 2: Invalid event type (should return 403)
echo "🧪 Test 2: Invalid event type (expect 403)"
curl -s -X POST http://localhost:7071/api/spec-dispatch \
  -H "Content-Type: application/json" \
  -d '{
    "eventType": "workitem.created",
    "resource": {"workItemId": 123}
  }' \
  -w "\nHTTP Status: %{http_code}\n"
echo ""

# Test 3: Missing work item ID (should return 400)
echo "🧪 Test 3: Missing workItemId (expect 400)"
curl -s -X POST http://localhost:7071/api/spec-dispatch \
  -H "Content-Type: application/json" \
  -d '{
    "eventType": "workitem.updated",
    "resource": {}
  }' \
  -w "\nHTTP Status: %{http_code}\n"
echo ""

# Test 4: Invalid JSON (should return 400)
echo "🧪 Test 4: Invalid JSON (expect 400)"
curl -s -X POST http://localhost:7071/api/spec-dispatch \
  -H "Content-Type: application/json" \
  -d 'not json' \
  -w "\nHTTP Status: %{http_code}\n"
echo ""

echo "✅ Tests complete!"
echo ""
echo "Expected results:"
echo "  Test 1: 204 (if PATs valid + real ADO work item) or 500 (if PATs missing)"
echo "  Test 2: 403 (validation failed)"
echo "  Test 3: 400 (bad request)"
echo "  Test 4: 400 (bad request)"
