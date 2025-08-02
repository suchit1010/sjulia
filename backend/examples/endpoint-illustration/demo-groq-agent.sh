#!/bin/bash

# JuliaOS Groq Agent Demo Script
# This script demonstrates how to create and use a Groq-powered AI agent

URL_BASE="localhost:8052/api/v1"

echo "=== JuliaOS Groq Agent Demo ==="
echo ""

echo "1. Checking current agents:"
curl -s "$URL_BASE/agents/" | jq '.' || curl -s "$URL_BASE/agents/"
echo ""

echo "2. Creating Groq AI Agent:"
curl -v -X POST -H "Content-Type: application/json" -d "@data/create-groq-agent.json" "$URL_BASE/agents/"
echo ""

echo "3. Agents after creation:"
curl -s "$URL_BASE/agents/" | jq '.' || curl -s "$URL_BASE/agents/"
echo ""

echo "4. Starting the Groq agent:"
curl -v -X PUT -H "Content-Type: application/json" -d '{"state": "running"}' "$URL_BASE/agents/groq-ai-agent"
echo ""

echo "5. Testing different task types with the Groq agent:"
echo ""

# Test 1: Simple chat
echo "Test 1: Simple Chat"
curl -v -X POST -H "Content-Type: application/json" -d '{
    "prompt": "Hello! Can you tell me about artificial intelligence?",
    "task_type": "chat",
    "style": "friendly"
}' "$URL_BASE/agents/groq-ai-agent/trigger"
echo ""

# Test 2: Code generation
echo "Test 2: Code Generation"
curl -v -X POST -H "Content-Type: application/json" -d '{
    "prompt": "Create a Python function that calculates the Fibonacci sequence",
    "task_type": "code_generation",
    "language": "python",
    "style": "technical"
}' "$URL_BASE/agents/groq-ai-agent/trigger"
echo ""

# Test 3: Analysis
echo "Test 3: Analysis"
curl -v -X POST -H "Content-Type: application/json" -d '{
    "prompt": "Analyze the pros and cons of renewable energy",
    "task_type": "analysis",
    "style": "formal",
    "max_length": 1000
}' "$URL_BASE/agents/groq-ai-agent/trigger"
echo ""

# Test 4: Creative writing
echo "Test 4: Creative Writing"
curl -v -X POST -H "Content-Type: application/json" -d '{
    "prompt": "Write a short story about a robot discovering emotions",
    "task_type": "creative_writing",
    "style": "imaginative",
    "max_length": 800
}' "$URL_BASE/agents/groq-ai-agent/trigger"
echo ""

# Test 5: Problem solving
echo "Test 5: Problem Solving"
curl -v -X POST -H "Content-Type: application/json" -d '{
    "prompt": "How can we reduce plastic waste in oceans?",
    "task_type": "problem_solving",
    "context": "Consider both technological and policy solutions",
    "style": "analytical"
}' "$URL_BASE/agents/groq-ai-agent/trigger"
echo ""

echo "=== Demo Complete ==="
echo "Your Groq AI agent is now running and ready to handle various AI tasks!"
echo "You can interact with it using the API endpoints shown above."
