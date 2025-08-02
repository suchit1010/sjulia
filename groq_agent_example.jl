#!/usr/bin/env julia

"""
JuliaOS Groq Agent Example
A simple Julia script demonstrating how to interact with the Groq AI agent
"""

using HTTP
using JSON
using DotEnv

# Load environment variables
DotEnv.load!()

# Configuration
const BASE_URL = "http://localhost:8052/api/v1"
const AGENT_ID = "groq-ai-agent"

"""
Create and start the Groq AI agent
"""
function setup_groq_agent()
    println("🚀 Setting up Groq AI Agent...")
    
    # Agent configuration
    agent_config = Dict(
        "id" => AGENT_ID,
        "name" => "Groq AI Assistant",
        "description" => "A comprehensive AI agent powered by Groq's fast LLM inference",
        "blueprint" => Dict(
            "tools" => [
                Dict(
                    "name" => "groq_agent",
                    "config" => Dict(
                        "model_name" => "llama-3.3-70b-versatile",
                        "temperature" => 0.7,
                        "max_tokens" => 2048,
                        "top_p" => 1.0,
                        "frequency_penalty" => 0.0,
                        "presence_penalty" => 0.0
                    )
                )
            ],
            "strategy" => Dict(
                "name" => "ai_assistant",
                "config" => Dict(
                    "default_task_type" => "chat",
                    "enable_context_memory" => true,
                    "max_context_length" => 4000
                )
            ),
            "trigger" => Dict(
                "type" => "webhook",
                "params" => Dict()
            )
        )
    )
    
    try
        # Create the agent
        response = HTTP.post(
            "$BASE_URL/agents/",
            ["Content-Type" => "application/json"],
            JSON.json(agent_config)
        )
        println("✅ Agent created successfully!")
        
        # Start the agent
        start_config = Dict("state" => "running")
        HTTP.put(
            "$BASE_URL/agents/$AGENT_ID",
            ["Content-Type" => "application/json"],
            JSON.json(start_config)
        )
        println("✅ Agent started and running!")
        
        return true
    catch e
        println("❌ Error setting up agent: $e")
        return false
    end
end

"""
Send a request to the Groq agent
"""
function ask_groq_agent(prompt::String, task_type::String="chat"; kwargs...)
    payload = Dict(
        "prompt" => prompt,
        "task_type" => task_type,
        kwargs...
    )
    
    try
        response = HTTP.post(
            "$BASE_URL/agents/$AGENT_ID/trigger",
            ["Content-Type" => "application/json"],
            JSON.json(payload)
        )
        
        result = JSON.parse(String(response.body))
        return result
    catch e
        println("❌ Error communicating with agent: $e")
        return nothing
    end
end

"""
Run interactive demo
"""
function run_demo()
    println("=" ^ 60)
    println("🤖 JuliaOS Groq AI Agent Demo")
    println("=" ^ 60)
    println()
    
    # Setup agent
    if !setup_groq_agent()
        println("Failed to setup agent. Exiting.")
        return
    end
    
    println()
    println("🧪 Running AI Task Demonstrations...")
    println()
    
    # Demo 1: Simple Chat
    println("💬 Demo 1: Simple Chat")
    println("-" ^ 30)
    result = ask_groq_agent(
        "Hello! Can you explain what JuliaOS is in simple terms?",
        "chat",
        style="friendly"
    )
    if result !== nothing && result["success"]
        println("🤖 Response: $(result["output"])")
    end
    println()
    
    # Demo 2: Code Generation
    println("👨‍💻 Demo 2: Julia Code Generation")
    println("-" ^ 35)
    result = ask_groq_agent(
        "Create a Julia function that implements binary search",
        "code_generation",
        language="julia",
        style="technical"
    )
    if result !== nothing && result["success"]
        println("🤖 Generated Code:")
        println(result["output"])
    end
    println()
    
    # Demo 3: Analysis
    println("📊 Demo 3: Technical Analysis")
    println("-" ^ 30)
    result = ask_groq_agent(
        "Analyze the advantages and disadvantages of using Julia for AI/ML development",
        "analysis",
        style="technical",
        max_length=1000
    )
    if result !== nothing && result["success"]
        println("🤖 Analysis:")
        println(result["output"])
    end
    println()
    
    # Demo 4: Problem Solving
    println("🧩 Demo 4: Problem Solving")
    println("-" ^ 28)
    result = ask_groq_agent(
        "How can we optimize performance in a distributed Julia application?",
        "problem_solving",
        context="Consider both computational and memory optimization strategies",
        style="technical"
    )
    if result !== nothing && result["success"]
        println("🤖 Solution:")
        println(result["output"])
    end
    println()
    
    # Demo 5: Creative Writing
    println("✍️ Demo 5: Creative Writing")
    println("-" ^ 28)
    result = ask_groq_agent(
        "Write a short story about an AI agent that becomes self-aware in a Julia environment",
        "creative_writing",
        style="imaginative",
        max_length=800
    )
    if result !== nothing && result["success"]
        println("🤖 Story:")
        println(result["output"])
    end
    println()
    
    println("=" ^ 60)
    println("✨ Demo completed! Your Groq AI agent is ready for use.")
    println("You can now interact with it via the API endpoints.")
    println("=" ^ 60)
end

"""
Interactive mode for testing
"""
function interactive_mode()
    println("🔄 Entering interactive mode...")
    println("Type 'quit' to exit, 'help' for available commands")
    println()
    
    while true
        print("julia-groq> ")
        input = readline()
        
        if lowercase(strip(input)) == "quit"
            println("👋 Goodbye!")
            break
        elseif lowercase(strip(input)) == "help"
            println("""
Available commands:
- quit: Exit interactive mode
- help: Show this help message
- chat <message>: Send a chat message
- code <description>: Generate code
- analyze <topic>: Perform analysis
- solve <problem>: Get problem-solving help

Or just type your message directly for chat mode.
            """)
            continue
        elseif isempty(strip(input))
            continue
        end
        
        # Parse command
        parts = split(input, " ", limit=2)
        if length(parts) >= 2 && parts[1] in ["chat", "code", "analyze", "solve"]
            command, message = parts[1], parts[2]
            task_type = Dict(
                "chat" => "chat",
                "code" => "code_generation",
                "analyze" => "analysis",
                "solve" => "problem_solving"
            )[command]
        else
            task_type = "chat"
            message = input
        end
        
        # Send request
        println("🤔 Thinking...")
        result = ask_groq_agent(message, task_type)
        
        if result !== nothing && result["success"]
            println("🤖 $(result["output"])")
        else
            println("❌ Sorry, I couldn't process that request.")
        end
        println()
    end
end

"""
Main function
"""
function main()
    if length(ARGS) == 0
        run_demo()
    elseif ARGS[1] == "interactive" || ARGS[1] == "-i"
        setup_groq_agent()
        interactive_mode()
    elseif ARGS[1] == "setup"
        setup_groq_agent()
    else
        println("""
Usage: julia groq_agent_example.jl [command]

Commands:
  (no args)    - Run demonstration
  interactive  - Enter interactive mode
  setup        - Just setup the agent
        """)
    end
end

# Run if called directly
if abspath(PROGRAM_FILE) == @__FILE__
    main()
end
