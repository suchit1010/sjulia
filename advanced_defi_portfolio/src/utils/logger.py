"""
Advanced Logging System for DeFi Portfolio Manager

Provides structured logging with multiple outputs and performance tracking.
"""

import os
import sys
import json
import time
from datetime import datetime
from typing import Any, Dict, Optional
from loguru import logger
from pathlib import Path


class PortfolioLogger:
    """Enhanced logger for portfolio management operations."""
    
    def __init__(self, log_level: str = "INFO", log_file: Optional[str] = None):
        self.start_time = time.time()
        self.log_file = log_file or "logs/portfolio_manager.log"
        
        # Create logs directory if it doesn't exist
        Path(self.log_file).parent.mkdir(parents=True, exist_ok=True)
        
        # Remove default logger
        logger.remove()
        
        # Add console handler with custom format
        logger.add(
            sys.stdout,
            format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
                   "<level>{level: <8}</level> | "
                   "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | "
                   "<level>{message}</level>",
            level=log_level,
            colorize=True
        )
        
        # Add file handler with JSON format for structured logging
        logger.add(
            self.log_file,
            format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {name}:{function}:{line} | {message}",
            level=log_level,
            rotation="1 day",
            retention="30 days",
            compression="gz"
        )
        
        # Add separate file for agent actions
        logger.add(
            "logs/agent_actions.log",
            format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {message}",
            level="INFO",
            filter=lambda record: "AGENT_ACTION" in record["message"],
            rotation="1 day"
        )
        
        # Add separate file for trading operations
        logger.add(
            "logs/trading.log", 
            format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {message}",
            level="INFO",
            filter=lambda record: "TRADE" in record["message"] or "ARBITRAGE" in record["message"],
            rotation="1 day"
        )
        
        self.logger = logger
        self.performance_metrics = {}
        
    def info(self, message: str, **kwargs):
        """Log info message with optional structured data."""
        if kwargs:
            message = f"{message} | Data: {json.dumps(kwargs, default=str)}"
        self.logger.info(message)
        
    def warning(self, message: str, **kwargs):
        """Log warning message with optional structured data."""
        if kwargs:
            message = f"{message} | Data: {json.dumps(kwargs, default=str)}"
        self.logger.warning(message)
        
    def error(self, message: str, **kwargs):
        """Log error message with optional structured data."""
        if kwargs:
            message = f"{message} | Data: {json.dumps(kwargs, default=str)}"
        self.logger.error(message)
        
    def debug(self, message: str, **kwargs):
        """Log debug message with optional structured data."""
        if kwargs:
            message = f"{message} | Data: {json.dumps(kwargs, default=str)}"
        self.logger.debug(message)

    def agent_action(self, agent_id: str, action: str, details: Dict[str, Any]):
        """Log agent-specific actions for tracking."""
        message = f"AGENT_ACTION | Agent: {agent_id} | Action: {action} | Details: {json.dumps(details, default=str)}"
        self.logger.info(message)
        
    def trade_action(self, trade_type: str, symbol: str, amount: float, price: float, details: Optional[Dict[str, Any]] = None):
        """Log trading operations."""
        trade_data = {
            "type": trade_type,
            "symbol": symbol,
            "amount": amount,
            "price": price,
            "timestamp": datetime.now().isoformat(),
            "details": details or {}
        }
        message = f"TRADE | {json.dumps(trade_data, default=str)}"
        self.logger.info(message)
        
    def arbitrage_opportunity(self, opportunity: Dict[str, Any]):
        """Log arbitrage opportunities."""
        message = f"ARBITRAGE | Opportunity: {json.dumps(opportunity, default=str)}"
        self.logger.info(message)
        
    def portfolio_update(self, portfolio_data: Dict[str, Any]):
        """Log portfolio state changes."""
        message = f"PORTFOLIO_UPDATE | {json.dumps(portfolio_data, default=str)}"
        self.logger.info(message)
        
    def performance_metric(self, metric_name: str, value: float, details: Optional[Dict[str, Any]] = None):
        """Track performance metrics."""
        timestamp = datetime.now().isoformat()
        self.performance_metrics[metric_name] = {
            "value": value,
            "timestamp": timestamp,
            "details": details or {}
        }
        
        message = f"METRIC | {metric_name}: {value} | {json.dumps(details or {}, default=str)}"
        self.logger.info(message)
        
    def swarm_coordination(self, swarm_id: str, action: str, agents: list, details: Dict[str, Any]):
        """Log swarm coordination activities."""
        swarm_data = {
            "swarm_id": swarm_id,
            "action": action,
            "agents": agents,
            "timestamp": datetime.now().isoformat(),
            "details": details
        }
        message = f"SWARM | {json.dumps(swarm_data, default=str)}"
        self.logger.info(message)
        
    def risk_alert(self, risk_type: str, severity: str, details: Dict[str, Any]):
        """Log risk management alerts."""
        alert_data = {
            "risk_type": risk_type,
            "severity": severity,
            "timestamp": datetime.now().isoformat(),
            "details": details
        }
        message = f"RISK_ALERT | {json.dumps(alert_data, default=str)}"
        
        if severity.upper() in ["HIGH", "CRITICAL"]:
            self.logger.error(message)
        elif severity.upper() == "MEDIUM":
            self.logger.warning(message)
        else:
            self.logger.info(message)
            
    def llm_interaction(self, agent_id: str, prompt: str, response: str, model: str):
        """Log LLM interactions for analysis."""
        llm_data = {
            "agent_id": agent_id,
            "model": model,
            "prompt_length": len(prompt),
            "response_length": len(response),
            "timestamp": datetime.now().isoformat(),
            "prompt_preview": prompt[:100] + "..." if len(prompt) > 100 else prompt,
            "response_preview": response[:100] + "..." if len(response) > 100 else response
        }
        message = f"LLM_INTERACTION | {json.dumps(llm_data, default=str)}"
        self.logger.debug(message)
        
    def get_performance_summary(self) -> Dict[str, Any]:
        """Get summary of performance metrics."""
        uptime = time.time() - self.start_time
        return {
            "uptime_seconds": uptime,
            "uptime_hours": uptime / 3600,
            "metrics": self.performance_metrics,
            "log_file": self.log_file
        }


# Global logger instance
portfolio_logger = PortfolioLogger(
    log_level=os.getenv("LOG_LEVEL", "INFO"),
    log_file=os.getenv("LOG_FILE", "logs/portfolio_manager.log")
)

# Convenience functions for easy import
def log_info(message: str, **kwargs):
    """Convenience function for info logging."""
    portfolio_logger.info(message, **kwargs)

def log_error(message: str, **kwargs):
    """Convenience function for error logging."""
    portfolio_logger.error(message, **kwargs)

def log_warning(message: str, **kwargs):
    """Convenience function for warning logging."""
    portfolio_logger.warning(message, **kwargs)

def log_debug(message: str, **kwargs):
    """Convenience function for debug logging."""
    portfolio_logger.debug(message, **kwargs)

def log_agent_action(agent_id: str, action: str, details: Dict[str, Any]):
    """Convenience function for agent action logging."""
    portfolio_logger.agent_action(agent_id, action, details)

def log_trade(trade_type: str, symbol: str, amount: float, price: float, details: Optional[Dict[str, Any]] = None):
    """Convenience function for trade logging."""
    portfolio_logger.trade_action(trade_type, symbol, amount, price, details)

def log_arbitrage(opportunity: Dict[str, Any]):
    """Convenience function for arbitrage logging."""
    portfolio_logger.arbitrage_opportunity(opportunity)
