using DotEnv
DotEnv.load!()

using ...Resources: Groq
using ..CommonTypes: ToolSpecification, ToolMetadata, ToolConfig

GROQ_API_KEY = ENV["GROQ_API_KEY"]
GROQ_MODEL = "llama-3.3-70b-versatile"  # Latest Llama model on Groq

Base.@kwdef struct ToolGroqAgentConfig <: ToolConfig
    api_key::String = GROQ_API_KEY
    model_name::String = GROQ_MODEL
    temperature::Float64 = 0.7
    max_tokens::Int = 2048
    top_p::Float64 = 1.0
    frequency_penalty::Float64 = 0.0
    presence_penalty::Float64 = 0.0
end

const ALLOWED_TASKS = Set([
    "chat", "code_generation", "analysis", "creative_writing", 
    "problem_solving", "explanation", "translation", "summarization"
])
const GROQ_MAX_ATTEMPTS = 3

"""
    tool_groq_agent(cfg::ToolGroqAgentConfig, task::Dict) -> Dict{String, Any}

A comprehensive AI agent powered by Groq's fast inference API that can handle various tasks
including chat, code generation, analysis, creative writing, and more.

# Arguments
- `cfg::ToolGroqAgentConfig`: Tool configuration with Groq API settings.
- `task::Dict`: A dictionary with task instructions.
    - Required keys:
        - "prompt": The main instruction or question for the AI agent.
        - "task_type": Type of task. One of: "chat", "code_generation", "analysis", 
                      "creative_writing", "problem_solving", "explanation", "translation", "summarization".
    - Optional keys:
        - "context": Additional context for the task (e.g., previous conversation, code snippets). Default: "".
        - "language": For translation tasks, target language. For code generation, programming language. Default: "".
        - "style": Writing style preference (e.g., "formal", "casual", "technical"). Default: "neutral".
        - "max_length": Maximum desired length of response. Default: unlimited.

# Returns
A dictionary with the execution result containing the AI agent's response.
"""
function tool_groq_agent(cfg::ToolGroqAgentConfig, task::Dict)
    # Validate required fields
    if !haskey(task, "prompt") || !(task["prompt"] isa AbstractString)
        return Dict("success" => false, "error" => "Missing or invalid 'prompt'")
    end
    
    if !haskey(task, "task_type") || !(task["task_type"] isa AbstractString)
        return Dict("success" => false, "error" => "Missing or invalid 'task_type'")
    end
    
    task_type = lowercase(task["task_type"])
    if task_type ∉ ALLOWED_TASKS
        return Dict("success" => false, "error" => "Invalid 'task_type'. Allowed types: $(join(ALLOWED_TASKS, ", "))")
    end

    # Extract task parameters
    prompt = task["prompt"]
    context = get(task, "context", "")
    language = get(task, "language", "")
    style = get(task, "style", "neutral")
    max_length = get(task, "max_length", nothing)

    # Build system prompt based on task type
    system_prompt = build_system_prompt(task_type, style, language, max_length)
    
    # Construct the full prompt with context
    full_prompt = construct_full_prompt(system_prompt, prompt, context)

    # Configure Groq client
    groq_cfg = Groq.GroqConfig(
        api_key = cfg.api_key,
        model_name = cfg.model_name,
        temperature = cfg.temperature,
        max_tokens = cfg.max_tokens,
        top_p = cfg.top_p,
        frequency_penalty = cfg.frequency_penalty,
        presence_penalty = cfg.presence_penalty
    )

    # Execute the request with retry logic
    for attempt in 1:GROQ_MAX_ATTEMPTS
        try
            response = Groq.groq_util(groq_cfg, full_prompt)
            
            # Post-process response if needed
            processed_response = post_process_response(response, task_type, max_length)
            
            return Dict(
                "success" => true,
                "output" => processed_response,
                "task_type" => task_type,
                "model_used" => cfg.model_name,
                "attempt" => attempt
            )
            
        catch e
            error_msg = string(e)
            if attempt == GROQ_MAX_ATTEMPTS
                return Dict(
                    "success" => false, 
                    "error" => "Failed after $GROQ_MAX_ATTEMPTS attempts. Last error: $error_msg"
                )
            end
            # Wait a bit before retrying
            sleep(1)
        end
    end
end

"""
Build system prompt based on task type and parameters.
"""
function build_system_prompt(task_type::String, style::String, language::String, max_length)
    base_prompt = "You are a helpful AI assistant powered by Groq's fast inference. "
    
    task_specific = if task_type == "chat"
        "Engage in natural conversation. Be helpful, informative, and engaging."
    elseif task_type == "code_generation"
        lang_spec = isempty(language) ? "" : " Focus on $language programming language."
        "Generate clean, well-documented, and efficient code.$lang_spec Explain your approach when helpful."
    elseif task_type == "analysis"
        "Provide thorough analysis with clear reasoning. Break down complex topics into understandable parts."
    elseif task_type == "creative_writing"
        "Create engaging, original content. Use vivid descriptions and maintain narrative flow."
    elseif task_type == "problem_solving"
        "Think step-by-step to solve problems. Show your reasoning process and provide clear solutions."
    elseif task_type == "explanation"
        "Explain concepts clearly and comprehensively. Use examples and analogies when helpful."
    elseif task_type == "translation"
        target_lang = isempty(language) ? "the target language" : language
        "Provide accurate translations to $target_lang. Maintain the original meaning and tone."
    elseif task_type == "summarization"
        "Create concise, accurate summaries that capture the key points and main ideas."
    else
        "Assist with the requested task to the best of your abilities."
    end
    
    style_instruction = if style != "neutral"
        " Use a $style tone and writing style."
    else
        ""
    end
    
    length_instruction = if max_length !== nothing
        " Keep your response under $max_length characters when possible."
    else
        ""
    end
    
    return base_prompt * task_specific * style_instruction * length_instruction
end

"""
Construct the full prompt with system instructions, context, and user prompt.
"""
function construct_full_prompt(system_prompt::String, user_prompt::String, context::String)
    if isempty(context)
        return "$system_prompt\n\nUser Request: $user_prompt"
    else
        return "$system_prompt\n\nContext: $context\n\nUser Request: $user_prompt"
    end
end

"""
Post-process the response based on task type and requirements.
"""
function post_process_response(response::String, task_type::String, max_length)
    # Trim whitespace
    processed = strip(response)
    
    # Apply length limit if specified
    if max_length !== nothing && length(processed) > max_length
        processed = processed[1:max_length] * "..."
    end
    
    return processed
end

const TOOL_GROQ_AGENT_METADATA = ToolMetadata(
    "groq_agent",
    "A comprehensive AI agent powered by Groq's fast inference API for various tasks including chat, code generation, analysis, and creative writing."
)

const TOOL_GROQ_AGENT_SPECIFICATION = ToolSpecification(
    tool_groq_agent,
    ToolGroqAgentConfig,
    TOOL_GROQ_AGENT_METADATA
)
