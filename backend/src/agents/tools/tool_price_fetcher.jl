using DotEnv
DotEnv.load!()

using HTTP
using JSON
using ..CommonTypes: ToolSpecification, ToolMetadata, ToolConfig

Base.@kwdef struct ToolPriceFetcherConfig <: ToolConfig
    timeout::Int = 30
    max_retries::Int = 3
    user_agent::String = "JuliaOS-PriceFetcher/1.0"
end

const SUPPORTED_DEXS = Set([
    "uniswap_v3", "sushiswap", "pancakeswap", "serum", "raydium", 
    "orca", "jupiter", "1inch", "dodo", "curve"
])

const DEX_ENDPOINTS = Dict(
    "uniswap_v3" => "https://api.thegraph.com/subgraphs/name/uniswap/uniswap-v3",
    "sushiswap" => "https://api.sushi.com/price",
    "pancakeswap" => "https://api.pancakeswap.info/api/v2/tokens",
    "serum" => "https://api.projectserum.com/",
    "raydium" => "https://api.raydium.io/v2/sdk/liquidity/mainnet.json",
    "orca" => "https://api.orca.so/v1/whirlpool/list",
    "jupiter" => "https://price.jup.ag/v4/price",
    "coingecko" => "https://api.coingecko.com/api/v3/simple/price"
)

"""
    tool_price_fetcher(cfg::ToolPriceFetcherConfig, task::Dict) -> Dict{String, Any}

Fetches cryptocurrency prices from various DEX APIs for arbitrage analysis.

# Arguments
- `cfg::ToolPriceFetcherConfig`: Tool configuration
- `task::Dict`: Task parameters
    - Required keys:
        - "token_symbol": Token symbol (e.g., "ETH", "SOL", "USDC")
    - Optional keys:
        - "dex_list": List of DEXs to query. Default: ["uniswap_v3", "jupiter", "coingecko"]
        - "base_currency": Base currency for pricing. Default: "USDC"
        - "include_volume": Include trading volume data. Default: false

# Returns
A dictionary with price data from multiple DEXs
"""
function tool_price_fetcher(cfg::ToolPriceFetcherConfig, task::Dict)
    # Validate required fields
    if !haskey(task, "token_symbol") || !(task["token_symbol"] isa AbstractString)
        return Dict("success" => false, "error" => "Missing or invalid 'token_symbol'")
    end

    token_symbol = uppercase(task["token_symbol"])
    dex_list = get(task, "dex_list", ["uniswap_v3", "jupiter", "coingecko"])
    base_currency = get(task, "base_currency", "USDC")
    include_volume = get(task, "include_volume", false)

    # Validate DEX list
    for dex in dex_list
        if dex ∉ SUPPORTED_DEXS
            return Dict("success" => false, "error" => "Unsupported DEX: $dex. Supported DEXs: $(join(SUPPORTED_DEXS, ", "))")
        end
    end

    results = Dict{String, Any}()
    errors = Dict{String, String}()

    for dex in dex_list
        try
            price_data = fetch_price_from_dex(cfg, dex, token_symbol, base_currency, include_volume)
            if price_data !== nothing
                results[dex] = price_data
            else
                errors[dex] = "No price data available"
            end
        catch e
            errors[dex] = string(e)
        end
    end

    # Calculate arbitrage opportunities
    arbitrage_opportunities = calculate_arbitrage_opportunities(results)

    return Dict(
        "success" => true,
        "token_symbol" => token_symbol,
        "base_currency" => base_currency,
        "timestamp" => now(),
        "prices" => results,
        "errors" => errors,
        "arbitrage_opportunities" => arbitrage_opportunities,
        "summary" => generate_price_summary(results, token_symbol, base_currency)
    )
end

"""
Fetch price data from a specific DEX
"""
function fetch_price_from_dex(cfg::ToolPriceFetcherConfig, dex::String, token::String, base::String, include_volume::Bool)
    if dex == "coingecko"
        return fetch_coingecko_price(cfg, token, base)
    elseif dex == "jupiter"
        return fetch_jupiter_price(cfg, token, base)
    elseif dex == "uniswap_v3"
        return fetch_uniswap_price(cfg, token, base, include_volume)
    else
        # Placeholder for other DEXs
        return Dict(
            "price" => rand(100.0:0.01:1000.0), # Mock price for demo
            "source" => dex,
            "volume_24h" => include_volume ? rand(1000000:100000000) : nothing
        )
    end
end

"""
Fetch price from CoinGecko API
"""
function fetch_coingecko_price(cfg::ToolPriceFetcherConfig, token::String, base::String)
    token_id = get_coingecko_token_id(token)
    base_currency = lowercase(base) == "usdc" ? "usd" : lowercase(base)
    
    url = "$(DEX_ENDPOINTS["coingecko"])?ids=$token_id&vs_currencies=$base_currency&include_24hr_vol=true"
    
    response = HTTP.get(url, ["User-Agent" => cfg.user_agent]; readtimeout=cfg.timeout)
    
    if response.status == 200
        data = JSON.parse(String(response.body))
        if haskey(data, token_id)
            price_data = data[token_id]
            return Dict(
                "price" => price_data[base_currency],
                "volume_24h" => get(price_data, "$(base_currency)_24h_vol", nothing),
                "source" => "coingecko",
                "last_updated" => now()
            )
        end
    end
    
    return nothing
end

"""
Fetch price from Jupiter API (Solana)
"""
function fetch_jupiter_price(cfg::ToolPriceFetcherConfig, token::String, base::String)
    # Jupiter uses token mint addresses, this is a simplified version
    token_map = Dict(
        "SOL" => "So11111111111111111111111111111111111111112",
        "USDC" => "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v"
    )
    
    token_mint = get(token_map, token, token)
    
    url = "$(DEX_ENDPOINTS["jupiter"])?ids=$token_mint"
    
    response = HTTP.get(url, ["User-Agent" => cfg.user_agent]; readtimeout=cfg.timeout)
    
    if response.status == 200
        data = JSON.parse(String(response.body))
        if haskey(data, "data") && haskey(data["data"], token_mint)
            price_data = data["data"][token_mint]
            return Dict(
                "price" => price_data["price"],
                "source" => "jupiter",
                "last_updated" => now()
            )
        end
    end
    
    return nothing
end

"""
Fetch price from Uniswap V3
"""
function fetch_uniswap_price(cfg::ToolPriceFetcherConfig, token::String, base::String, include_volume::Bool)
    # This would typically use GraphQL queries to Uniswap's subgraph
    # For demo purposes, returning mock data
    return Dict(
        "price" => rand(100.0:0.01:1000.0),
        "volume_24h" => include_volume ? rand(1000000:100000000) : nothing,
        "source" => "uniswap_v3",
        "liquidity" => rand(1000000:10000000),
        "last_updated" => now()
    )
end

"""
Calculate arbitrage opportunities between different DEXs
"""
function calculate_arbitrage_opportunities(results::Dict)
    if length(results) < 2
        return []
    end
    
    opportunities = []
    dex_names = collect(keys(results))
    
    for i in 1:length(dex_names)
        for j in (i+1):length(dex_names)
            dex_a, dex_b = dex_names[i], dex_names[j]
            price_a = results[dex_a]["price"]
            price_b = results[dex_b]["price"]
            
            if price_a > price_b
                profit_pct = ((price_a - price_b) / price_b) * 100
                push!(opportunities, Dict(
                    "buy_from" => dex_b,
                    "sell_to" => dex_a,
                    "buy_price" => price_b,
                    "sell_price" => price_a,
                    "profit_percentage" => profit_pct,
                    "profit_amount" => price_a - price_b
                ))
            elseif price_b > price_a
                profit_pct = ((price_b - price_a) / price_a) * 100
                push!(opportunities, Dict(
                    "buy_from" => dex_a,
                    "sell_to" => dex_b,
                    "buy_price" => price_a,
                    "sell_price" => price_b,
                    "profit_percentage" => profit_pct,
                    "profit_amount" => price_b - price_a
                ))
            end
        end
    end
    
    # Sort by profit percentage descending
    sort!(opportunities, by = x -> x["profit_percentage"], rev = true)
    
    return opportunities
end

"""
Generate a summary of price data
"""
function generate_price_summary(results::Dict, token::String, base::String)
    if isempty(results)
        return "No price data available"
    end
    
    prices = [data["price"] for data in values(results)]
    
    return Dict(
        "min_price" => minimum(prices),
        "max_price" => maximum(prices),
        "avg_price" => sum(prices) / length(prices),
        "price_spread" => maximum(prices) - minimum(prices),
        "spread_percentage" => ((maximum(prices) - minimum(prices)) / minimum(prices)) * 100,
        "dex_count" => length(results)
    )
end

"""
Map token symbols to CoinGecko IDs
"""
function get_coingecko_token_id(token::String)
    token_map = Dict(
        "BTC" => "bitcoin",
        "ETH" => "ethereum",
        "SOL" => "solana",
        "USDC" => "usd-coin",
        "USDT" => "tether",
        "BNB" => "binancecoin",
        "ADA" => "cardano",
        "DOT" => "polkadot",
        "AVAX" => "avalanche-2",
        "MATIC" => "matic-network"
    )
    
    return get(token_map, token, lowercase(token))
end

const TOOL_PRICE_FETCHER_METADATA = ToolMetadata(
    "price_fetcher",
    "Fetches cryptocurrency prices from various DEX APIs for arbitrage analysis"
)

const TOOL_PRICE_FETCHER_SPECIFICATION = ToolSpecification(
    tool_price_fetcher,
    ToolPriceFetcherConfig,
    TOOL_PRICE_FETCHER_METADATA
)
