using JuliaOS
println("Testing direct import:")
ac = JuliaOS.JuliaOSFramework.AgentCore
println("AgentConfig: ", isdefined(ac, :AgentConfig))
println("TRADING: ", isdefined(ac, :TRADING))
println("OrderedDictAgentMemory: ", isdefined(ac, :OrderedDictAgentMemory))
println("PriorityAgentQueue: ", isdefined(ac, :PriorityAgentQueue))
println("Skill: ", isdefined(ac, :Skill))
println("SkillState: ", isdefined(ac, :SkillState))

# Try to access them
try
    config = ac.AgentConfig("test", ac.TRADING)
    println("✅ AgentConfig created successfully!")
    println("Config name: ", config.name)
    println("Config type: ", config.type)
catch e
    println("❌ Error creating AgentConfig: ", e)
end
