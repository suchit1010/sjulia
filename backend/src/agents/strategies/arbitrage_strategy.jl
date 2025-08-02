module ArbitrageStrategy
    using JuliaOSBackend.Agent, JSON3
    function arbitrage_logic(prices::Dict{String, Float64})
        try
            solana_price = get(prices, "solana", 0.0)
            eth_price = get(prices, "ethereum", 0.0)
            if solana_price > 0 && eth_price > 0 && (eth_price - solana_price) / solana_price > 0.01
                response = Agent.useLLM(
                    model="llama3-8b-8192",
                    prompt="Arbitrage: SOL/USDC prices - Solana: $solana_price, Ethereum: $eth_price. Profitable after gas and bridge costs? Return JSON: {decision: Bool, amount: Float64, buy_chain: String, sell_chain: String}",
                    api_key=ENV["GROQ_API_KEY"]
                )
                result = JSON3.read(response)
                return result.decision ? (action="trade", amount=result.amount, buy_chain=result.buy_chain, sell_chain=result.sell_chain) : (action="wait", amount=0.0)
            end
            return (action="wait", amount=0.0)
        catch e
            println("Error in strategy: $e")
            return (action="wait", amount=0.0)
        end
    end
end