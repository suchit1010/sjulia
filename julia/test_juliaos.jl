println("Testing JuliaOS module loading...")
try
    using JuliaOS
    println("✅ JuliaOS module loaded successfully!")
    
    # Try to access some functions
    if isdefined(JuliaOS, :initialize)
        println("✅ initialize function is available")
    else
        println("⚠️  initialize function not found")
    end
    
    # Check available exports
    println("Available exports:", names(JuliaOS))
    
catch e
    println("❌ Error loading JuliaOS module:")
    println(e)
end
