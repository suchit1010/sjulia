module Groq

using HTTP
using JSON

export GroqConfig, groq_util

@kwdef struct GroqConfig
    api_key::String
    model_name::String = "llama-3.3-70b-versatile"  # Default to latest Llama model
    temperature::Float64 = 0.7
    max_tokens::Int = 1024
    top_p::Float64 = 1.0
    frequency_penalty::Float64 = 0.0
    presence_penalty::Float64 = 0.0
end

"""
    groq_util(cfg::GroqConfig, prompt::String) :: String

Sends prompt to Groq's API and returns its text completion.
"""
function groq_util(
    cfg::GroqConfig,
    prompt::String
)::String
    endpoint_url = "https://api.groq.com/openai/v1/chat/completions"

    body_dict = Dict(
        "model" => cfg.model_name,
        "messages" => [
            Dict("role" => "user", "content" => prompt)
        ],
        "temperature" => cfg.temperature,
        "max_tokens" => cfg.max_tokens,
        "top_p" => cfg.top_p,
        "frequency_penalty" => cfg.frequency_penalty,
        "presence_penalty" => cfg.presence_penalty,
        "stream" => false
    )
    request_body = JSON.json(body_dict)

    resp = HTTP.request(
        "POST",
        endpoint_url;
        headers = [
            "Content-Type" => "application/json",
            "Authorization" => "Bearer $(cfg.api_key)"
        ],
        body = request_body
    )

    if resp.status != 200
        error("Groq API request failed with status $(resp.status): $(String(resp.body))")
    end

    resp_json = JSON.parse(String(resp.body))

    if !haskey(resp_json, "choices") || isempty(resp_json["choices"])
        error("Groq response missing 'choices' or the list is empty.")
    end

    first_choice = resp_json["choices"][1]
    
    if !haskey(first_choice, "message") ||
       !haskey(first_choice["message"], "content")
        error("Groq response's first choice missing 'message.content'.")
    end

    generated_text = first_choice["message"]["content"]
    return generated_text
end

end
