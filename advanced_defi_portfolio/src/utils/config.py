"""
Configuration Management for Advanced DeFi Portfolio Manager

Handles environment variables, API keys, and system configuration.
"""

import os
from typing import Dict, Any, Optional
from dataclasses import dataclass, field
from dotenv import load_dotenv
from pathlib import Path


@dataclass
class JuliaOSConfig:
    """JuliaOS backend configuration."""
    host: str = "http://127.0.0.1:8052/api/v1"
    timeout: int = 30


@dataclass 
class LLMConfig:
    """Large Language Model configuration."""
    api_key: str = ""
    model: str = "gpt-4"
    base_url: str = "https://api.openai.com/v1"
    temperature: float = 0.7
    max_tokens: int = 1024


@dataclass
class BlockchainConfig:
    """Blockchain network configuration."""
    solana_rpc: str = "https://api.devnet.solana.com"
    solana_private_key: str = ""
    ethereum_rpc: str = "https://sepolia.infura.io/v3/YOUR_INFURA_KEY"
    ethereum_private_key: str = ""


@dataclass
class DashboardConfig:
    """Web dashboard configuration."""
    host: str = "0.0.0.0"
    port: int = 5000
    debug: bool = True


@dataclass
class RiskConfig:
    """Risk management configuration."""
    max_trade_size_usd: float = 1000.0
    max_portfolio_risk: float = 0.05
    enable_real_trading: bool = False
    max_slippage: float = 0.02
    min_liquidity_usd: float = 10000.0


@dataclass
class LoggingConfig:
    """Logging system configuration."""
    level: str = "INFO"
    file: str = "logs/portfolio_manager.log"
    enable_metrics: bool = True
    metrics_port: int = 8080


@dataclass
class DEXConfig:
    """Decentralized exchange configuration."""
    uniswap_api_key: str = ""
    jupiter_api_url: str = "https://price.jup.ag/v4"
    sushiswap_api_url: str = "https://api.sushi.com"
    pancakeswap_api_url: str = "https://api.pancakeswap.com"


@dataclass
class PortfolioConfig:
    """Portfolio management configuration."""
    juliaos: JuliaOSConfig = field(default_factory=JuliaOSConfig)
    llm: LLMConfig = field(default_factory=LLMConfig)
    blockchain: BlockchainConfig = field(default_factory=BlockchainConfig)
    dashboard: DashboardConfig = field(default_factory=DashboardConfig)
    risk: RiskConfig = field(default_factory=RiskConfig)
    logging: LoggingConfig = field(default_factory=LoggingConfig)
    dex: DEXConfig = field(default_factory=DEXConfig)
    
    # Agent-specific configurations
    arbitrage_enabled: bool = True
    market_making_enabled: bool = True
    staking_enabled: bool = True
    governance_enabled: bool = True
    gaming_enabled: bool = True
    compliance_enabled: bool = True
    
    # Performance tuning
    price_fetch_interval: int = 30  # seconds
    portfolio_rebalance_interval: int = 300  # seconds
    agent_heartbeat_interval: int = 60  # seconds
    
    # Portfolio targets
    target_assets: Dict[str, float] = field(default_factory=lambda: {
        "SOL": 0.30,
        "ETH": 0.30,
        "USDC": 0.20,
        "BTC": 0.20
    })


class ConfigManager:
    """Configuration manager with environment variable support."""
    
    def __init__(self, env_file: Optional[str] = None):
        """Initialize configuration manager."""
        if env_file:
            load_dotenv(env_file)
        else:
            # Try to load from multiple possible locations
            for env_path in [".env", "../.env", "../../.env"]:
                if Path(env_path).exists():
                    load_dotenv(env_path)
                    break
        
        self.config = self._load_config()
    
    def _load_config(self) -> PortfolioConfig:
        """Load configuration from environment variables."""
        config = PortfolioConfig()
        
        # JuliaOS Configuration
        config.juliaos.host = os.getenv("JULIAOS_HOST", config.juliaos.host)
        config.juliaos.timeout = int(os.getenv("JULIAOS_TIMEOUT", config.juliaos.timeout))
        
        # LLM Configuration
        config.llm.api_key = os.getenv("OPENAI_API_KEY", "")
        config.llm.model = os.getenv("OPENAI_MODEL", config.llm.model)
        config.llm.base_url = os.getenv("OPENAI_BASE_URL", config.llm.base_url)
        
        # Blockchain Configuration
        config.blockchain.solana_rpc = os.getenv("SOLANA_RPC_URL", config.blockchain.solana_rpc)
        config.blockchain.solana_private_key = os.getenv("SOLANA_PRIVATE_KEY", "")
        config.blockchain.ethereum_rpc = os.getenv("ETHEREUM_RPC_URL", config.blockchain.ethereum_rpc)
        config.blockchain.ethereum_private_key = os.getenv("ETHEREUM_PRIVATE_KEY", "")
        
        # Dashboard Configuration
        config.dashboard.host = os.getenv("DASHBOARD_HOST", config.dashboard.host)
        config.dashboard.port = int(os.getenv("DASHBOARD_PORT", config.dashboard.port))
        config.dashboard.debug = os.getenv("DASHBOARD_DEBUG", "true").lower() == "true"
        
        # Risk Configuration
        config.risk.max_trade_size_usd = float(os.getenv("MAX_TRADE_SIZE_USD", config.risk.max_trade_size_usd))
        config.risk.max_portfolio_risk = float(os.getenv("MAX_PORTFOLIO_RISK", config.risk.max_portfolio_risk))
        config.risk.enable_real_trading = os.getenv("ENABLE_REAL_TRADING", "false").lower() == "true"
        
        # Logging Configuration
        config.logging.level = os.getenv("LOG_LEVEL", config.logging.level)
        config.logging.file = os.getenv("LOG_FILE", config.logging.file)
        config.logging.enable_metrics = os.getenv("ENABLE_METRICS", "true").lower() == "true"
        config.logging.metrics_port = int(os.getenv("METRICS_PORT", config.logging.metrics_port))
        
        # DEX Configuration
        config.dex.uniswap_api_key = os.getenv("UNISWAP_API_KEY", "")
        config.dex.jupiter_api_url = os.getenv("JUPITER_API_URL", config.dex.jupiter_api_url)
        
        return config
    
    def get_config(self) -> PortfolioConfig:
        """Get the current configuration."""
        return self.config
    
    def validate_config(self) -> Dict[str, Any]:
        """Validate configuration and return status."""
        issues = []
        warnings = []
        
        # Required API keys
        if not self.config.llm.api_key:
            issues.append("OpenAI API key is required")
            
        # Blockchain keys (warnings if missing)
        if not self.config.blockchain.solana_private_key:
            warnings.append("Solana private key not set - some features will be limited")
            
        if not self.config.blockchain.ethereum_private_key:
            warnings.append("Ethereum private key not set - some features will be limited")
        
        # Risk management validation
        if self.config.risk.max_trade_size_usd <= 0:
            issues.append("Max trade size must be positive")
            
        if self.config.risk.max_portfolio_risk <= 0 or self.config.risk.max_portfolio_risk > 1:
            issues.append("Max portfolio risk must be between 0 and 1")
        
        # Portfolio target validation
        total_allocation = sum(self.config.target_assets.values())
        if abs(total_allocation - 1.0) > 0.01:
            warnings.append(f"Portfolio allocation sums to {total_allocation:.2f}, not 1.0")
        
        return {
            "valid": len(issues) == 0,
            "issues": issues,
            "warnings": warnings,
            "config_summary": {
                "juliaos_host": self.config.juliaos.host,
                "llm_model": self.config.llm.model,
                "real_trading": self.config.risk.enable_real_trading,
                "max_trade_size": self.config.risk.max_trade_size_usd,
                "log_level": self.config.logging.level
            }
        }
    
    def get_agent_config(self, agent_type: str) -> Dict[str, Any]:
        """Get configuration specific to an agent type."""
        base_config = {
            "llm_config": {
                "provider": "openai",
                "api_key": self.config.llm.api_key,
                "api_base": self.config.llm.base_url,
                "model": self.config.llm.model,
                "temperature": self.config.llm.temperature,
                "max_tokens": self.config.llm.max_tokens
            },
            "risk_config": {
                "max_trade_size": self.config.risk.max_trade_size_usd,
                "max_portfolio_risk": self.config.risk.max_portfolio_risk,
                "enable_real_trading": self.config.risk.enable_real_trading
            }
        }
        
        # Agent-specific configurations
        if agent_type == "arbitrage":
            base_config.update({
                "min_profit_threshold": 0.005,  # 0.5%
                "max_slippage": self.config.risk.max_slippage,
                "supported_chains": ["solana", "ethereum"],
                "supported_dexs": ["raydium", "uniswap_v3"]
            })
        elif agent_type == "market_making":
            base_config.update({
                "spread_target": 0.002,  # 0.2%
                "inventory_target": 0.5,
                "rebalance_threshold": 0.1
            })
        elif agent_type == "staking":
            base_config.update({
                "min_yield": 0.05,  # 5% APY
                "max_lockup_days": 365,
                "diversification_limit": 0.25
            })
        elif agent_type == "governance":
            base_config.update({
                "voting_threshold": 0.7,  # 70% confidence
                "analysis_depth": "detailed",
                "auto_vote": False
            })
        
        return base_config


# Global configuration instance
config_manager = ConfigManager()

def get_config() -> PortfolioConfig:
    """Get the global configuration instance."""
    return config_manager.get_config()

def validate_environment() -> Dict[str, Any]:
    """Validate the current environment configuration."""
    return config_manager.validate_config()

def get_agent_config(agent_type: str) -> Dict[str, Any]:
    """Get configuration for a specific agent type."""
    return config_manager.get_agent_config(agent_type)
