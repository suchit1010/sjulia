println("Testing AgentCore module access...")
try
    using JuliaOS
    
    # Try different ways to access AgentCore
    println("Checking if AgentCore is available in JuliaOS...")
    if isdefined(JuliaOS, :AgentCore)
        println("✅ AgentCore found in JuliaOS")
    else
        println("⚠️  AgentCore not directly in JuliaOS")
    end
    
    # Check JuliaOSFramework
    if isdefined(JuliaOS, :JuliaOSFramework)
        println("✅ JuliaOSFramework found")
        framework = JuliaOS.JuliaOSFramework
        if isdefined(framework, :AgentCore)
            println("✅ AgentCore found in JuliaOSFramework")
            agent_core = framework.AgentCore
            
            # Check for the types we need
            if isdefined(agent_core, :AgentConfig)
                println("✅ AgentConfig found")
            else
                println("❌ AgentConfig not found")
            end
        else
            println("❌ AgentCore not found in JuliaOSFramework")
        end
    else
        println("❌ JuliaOSFramework not found")
    end
    
catch e
    println("❌ Error:")
    println(e)
    println(stacktrace())
end
