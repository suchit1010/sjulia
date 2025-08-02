# JuliaOS Groq Agent Demo Script (PowerShell)
# This script demonstrates how to create and use a Groq-powered AI agent

$URL_BASE = "http://localhost:8052/api/v1"

Write-Host "=== JuliaOS Groq Agent Demo ===" -ForegroundColor Green
Write-Host ""

Write-Host "1. Checking current agents:" -ForegroundColor Yellow
try {
    $response = Invoke-RestMethod -Uri "$URL_BASE/agents/" -Method GET
    $response | ConvertTo-Json -Depth 10
} catch {
    Write-Host "Error checking agents: $_" -ForegroundColor Red
}
Write-Host ""

Write-Host "2. Creating Groq AI Agent:" -ForegroundColor Yellow
$createAgentData = Get-Content "data/create-groq-agent.json" -Raw
try {
    $response = Invoke-RestMethod -Uri "$URL_BASE/agents/" -Method POST -Body $createAgentData -ContentType "application/json"
    Write-Host "Agent created successfully!" -ForegroundColor Green
} catch {
    Write-Host "Error creating agent: $_" -ForegroundColor Red
}
Write-Host ""

Write-Host "3. Agents after creation:" -ForegroundColor Yellow
try {
    $response = Invoke-RestMethod -Uri "$URL_BASE/agents/" -Method GET
    $response | ConvertTo-Json -Depth 10
} catch {
    Write-Host "Error checking agents: $_" -ForegroundColor Red
}
Write-Host ""

Write-Host "4. Starting the Groq agent:" -ForegroundColor Yellow
$runAgentData = '{"state": "RUNNING"}'
try {
    $response = Invoke-RestMethod -Uri "$URL_BASE/agents/groq-ai-agent" -Method PUT -Body $runAgentData -ContentType "application/json"
    Write-Host "Agent started successfully!" -ForegroundColor Green
} catch {
    Write-Host "Error starting agent: $_" -ForegroundColor Red
}
Write-Host ""

Write-Host "5. Testing different task types with the Groq agent:" -ForegroundColor Yellow
Write-Host ""

# Test 1: Simple chat
Write-Host "Test 1: Simple Chat" -ForegroundColor Cyan
$chatData = @{
    prompt = "Hello! Can you tell me about artificial intelligence?"
    task_type = "chat"
    style = "friendly"
} | ConvertTo-Json
try {
    $response = Invoke-RestMethod -Uri "$URL_BASE/agents/groq-ai-agent/trigger" -Method POST -Body $chatData -ContentType "application/json"
    Write-Host "Response: $($response.output)" -ForegroundColor White
} catch {
    Write-Host "Error in chat test: $_" -ForegroundColor Red
}
Write-Host ""

# Test 2: Code generation
Write-Host "Test 2: Code Generation" -ForegroundColor Cyan
$codeData = @{
    prompt = "Create a Python function that calculates the Fibonacci sequence"
    task_type = "code_generation"
    language = "python"
    style = "technical"
} | ConvertTo-Json
try {
    $response = Invoke-RestMethod -Uri "$URL_BASE/agents/groq-ai-agent/trigger" -Method POST -Body $codeData -ContentType "application/json"
    Write-Host "Response: $($response.output)" -ForegroundColor White
} catch {
    Write-Host "Error in code generation test: $_" -ForegroundColor Red
}
Write-Host ""

# Test 3: Analysis
Write-Host "Test 3: Analysis" -ForegroundColor Cyan
$analysisData = @{
    prompt = "Analyze the pros and cons of renewable energy"
    task_type = "analysis"
    style = "formal"
    max_length = 1000
} | ConvertTo-Json
try {
    $response = Invoke-RestMethod -Uri "$URL_BASE/agents/groq-ai-agent/trigger" -Method POST -Body $analysisData -ContentType "application/json"
    Write-Host "Response: $($response.output)" -ForegroundColor White
} catch {
    Write-Host "Error in analysis test: $_" -ForegroundColor Red
}
Write-Host ""

# Test 4: Creative writing
Write-Host "Test 4: Creative Writing" -ForegroundColor Cyan
$creativeData = @{
    prompt = "Write a short story about a robot discovering emotions"
    task_type = "creative_writing"
    style = "imaginative"
    max_length = 800
} | ConvertTo-Json
try {
    $response = Invoke-RestMethod -Uri "$URL_BASE/agents/groq-ai-agent/trigger" -Method POST -Body $creativeData -ContentType "application/json"
    Write-Host "Response: $($response.output)" -ForegroundColor White
} catch {
    Write-Host "Error in creative writing test: $_" -ForegroundColor Red
}
Write-Host ""

# Test 5: Problem solving
Write-Host "Test 5: Problem Solving" -ForegroundColor Cyan
$problemData = @{
    prompt = "How can we reduce plastic waste in oceans?"
    task_type = "problem_solving"
    context = "Consider both technological and policy solutions"
    style = "analytical"
} | ConvertTo-Json
try {
    $response = Invoke-RestMethod -Uri "$URL_BASE/agents/groq-ai-agent/trigger" -Method POST -Body $problemData -ContentType "application/json"
    Write-Host "Response: $($response.output)" -ForegroundColor White
} catch {
    Write-Host "Error in problem solving test: $_" -ForegroundColor Red
}
Write-Host ""

Write-Host "=== Demo Complete ===" -ForegroundColor Green
Write-Host "Your Groq AI agent is now running and ready to handle various AI tasks!" -ForegroundColor Green
Write-Host "You can interact with it using the API endpoints shown above." -ForegroundColor Green
