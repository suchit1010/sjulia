"""
Advanced DeFi Portfolio Manager - Main Application

Coordinates all components and provides the main execution flow.
"""

import asyncio
import os
import sys
from typing import Dict, Any
from datetime import datetime

# Add the project root to Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_root)

from src.utils.logger import portfolio_logger, log_info, log_error
from src.utils.config import get_config, validate_environment
from src.agents.agent_manager import PortfolioAgentManager
from src.strategies.portfolio_analysis import analyze_portfolio_opportunities


class AdvancedDefiPortfolioManager:
    """Main application orchestrating the DeFi portfolio management system."""
    
    def __init__(self):
        self.config = get_config()
        self.agent_manager = None
        self.is_running = False
        
    async def initialize(self) -> bool:
        """Initialize the portfolio management system."""
        try:
            log_info("🚀 Initializing Advanced DeFi Portfolio Manager")
            
            # Validate environment
            validation = validate_environment()
            if not validation["valid"]:
                log_error("Environment validation failed", issues=validation["issues"])
                return False
            
            if validation["warnings"]:
                portfolio_logger.warning("Environment warnings", warnings=validation["warnings"])
            
            log_info("✅ Environment validation passed", config=validation["config_summary"])
            
            # Initialize agent manager
            self.agent_manager = PortfolioAgentManager(self.config.juliaos.host)
            
            return True
            
        except Exception as e:
            log_error(f"Failed to initialize portfolio manager: {e}")
            return False
    
    async def start_system(self) -> Dict[str, Any]:
        """Start the complete portfolio management system."""
        try:
            log_info("🔄 Starting portfolio management system")
            
            # Step 1: Initialize agents
            manager = PortfolioAgentManager(self.config.juliaos.host)
            async with manager as agent_manager:
                log_info("📊 Initializing AI agents...")
                agent_results = await agent_manager.initialize_portfolio_agents()
                
                if "error" in agent_results:
                    log_error("Failed to initialize agents", error=agent_results["error"])
                    return {"success": False, "error": "Agent initialization failed"}
                
                log_info(f"✅ Successfully initialized {len(agent_results)} agent types")
                
                # Step 2: Perform initial portfolio analysis
                log_info("🔍 Performing initial portfolio analysis...")
                analysis_result = await analyze_portfolio_opportunities(
                    target_allocation_usd=self.config.risk.max_trade_size_usd * 10
                )
                
                if "error" in analysis_result:
                    log_error("Portfolio analysis failed", error=analysis_result["error"])
                else:
                    log_info("✅ Portfolio analysis completed", 
                            protocols=analysis_result.get("protocols_analyzed", 0),
                            opportunities=analysis_result.get("opportunities_found", 0))
                
                # Step 3: Start agent coordination
                log_info("🤖 Starting agent coordination and monitoring...")
                coordination_result = await self._start_agent_coordination(agent_manager, analysis_result)
                
                # Step 4: Begin continuous monitoring
                log_info("📈 Starting continuous portfolio monitoring...")
                self.is_running = True
                
                return {
                    "success": True,
                    "agents": agent_results,
                    "analysis": analysis_result,
                    "coordination": coordination_result,
                    "start_time": datetime.now().isoformat(),
                    "status": "running"
                }
                
        except Exception as e:
            log_error(f"Error starting system: {e}")
            return {"success": False, "error": str(e)}
    
    async def _start_agent_coordination(self, manager: PortfolioAgentManager, analysis_result: Dict[str, Any]) -> Dict[str, Any]:
        """Start coordination between agents based on analysis results."""
        try:
            coordination_results = {}
            
            # Task 1: Portfolio Analysis Agent - Continuous monitoring
            if analysis_result.get("optimization_result"):
                analysis_task = {
                    "task": "monitor_portfolio",
                    "optimization_data": analysis_result["optimization_result"],
                    "monitoring_interval": self.config.portfolio_rebalance_interval
                }
                
                analysis_result_task = await manager.execute_agent_task("analysis", analysis_task)
                coordination_results["analysis_task"] = analysis_result_task
            
            # Task 2: Arbitrage Swarm - Start monitoring
            arbitrage_task = {
                "task": "monitor_arbitrage",
                "target_profit_threshold": 0.005,  # 0.5%
                "max_trade_size": self.config.risk.max_trade_size_usd,
                "monitoring_interval": self.config.price_fetch_interval
            }
            
            arbitrage_result = await manager.execute_agent_task("arbitrage", arbitrage_task)
            coordination_results["arbitrage_task"] = arbitrage_result
            
            # Task 3: Market Making Agent - Start liquidity provision
            market_making_task = {
                "task": "start_market_making",
                "target_pairs": ["SOL/USDC", "ETH/USDC"],
                "spread_target": 0.002,
                "max_inventory": self.config.risk.max_trade_size_usd * 0.5
            }
            
            mm_result = await manager.execute_agent_task("market_making", market_making_task)
            coordination_results["market_making_task"] = mm_result
            
            # Task 4: Staking Agent - Optimize staking positions
            staking_task = {
                "task": "optimize_staking",
                "target_allocation": self.config.risk.max_trade_size_usd * 0.3,
                "min_yield": 0.05,
                "max_lockup_days": 365
            }
            
            staking_result = await manager.execute_agent_task("staking", staking_task)
            coordination_results["staking_task"] = staking_result
            
            # Task 5: Governance Agent - Monitor proposals
            governance_task = {
                "task": "monitor_governance",
                "dao_list": ["uniswap", "aave", "compound"],
                "voting_threshold": 0.7
            }
            
            governance_result = await manager.execute_agent_task("governance", governance_task)
            coordination_results["governance_task"] = governance_result
            
            # Task 6: Gaming Agent - Optimize gaming assets
            gaming_task = {
                "task": "analyze_gaming_portfolio",
                "focus_areas": ["nft_optimization", "play_to_earn"],
                "risk_tolerance": "moderate"
            }
            
            gaming_result = await manager.execute_agent_task("gaming", gaming_task)
            coordination_results["gaming_task"] = gaming_result
            
            # Task 7: Compliance Agent - Start monitoring
            compliance_task = {
                "task": "start_compliance_monitoring",
                "monitoring_scope": ["transaction_tracing", "risk_assessment"],
                "alert_threshold": "medium"
            }
            
            compliance_result = await manager.execute_agent_task("compliance", compliance_task)
            coordination_results["compliance_task"] = compliance_result
            
            log_info(f"✅ Agent coordination started with {len(coordination_results)} active tasks")
            return coordination_results
            
        except Exception as e:
            log_error(f"Error in agent coordination: {e}")
            return {"error": str(e)}
    
    async def run_monitoring_loop(self) -> None:
        """Run the continuous monitoring loop."""
        log_info("🔄 Starting continuous monitoring loop")
        
        loop_count = 0
        
        try:
            while self.is_running:
                loop_count += 1
                log_info(f"📊 Monitoring loop iteration {loop_count}")
                
                # Perform periodic tasks
                await self._perform_periodic_tasks()
                
                # Wait for next iteration
                await asyncio.sleep(self.config.agent_heartbeat_interval)
                
        except KeyboardInterrupt:
            log_info("⏹️ Monitoring loop interrupted by user")
            self.is_running = False
        except Exception as e:
            log_error(f"Error in monitoring loop: {e}")
            self.is_running = False
    
    async def _perform_periodic_tasks(self) -> None:
        """Perform periodic maintenance and monitoring tasks."""
        try:
            # Task 1: Health check on agents
            if self.agent_manager:
                async with self.agent_manager as manager:
                    agent_status = await manager.get_agent_status()
                    
                    active_agents = sum(
                        len(agents) if isinstance(agents, list) else 1 
                        for agents in agent_status.values()
                    )
                    
                    portfolio_logger.performance_metric("active_agents", active_agents)
            
            # Task 2: Portfolio rebalancing check (every 5 minutes)
            current_time = datetime.now()
            if current_time.minute % 5 == 0:
                log_info("🔄 Performing portfolio rebalancing check")
                # Trigger portfolio analysis update
                analysis_result = await analyze_portfolio_opportunities(
                    target_allocation_usd=self.config.risk.max_trade_size_usd * 10
                )
                
                if "error" not in analysis_result:
                    portfolio_logger.performance_metric(
                        "portfolio_opportunities", 
                        analysis_result.get("opportunities_found", 0)
                    )
            
            # Task 3: Risk monitoring
            await self._monitor_risk_metrics()
            
        except Exception as e:
            log_error(f"Error in periodic tasks: {e}")
    
    async def _monitor_risk_metrics(self) -> None:
        """Monitor risk metrics and alert on issues."""
        try:
            # Simple risk monitoring
            risk_metrics = {
                "system_uptime": (datetime.now() - datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)).total_seconds(),
                "active_strategies": 7,  # Number of agent types
                "max_trade_size": self.config.risk.max_trade_size_usd,
                "real_trading_enabled": self.config.risk.enable_real_trading
            }
            
            # Log risk metrics
            for metric, value in risk_metrics.items():
                portfolio_logger.performance_metric(f"risk_{metric}", value)
            
            # Alert if real trading is enabled (should be disabled for demo)
            if self.config.risk.enable_real_trading:
                portfolio_logger.risk_alert(
                    "real_trading_enabled", 
                    "HIGH", 
                    {"message": "Real trading is enabled - ensure this is intentional"}
                )
                
        except Exception as e:
            log_error(f"Error monitoring risk metrics: {e}")
    
    def stop_system(self) -> None:
        """Stop the portfolio management system."""
        log_info("⏹️ Stopping portfolio management system")
        self.is_running = False
    
    async def get_system_status(self) -> Dict[str, Any]:
        """Get comprehensive system status."""
        try:
            status = {
                "system_running": self.is_running,
                "config_summary": {
                    "juliaos_host": self.config.juliaos.host,
                    "real_trading": self.config.risk.enable_real_trading,
                    "max_trade_size": self.config.risk.max_trade_size_usd,
                    "log_level": self.config.logging.level
                },
                "performance_metrics": portfolio_logger.get_performance_summary(),
                "timestamp": datetime.now().isoformat()
            }
            
            if self.agent_manager:
                async with self.agent_manager as manager:
                    status["agents"] = await manager.get_agent_status()
            
            return status
            
        except Exception as e:
            log_error(f"Error getting system status: {e}")
            return {"error": str(e)}


async def main():
    """Main entry point for the Advanced DeFi Portfolio Manager."""
    
    print("🚀 Advanced DeFi Portfolio Manager")
    print("=" * 50)
    print("Powered by JuliaOS AI Agents & Swarm Intelligence")
    print("=" * 50)
    
    manager = AdvancedDefiPortfolioManager()
    
    try:
        # Initialize system
        if not await manager.initialize():
            print("❌ Failed to initialize system")
            return
        
        # Start system
        start_result = await manager.start_system()
        
        if not start_result["success"]:
            print(f"❌ Failed to start system: {start_result.get('error', 'Unknown error')}")
            return
        
        print("✅ System started successfully!")
        print("\n📊 System Summary:")
        print(f"   • Agents initialized: {len(start_result['agents'])}")
        print(f"   • Protocols analyzed: {start_result['analysis'].get('protocols_analyzed', 0)}")
        print(f"   • Opportunities found: {start_result['analysis'].get('opportunities_found', 0)}")
        print(f"   • Status: {start_result['status']}")
        
        print("\n🤖 Active Agents:")
        for agent_type, agent_id in start_result['agents'].items():
            print(f"   • {agent_type}: {agent_id}")
        
        print("\n📈 Starting continuous monitoring...")
        print("Press Ctrl+C to stop the system")
        
        # Run monitoring loop
        await manager.run_monitoring_loop()
        
    except KeyboardInterrupt:
        print("\n⏹️ System shutdown requested")
    except Exception as e:
        log_error(f"Unexpected error in main: {e}")
        print(f"❌ Unexpected error: {e}")
    finally:
        manager.stop_system()
        print("🔄 System cleanup completed")
        print("👋 Thank you for using Advanced DeFi Portfolio Manager!")


if __name__ == "__main__":
    asyncio.run(main())
