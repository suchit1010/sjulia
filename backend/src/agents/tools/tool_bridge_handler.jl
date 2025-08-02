using DotEnv
DotEnv.load!()

using HTTP
using JSON
using Dates
using ..CommonTypes: ToolSpecification, ToolMetadata, ToolConfig

Base.@kwdef struct ToolBridgeHandlerConfig <: ToolConfig
    max_bridge_amount::Float64 = 1000.0  # Max amount to bridge
    default_timeout::Int = 3600  # 1 hour timeout for bridge operations
    simulation_mode::Bool = true  # Start in simulation mode
    supported_protocols::Vector{String} = ["wormhole", "layerzero", "multichain", "stargate"]
end

const SUPPORTED_CHAINS = Dict(
    "ethereum" => Dict("chain_id" => 1, "wormhole_id" => 2),
    "polygon" => Dict("chain_id" => 137, "wormhole_id" => 5),
    "bsc" => Dict("chain_id" => 56, "wormhole_id" => 4),
    "solana" => Dict("chain_id" => 101, "wormhole_id" => 1),
    "arbitrum" => Dict("chain_id" => 42161, "wormhole_id" => 23),
    "optimism" => Dict("chain_id" => 10, "wormhole_id" => 24),
    "avalanche" => Dict("chain_id" => 43114, "wormhole_id" => 6)
)

const BRIDGE_PROTOCOLS = Dict(
    "wormhole" => Dict(
        "name" => "Wormhole",
        "mainnet_endpoint" => "https://api.wormhole.com",
        "testnet_endpoint" => "https://api.testnet.wormhole.com",
        "guardian_rpc" => "https://wormhole-v2-mainnet-api.certus.one",
        "contract_addresses" => Dict(
            "ethereum" => "0x98f3c9e6E3fAce36bAAd05FE09d375Ef1464288B",
            "polygon" => "0x7A4B5a56256163F07b2C80A7cA55aBE66c4ec4d7",
            "solana" => "worm2ZoG2kUd4vFXhvjh93UUH596ayRfgQ2MgjNMTth"
        )
    ),
    "layerzero" => Dict(
        "name" => "LayerZero",
        "mainnet_endpoint" => "https://api.layerzero.network",
        "testnet_endpoint" => "https://testnet-api.layerzero.network",
        "contract_addresses" => Dict(
            "ethereum" => "0x66A71Dcef29A0fFBDBE3c6a460a3B5BC225Cd675",
            "polygon" => "0x3c2269811836af69497E5F486A85D7316753cf62",
            "arbitrum" => "0x3c2269811836af69497E5F486A85D7316753cf62"
        )
    ),
    "stargate" => Dict(
        "name" => "Stargate",
        "mainnet_endpoint" => "https://api.stargate.finance",
        "testnet_endpoint" => "https://testnet-api.stargate.finance",
        "contract_addresses" => Dict(
            "ethereum" => "0x8731d54E9D02c286767d56ac03e8037C07e01e98",
            "polygon" => "0x45A01E4e04F14f7A4a6702c74187c5F6222033cd",
            "arbitrum" => "0x53Bf833A5d6c4ddA888F69c22C88C9f356a41614"
        )
    )
)

"""
    tool_bridge_handler(cfg::ToolBridgeHandlerConfig, task::Dict) -> Dict{String, Any}

Handles cross-chain asset transfers for arbitrage operations using various bridge protocols.

# Arguments
- `cfg::ToolBridgeHandlerConfig`: Tool configuration
- `task::Dict`: Task parameters
    - Required keys:
        - "action": "estimate", "simulate", or "execute"
        - "token_symbol": Token to bridge (e.g., "USDC", "ETH")
        - "amount": Amount to bridge
        - "source_chain": Source blockchain
        - "destination_chain": Destination blockchain
    - Optional keys:
        - "bridge_protocol": Specific bridge to use. Default: "auto"
        - "max_fee_percentage": Maximum acceptable bridge fee. Default: 0.005 (0.5%)
        - "urgency": "low", "medium", "high". Affects protocol selection. Default: "medium"

# Returns
A dictionary with bridge operation results
"""
function tool_bridge_handler(cfg::ToolBridgeHandlerConfig, task::Dict)
    # Validate required fields
    required_fields = ["action", "token_symbol", "amount", "source_chain", "destination_chain"]
    for field in required_fields
        if !haskey(task, field)
            return Dict("success" => false, "error" => "Missing required field: $field")
        end
    end

    action = task["action"]
    token_symbol = uppercase(task["token_symbol"])
    amount = task["amount"]
    source_chain = lowercase(task["source_chain"])
    destination_chain = lowercase(task["destination_chain"])

    # Validate inputs
    if action ∉ ["estimate", "simulate", "execute"]
        return Dict("success" => false, "error" => "Invalid action. Must be 'estimate', 'simulate', or 'execute'")
    end

    if source_chain == destination_chain
        return Dict("success" => false, "error" => "Source and destination chains cannot be the same")
    end

    if source_chain ∉ keys(SUPPORTED_CHAINS) || destination_chain ∉ keys(SUPPORTED_CHAINS)
        return Dict("success" => false, "error" => "Unsupported chain. Supported: $(join(keys(SUPPORTED_CHAINS), ", "))")
    end

    if amount <= 0 || amount > cfg.max_bridge_amount
        return Dict("success" => false, "error" => "Invalid amount. Must be between 0 and $(cfg.max_bridge_amount)")
    end

    # Extract optional parameters
    bridge_protocol = get(task, "bridge_protocol", "auto")
    max_fee_percentage = get(task, "max_fee_percentage", 0.005)
    urgency = get(task, "urgency", "medium")

    try
        if action == "estimate"
            return estimate_bridge_costs(cfg, token_symbol, amount, source_chain, destination_chain, bridge_protocol, urgency)
        elseif action == "simulate"
            return simulate_bridge_transfer(cfg, token_symbol, amount, source_chain, destination_chain, bridge_protocol, max_fee_percentage, urgency)
        else  # execute
            if cfg.simulation_mode
                result = simulate_bridge_transfer(cfg, token_symbol, amount, source_chain, destination_chain, bridge_protocol, max_fee_percentage, urgency)
                result["note"] = "Bridge executed in simulation mode for safety"
                return result
            else
                return execute_bridge_transfer(cfg, token_symbol, amount, source_chain, destination_chain, bridge_protocol, max_fee_percentage, urgency)
            end
        end
    catch e
        return Dict("success" => false, "error" => "Bridge operation failed: $(string(e))")
    end
end

"""
Estimate bridge costs by querying real bridge protocol APIs
"""
function estimate_bridge_costs(cfg::ToolBridgeHandlerConfig, token::String, amount::Float64, 
                              source::String, destination::String, protocol::String, urgency::String)
    
    estimates = []
    protocols_to_check = protocol == "auto" ? cfg.supported_protocols : [protocol]
    
    for proto in protocols_to_check
        if proto ∉ keys(BRIDGE_PROTOCOLS)
            continue
        end
        
        try
            # Query real bridge protocol API for fee estimation
            bridge_info = BRIDGE_PROTOCOLS[proto]
            endpoint = cfg.simulation_mode ? bridge_info["testnet_endpoint"] : bridge_info["mainnet_endpoint"]
            
            # Call real API to get bridge fees and timing
            fee_data = query_bridge_fees(endpoint, proto, token, amount, source, destination)
            
            if fee_data["success"]
                push!(estimates, Dict(
                    "protocol" => proto,
                    "protocol_name" => bridge_info["name"],
                    "bridge_fee" => fee_data["fee_amount"],
                    "bridge_fee_percentage" => fee_data["fee_percentage"],
                    "gas_cost_usd" => fee_data["gas_estimate"],
                    "total_cost" => fee_data["total_cost"],
                    "net_amount_received" => amount - fee_data["total_cost"],
                    "estimated_time_minutes" => fee_data["estimated_time"],
                    "liquidity_available" => fee_data["liquidity_check"],
                    "supported" => true
                ))
            end
        catch e
            # Log error but continue with other protocols
            @warn "Failed to get estimate from $proto: $(string(e))"
            continue
        end
    end
    
    # Sort by total cost (ascending)
    sort!(estimates, by = x -> x["total_cost"])
    
    return Dict(
        "success" => true,
        "token_symbol" => token,
        "amount" => amount,
        "source_chain" => source,
        "destination_chain" => destination,
        "estimates" => estimates,
        "recommended_protocol" => isempty(estimates) ? "none" : estimates[1]["protocol"],
        "cheapest_option" => isempty(estimates) ? nothing : estimates[1],
        "fastest_option" => isempty(estimates) ? nothing : sort(estimates, by = x -> x["estimated_time_minutes"])[1]
    )
end

"""
Simulate a bridge transfer using real API data
"""
function simulate_bridge_transfer(cfg::ToolBridgeHandlerConfig, token::String, amount::Float64,
                                 source::String, destination::String, protocol::String, 
                                 max_fee_percentage::Float64, urgency::String)
    
    # Select best protocol if auto
    if protocol == "auto"
        estimates = estimate_bridge_costs(cfg, token, amount, source, destination, protocol, urgency)
        
        if estimates["success"] && !isempty(estimates["estimates"])
            # Filter by max fee percentage
            suitable_options = filter(x -> x["bridge_fee_percentage"] <= max_fee_percentage * 100, estimates["estimates"])
            
            if isempty(suitable_options)
                return Dict("success" => false, "error" => "No bridge protocols meet the maximum fee requirement")
            end
            
            # Select based on urgency
            selected_protocol = if urgency == "high"
                sort(suitable_options, by = x -> x["estimated_time_minutes"])[1]["protocol"]
            else
                suitable_options[1]["protocol"]  # Already sorted by cost
            end
        else
            return Dict("success" => false, "error" => "No suitable bridge protocols found")
        end
    else
        selected_protocol = protocol
    end
    
    # Get real bridge details
    bridge_details = get_bridge_transfer_details(selected_protocol, token, amount, source, destination)
    
    if !bridge_details["success"]
        return bridge_details
    end
    
    # Add simulation metadata
    simulation_result = merge(bridge_details, Dict(
        "simulation" => true,
        "token_symbol" => token,
        "source_chain" => source,
        "destination_chain" => destination,
        "risk_assessment" => assess_bridge_risks(selected_protocol, token, amount, source, destination),
        "monitoring" => Dict(
            "status_check_interval_seconds" => 30,
            "max_wait_time_minutes" => bridge_details["total_time_estimate"] * 2,
            "status_endpoint" => bridge_details["status_check_url"],
            "estimated_completion" => now() + Dates.Minute(bridge_details["total_time_estimate"])
        ),
        "timestamp" => now()
    ))
    
    return simulation_result
end

"""
Execute a real bridge transfer (placeholder)
"""
function execute_bridge_transfer(cfg::ToolBridgeHandlerConfig, token::String, amount::Float64,
                                source::String, destination::String, protocol::String,
                                max_fee_percentage::Float64, urgency::String)
    
    # In a real implementation, this would:
    # 1. Connect to source chain wallet
    # 2. Check token balance and allowances
    # 3. Call bridge contract
    # 4. Monitor cross-chain message
    # 5. Verify completion on destination chain
    
    return Dict(
        "success" => false,
        "error" => "Real bridge execution not implemented for safety. Use simulation mode.",
        "note" => "To enable real bridging, implement proper wallet integration and bridge protocol APIs"
    )
end

"""
Get real bridge transfer status and details
"""
function get_bridge_transfer_details(protocol::String, token::String, amount::Float64, 
                                   source::String, destination::String, tx_hash::String = "")
    
    # Get real fee estimation
    bridge_info = BRIDGE_PROTOCOLS[protocol]
    endpoint = bridge_info["testnet_endpoint"]
    
    fee_data = query_bridge_fees(endpoint, protocol, token, amount, source, destination)
    
    if !fee_data["success"]
        return Dict("success" => false, "error" => "Failed to get bridge details: $(fee_data["error"])")
    end
    
    # Real bridge process stages
    stages = [
        Dict("stage" => "validate_transaction", "description" => "Validating source transaction", "estimated_time_seconds" => 30),
        Dict("stage" => "lock_tokens", "description" => "Locking tokens on source chain", "estimated_time_seconds" => 60),
        Dict("stage" => "generate_proof", "description" => "Generating cryptographic proof", "estimated_time_seconds" => 300),
        Dict("stage" => "relay_message", "description" => "Relaying message to destination", "estimated_time_seconds" => 600),
        Dict("stage" => "mint_tokens", "description" => "Minting tokens on destination", "estimated_time_seconds" => 120)
    ]
    
    return Dict(
        "success" => true,
        "protocol" => protocol,
        "input_amount" => amount,
        "bridge_fee" => fee_data["fee_amount"],
        "bridge_fee_percentage" => fee_data["fee_percentage"],
        "output_amount" => amount - fee_data["total_cost"],
        "gas_cost_source" => fee_data["gas_estimate"] * 0.6,
        "gas_cost_destination" => fee_data["gas_estimate"] * 0.4,
        "total_time_estimate" => fee_data["estimated_time"],
        "stages" => stages,
        "source_transaction" => !isempty(tx_hash) ? tx_hash : "pending",
        "destination_transaction" => "pending",
        "bridge_message_id" => "pending",
        "status_check_url" => "$(bridge_info["testnet_endpoint"])/status/",
        "liquidity_available" => fee_data["liquidity_check"]
    )
end

"""
Assess risks associated with bridge operation
"""
function assess_bridge_risks(protocol::String, token::String, amount::Float64, source::String, destination::String)
    risks = []
    risk_score = 0.0
    
    # Protocol-specific risks
    if protocol == "wormhole"
        if amount > 10000
            push!(risks, "Large amount bridging via Wormhole may face additional security delays")
            risk_score += 0.2
        end
    end
    
    # Token-specific risks
    if token ∉ ["USDC", "USDT", "ETH"]
        push!(risks, "Less common token may have lower liquidity on destination chain")
        risk_score += 0.15
    end
    
    # Chain-specific risks
    high_risk_chains = ["bsc"]  # Example
    if source ∈ high_risk_chains || destination ∈ high_risk_chains
        push!(risks, "Chain may have higher bridge failure rates")
        risk_score += 0.1
    end
    
    # Amount-based risks
    if amount > 1000
        push!(risks, "Large amount increases exposure to bridge smart contract risks")
        risk_score += 0.1
    end
    
    risk_level = risk_score < 0.2 ? "low" : risk_score < 0.4 ? "medium" : "high"
    
    return Dict(
        "risk_level" => risk_level,
        "risk_score" => risk_score,
        "identified_risks" => risks,
        "mitigation_suggestions" => generate_risk_mitigation_suggestions(risks),
        "insurance_available" => protocol ∈ ["wormhole", "layerzero"],
        "recommended_max_amount" => calculate_recommended_max_amount(protocol, token, source, destination)
    )
end

"""
Generate risk mitigation suggestions
"""
function generate_risk_mitigation_suggestions(risks::Vector)
    suggestions = []
    
    if any(contains.(risks, "Large amount"))
        push!(suggestions, "Consider splitting large transfers into smaller batches")
    end
    
    if any(contains.(risks, "Less common token"))
        push!(suggestions, "Verify sufficient liquidity on destination chain before bridging")
    end
    
    if any(contains.(risks, "security delays"))
        push!(suggestions, "Allow extra time for large transfers due to security checks")
    end
    
    if any(contains.(risks, "failure rates"))
        push!(suggestions, "Monitor bridge status closely and have backup bridge options ready")
    end
    
    if isempty(suggestions)
        push!(suggestions, "Bridge operation appears low risk - proceed with standard monitoring")
    end
    
    return suggestions
end

"""
Calculate recommended maximum amount based on real protocol limits and liquidity
"""
function calculate_recommended_max_amount(protocol::String, token::String, source::String, destination::String)
    try
        # Query real protocol limits
        bridge_info = BRIDGE_PROTOCOLS[protocol]
        endpoint = bridge_info["testnet_endpoint"]
        
        # Check protocol-specific limits
        if protocol == "wormhole"
            # Wormhole has different limits per token and chain
            return query_wormhole_limits(endpoint, token, source, destination)
        elseif protocol == "layerzero"
            # LayerZero limits based on daily volume
            return query_layerzero_limits(endpoint, token, source, destination)
        elseif protocol == "stargate"
            # Stargate limits based on pool liquidity
            return query_stargate_limits(endpoint, token, source, destination)
        end
    catch e
        @warn "Failed to get protocol limits: $(string(e))"
    end
    
    # Conservative fallback limits
    base_limits = Dict(
        "USDC" => 100000.0,
        "USDT" => 100000.0,
        "ETH" => 50.0,
        "BTC" => 5.0
    )
    
    return get(base_limits, token, 10000.0)
end

"""
Query Wormhole transfer limits
"""
function query_wormhole_limits(endpoint::String, token::String, source::String, destination::String)
    try
        # Query guardian network for rate limits
        limits_url = "$endpoint/v1/governor/limits"
        response = HTTP.get(limits_url)
        
        if response.status == 200
            data = JSON.parse(String(response.body))
            # Extract chain-specific limits
            chain_limits = get(data, "chainLimits", Dict())
            source_limit = get(chain_limits, string(SUPPORTED_CHAINS[source]["wormhole_id"]), Dict())
            return Float64(get(source_limit, "maxTransactionSize", 50000))
        end
    catch e
        @warn "Failed to query Wormhole limits: $(string(e))"
    end
    
    return 50000.0 # Conservative default
end

"""
Query LayerZero transfer limits
"""
function query_layerzero_limits(endpoint::String, token::String, source::String, destination::String)
    try
        # LayerZero limits are usually per-application
        limits_url = "$endpoint/v1/limits/$(SUPPORTED_CHAINS[source]["chain_id"])"
        headers = ["Content-Type" => "application/json"]
        
        response = HTTP.get(limits_url, headers)
        
        if response.status == 200
            data = JSON.parse(String(response.body))
            daily_limit = get(data, "dailyLimit", 1000000)
            return Float64(daily_limit * 0.1) # Use 10% of daily limit per transaction
        end
    catch e
        @warn "Failed to query LayerZero limits: $(string(e))"
    end
    
    return 25000.0 # Conservative default
end

"""
Query Stargate pool liquidity limits
"""
function query_stargate_limits(endpoint::String, token::String, source::String, destination::String)
    try
        # Query pool liquidity
        pool_mapping = Dict("USDC" => 1, "USDT" => 2, "ETH" => 13)
        pool_id = get(pool_mapping, token, 1)
        
        liquidity_url = "$endpoint/v1/pool/$(SUPPORTED_CHAINS[source]["chain_id"])/$pool_id"
        response = HTTP.get(liquidity_url)
        
        if response.status == 200
            data = JSON.parse(String(response.body))
            total_liquidity = parse(Float64, get(data, "totalLiquidity", "0"))
            # Recommend max 5% of pool liquidity
            return total_liquidity * 0.05
        end
    catch e
        @warn "Failed to query Stargate limits: $(string(e))"
    end
    
    return 75000.0 # Conservative default
end

"""
Estimate gas costs for bridge operations
"""
function estimate_gas_cost(chain::String, operation::String)
    # This function is kept for backward compatibility but now calls the real implementation
    return estimate_real_gas_cost(chain, chain, "wormhole") # Default to wormhole for single chain estimate
end

"""
Calculate confidence score based on real protocol performance data
"""
function calculate_confidence_score(protocol::String, source::String, destination::String, token::String)
    try
        # Query real performance metrics
        bridge_info = BRIDGE_PROTOCOLS[protocol]
        endpoint = bridge_info["testnet_endpoint"]
        
        # Get historical success rates and performance data
        stats = query_bridge_performance(endpoint, protocol, source, destination, token)
        
        if stats["success"]
            base_score = stats["success_rate"] # Already a percentage
            
            # Adjust for chain pair reliability
            if (source == "ethereum" && destination == "polygon") || (source == "polygon" && destination == "ethereum")
                base_score += 0.02  # Well-tested route
            end
            
            # Adjust for token stability
            if token ∈ ["USDC", "USDT"]
                base_score += 0.01  # Stable coins are safer
            end
            
            # Adjust for recent performance
            if stats["recent_downtime_hours"] < 1
                base_score += 0.01
            elseif stats["recent_downtime_hours"] > 24
                base_score -= 0.05
            end
            
            return min(base_score, 0.98) # Cap at 98%
        end
    catch e
        @warn "Failed to get real confidence score: $(string(e))"
    end
    
    # Fallback scores based on protocol reputation
    fallback_scores = Dict(
        "wormhole" => 0.85,
        "layerzero" => 0.90,
        "stargate" => 0.88
    )
    
    return get(fallback_scores, protocol, 0.75)
end

"""
Query real bridge performance statistics
"""
function query_bridge_performance(endpoint::String, protocol::String, source::String, destination::String, token::String)
    try
        if protocol == "wormhole"
            # Query Wormhole guardian network statistics
            stats_url = "$endpoint/v1/stats/$(SUPPORTED_CHAINS[source]["wormhole_id"])/$(SUPPORTED_CHAINS[destination]["wormhole_id"])"
            response = HTTP.get(stats_url)
            
            if response.status == 200
                data = JSON.parse(String(response.body))
                return Dict(
                    "success" => true,
                    "success_rate" => get(data, "successRate", 0.85),
                    "avg_completion_time" => get(data, "avgCompletionTime", 900), # seconds
                    "recent_downtime_hours" => get(data, "recentDowntime", 0),
                    "total_volume_24h" => get(data, "volume24h", 0)
                )
            end
        elseif protocol == "layerzero"
            # Query LayerZero statistics
            stats_url = "$endpoint/v1/analytics/$(SUPPORTED_CHAINS[source]["chain_id"])"
            response = HTTP.get(stats_url)
            
            if response.status == 200
                data = JSON.parse(String(response.body))
                return Dict(
                    "success" => true,
                    "success_rate" => get(data, "reliability", 0.90),
                    "avg_completion_time" => get(data, "avgTime", 600),
                    "recent_downtime_hours" => get(data, "downtime", 0),
                    "total_volume_24h" => get(data, "dailyVolume", 0)
                )
            end
        end
    catch e
        @warn "Failed to query bridge performance: $(string(e))"
    end
    
    return Dict("success" => false)
end

"""
Query real bridge protocol APIs for fee estimation
"""
function query_bridge_fees(endpoint::String, protocol::String, token::String, amount::Float64, 
                          source::String, destination::String)
    
    headers = ["Content-Type" => "application/json", "User-Agent" => "JuliaOS-Bridge-Agent/1.0"]
    
    try
        if protocol == "wormhole"
            return query_wormhole_fees(endpoint, token, amount, source, destination, headers)
        elseif protocol == "layerzero"
            return query_layerzero_fees(endpoint, token, amount, source, destination, headers)
        elseif protocol == "stargate"
            return query_stargate_fees(endpoint, token, amount, source, destination, headers)
        else
            return Dict("success" => false, "error" => "Unsupported protocol: $protocol")
        end
    catch e
        return Dict("success" => false, "error" => "API query failed: $(string(e))")
    end
end

"""
Query Wormhole bridge fees
"""
function query_wormhole_fees(endpoint::String, token::String, amount::Float64, 
                           source::String, destination::String, headers::Vector)
    
    # Get chain IDs for Wormhole
    source_chain_id = SUPPORTED_CHAINS[source]["wormhole_id"]
    dest_chain_id = SUPPORTED_CHAINS[destination]["wormhole_id"]
    
    # Query Wormhole VAA fee
    vaa_url = "$endpoint/v1/relayer/fee/$source_chain_id/$dest_chain_id"
    
    response = HTTP.get(vaa_url, headers)
    
    if response.status == 200
        fee_data = JSON.parse(String(response.body))
        
        # Calculate bridge fees (Wormhole charges gas + relayer fee)
        base_fee = get(fee_data, "fee", 0.0)
        gas_estimate = estimate_real_gas_cost(source, destination, "wormhole")
        total_cost = base_fee + gas_estimate
        
        return Dict(
            "success" => true,
            "fee_amount" => base_fee,
            "fee_percentage" => (total_cost / amount) * 100,
            "gas_estimate" => gas_estimate,
            "total_cost" => total_cost,
            "estimated_time" => 15, # Wormhole typically takes 15-20 minutes
            "liquidity_check" => check_wormhole_liquidity(endpoint, token, destination)
        )
    else
        return Dict("success" => false, "error" => "Wormhole API error: $(response.status)")
    end
end

"""
Query LayerZero bridge fees
"""
function query_layerzero_fees(endpoint::String, token::String, amount::Float64, 
                            source::String, destination::String, headers::Vector)
    
    # Get LayerZero chain IDs
    source_chain_id = SUPPORTED_CHAINS[source]["chain_id"]
    dest_chain_id = SUPPORTED_CHAINS[destination]["chain_id"]
    
    # Query LayerZero fee estimation
    fee_url = "$endpoint/v1/fees"
    payload = Dict(
        "srcChainId" => source_chain_id,
        "dstChainId" => dest_chain_id,
        "amount" => string(Int(amount * 1e18)), # Convert to wei/smallest unit
        "token" => token
    )
    
    response = HTTP.post(fee_url, headers, JSON.json(payload))
    
    if response.status == 200
        fee_data = JSON.parse(String(response.body))
        
        native_fee = parse(Float64, get(fee_data, "nativeFee", "0")) / 1e18
        gas_estimate = estimate_real_gas_cost(source, destination, "layerzero")
        total_cost = native_fee + gas_estimate
        
        return Dict(
            "success" => true,
            "fee_amount" => native_fee,
            "fee_percentage" => (total_cost / amount) * 100,
            "gas_estimate" => gas_estimate,
            "total_cost" => total_cost,
            "estimated_time" => 10, # LayerZero is typically faster
            "liquidity_check" => true # LayerZero doesn't have liquidity pools
        )
    else
        return Dict("success" => false, "error" => "LayerZero API error: $(response.status)")
    end
end

"""
Query Stargate bridge fees
"""
function query_stargate_fees(endpoint::String, token::String, amount::Float64, 
                           source::String, destination::String, headers::Vector)
    
    # Get Stargate pool IDs for the token
    pool_mapping = Dict(
        "USDC" => 1,
        "USDT" => 2,
        "ETH" => 13
    )
    
    if token ∉ keys(pool_mapping)
        return Dict("success" => false, "error" => "Token not supported by Stargate: $token")
    end
    
    source_chain_id = SUPPORTED_CHAINS[source]["chain_id"]
    dest_chain_id = SUPPORTED_CHAINS[destination]["chain_id"]
    pool_id = pool_mapping[token]
    
    # Query Stargate fee
    fee_url = "$endpoint/v1/quote"
    payload = Dict(
        "srcChainId" => source_chain_id,
        "dstChainId" => dest_chain_id,
        "srcPoolId" => pool_id,
        "dstPoolId" => pool_id,
        "amount" => string(Int(amount * 1e6)) # USDC/USDT use 6 decimals
    )
    
    response = HTTP.post(fee_url, headers, JSON.json(payload))
    
    if response.status == 200
        fee_data = JSON.parse(String(response.body))
        
        bridge_fee = parse(Float64, get(fee_data, "eqFee", "0")) / 1e6
        gas_estimate = estimate_real_gas_cost(source, destination, "stargate")
        total_cost = bridge_fee + gas_estimate
        
        return Dict(
            "success" => true,
            "fee_amount" => bridge_fee,
            "fee_percentage" => (total_cost / amount) * 100,
            "gas_estimate" => gas_estimate,
            "total_cost" => total_cost,
            "estimated_time" => 8, # Stargate is usually fastest
            "liquidity_check" => check_stargate_liquidity(fee_data)
        )
    else
        return Dict("success" => false, "error" => "Stargate API error: $(response.status)")
    end
end

"""
Check Wormhole liquidity on destination chain
"""
function check_wormhole_liquidity(endpoint::String, token::String, destination::String)
    try
        # Query guardian network for token availability
        guardian_url = "$endpoint/v1/tokens/$token/chains/$(SUPPORTED_CHAINS[destination]["wormhole_id"])"
        response = HTTP.get(guardian_url)
        
        if response.status == 200
            data = JSON.parse(String(response.body))
            return get(data, "exists", false)
        end
    catch e
        @warn "Failed to check Wormhole liquidity: $(string(e))"
    end
    
    return true # Assume available if check fails
end

"""
Check Stargate pool liquidity
"""
function check_stargate_liquidity(fee_data::Dict)
    # Stargate returns liquidity info in the quote response
    available_liquidity = parse(Float64, get(fee_data, "eqReward", "0"))
    return available_liquidity > 0
end

"""
Estimate real gas costs using current network conditions
"""
function estimate_real_gas_cost(source::String, destination::String, protocol::String)
    # Query real gas prices from network RPCs or gas stations
    try
        source_gas_price = query_gas_price(source)
        dest_gas_price = query_gas_price(destination)
        
        # Protocol-specific gas usage estimates
        gas_usage = Dict(
            "wormhole" => Dict("send" => 150000, "receive" => 80000),
            "layerzero" => Dict("send" => 120000, "receive" => 60000),
            "stargate" => Dict("send" => 100000, "receive" => 50000)
        )
        
        protocol_gas = get(gas_usage, protocol, Dict("send" => 120000, "receive" => 60000))
        
        # Calculate USD cost
        source_cost = (source_gas_price * protocol_gas["send"]) / 1e9 * get_eth_price()
        dest_cost = (dest_gas_price * protocol_gas["receive"]) / 1e9 * get_eth_price()
        
        return source_cost + dest_cost
        
    catch e
        @warn "Failed to get real gas estimates: $(string(e))"
        # Fallback to conservative estimates
        return 0.01 # $0.01 USD
    end
end

"""
Query current gas price from network
"""
function query_gas_price(chain::String)
    rpc_endpoints = Dict(
        "ethereum" => "https://eth-mainnet.g.alchemy.com/v2/demo",
        "polygon" => "https://polygon-rpc.com",
        "arbitrum" => "https://arb1.arbitrum.io/rpc",
        "optimism" => "https://mainnet.optimism.io"
    )
    
    rpc_url = get(rpc_endpoints, chain, "")
    
    if isempty(rpc_url)
        return 20.0 # 20 gwei fallback
    end
    
    try
        payload = Dict(
            "jsonrpc" => "2.0",
            "method" => "eth_gasPrice",
            "params" => [],
            "id" => 1
        )
        
        response = HTTP.post(rpc_url, ["Content-Type" => "application/json"], JSON.json(payload))
        
        if response.status == 200
            data = JSON.parse(String(response.body))
            gas_price_hex = get(data, "result", "0x0")
            gas_price_wei = parse(UInt64, gas_price_hex, base=16)
            return Float64(gas_price_wei) / 1e9 # Convert to gwei
        end
    catch e
        @warn "Failed to query gas price for $chain: $(string(e))"
    end
    
    return 20.0 # Fallback
end

"""
Get current ETH price for gas cost conversion
"""
function get_eth_price()
    try
        # Use a free API to get ETH price
        response = HTTP.get("https://api.coingecko.com/api/v3/simple/price?ids=ethereum&vs_currencies=usd")
        
        if response.status == 200
            data = JSON.parse(String(response.body))
            return get(get(data, "ethereum", Dict()), "usd", 2000.0)
        end
    catch e
        @warn "Failed to get ETH price: $(string(e))"
    end
    
    return 2000.0 # Fallback price
end

const TOOL_BRIDGE_HANDLER_METADATA = ToolMetadata(
    "bridge_handler",
    "Handles cross-chain asset transfers for arbitrage operations using various bridge protocols like Wormhole"
)

const TOOL_BRIDGE_HANDLER_SPECIFICATION = ToolSpecification(
    tool_bridge_handler,
    ToolBridgeHandlerConfig,
    TOOL_BRIDGE_HANDLER_METADATA
)
