"""
JuliaOS Agent Integration

Core agent creation and management for the Advanced DeFi Portfolio Manager.
"""

import asyncio
import sys
import os
from typing import Dict, List, Any, Optional
from datetime import datetime
import json

# Add parent directory to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..', 'python', 'src'))

import juliaos
from ..utils.logger import portfolio_logger, log_agent_action
from ..utils.config import get_config, get_agent_config


class PortfolioAgentManager:
    """Manages JuliaOS agents for portfolio operations."""
    
    def __init__(self, juliaos_host: str = "http://127.0.0.1:8052/api/v1"):
        self.host = juliaos_host
        self.config = get_config()
        self.agents = {}
        self.connection = None
        
    async def __aenter__(self):
        """Async context manager entry."""
        self.connection = juliaos.JuliaOSConnection(self.host)
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        if self.connection:
            await self.cleanup_agents()
    
    async def initialize_portfolio_agents(self) -> Dict[str, Any]:
        """Initialize all portfolio management agents."""
        portfolio_logger.info("Initializing portfolio management agents")
        
        results = {}
        
        try:
            with self.connection as conn:
                # 1. Portfolio Analysis Agent
                analysis_agent = await self._create_analysis_agent(conn)
                if analysis_agent:
                    results["analysis_agent"] = analysis_agent.id
                    self.agents["analysis"] = analysis_agent
                
                # 2. Cross-Chain Arbitrage Swarm
                arbitrage_agents = await self._create_arbitrage_swarm(conn)
                if arbitrage_agents:
                    results["arbitrage_swarm"] = [agent.id for agent in arbitrage_agents]
                    self.agents["arbitrage"] = arbitrage_agents
                
                # 3. Market Making Agents
                market_making_agent = await self._create_market_making_agent(conn)
                if market_making_agent:
                    results["market_making_agent"] = market_making_agent.id
                    self.agents["market_making"] = market_making_agent
                
                # 4. Staking Optimization Agent
                staking_agent = await self._create_staking_agent(conn)
                if staking_agent:
                    results["staking_agent"] = staking_agent.id
                    self.agents["staking"] = staking_agent
                
                # 5. DAO Governance Advisor
                governance_agent = await self._create_governance_agent(conn)
                if governance_agent:
                    results["governance_agent"] = governance_agent.id
                    self.agents["governance"] = governance_agent
                
                # 6. Gaming Companion Agent
                gaming_agent = await self._create_gaming_agent(conn)
                if gaming_agent:
                    results["gaming_agent"] = gaming_agent.id
                    self.agents["gaming"] = gaming_agent
                
                # 7. Compliance Agent
                compliance_agent = await self._create_compliance_agent(conn)
                if compliance_agent:
                    results["compliance_agent"] = compliance_agent.id
                    self.agents["compliance"] = compliance_agent
                
                portfolio_logger.info(f"Successfully initialized {len(results)} agent types")
                return results
                
        except Exception as e:
            portfolio_logger.error(f"Error initializing agents: {e}")
            return {"error": str(e)}
    
    async def _create_analysis_agent(self, conn) -> Optional[juliaos.Agent]:
        """Create the portfolio analysis agent."""
        try:
            agent_config = get_agent_config("analysis")
            
            blueprint = juliaos.AgentBlueprint(
                tools=[
                    juliaos.ToolBlueprint(
                        name="llm_chat",
                        config={}
                    ),
                    juliaos.ToolBlueprint(
                        name="ping",
                        config={}
                    )
                ],
                strategy=juliaos.StrategyBlueprint(
                    name="plan_execute",
                    config={
                        "analysis_type": "portfolio_optimization",
                        "target_allocation": 10000,
                        "risk_tolerance": "moderate"
                    }
                ),
                trigger=juliaos.TriggerConfig(
                    type="webhook",
                    params={}
                )
            )
            
            agent_id = "portfolio-analysis-agent"
            agent_name = "Portfolio Analysis Agent"
            agent_description = "AI agent that analyzes DeFi protocols and optimizes portfolio allocation"
            
            # Clean up existing agent
            try:
                existing_agent = juliaos.Agent.load(conn, agent_id)
                if existing_agent:
                    existing_agent.delete()
                    portfolio_logger.info(f"Cleaned up existing agent: {agent_id}")
            except:
                pass
            
            # Create new agent
            agent = juliaos.Agent.create(conn, blueprint, agent_id, agent_name, agent_description)
            if agent:
                agent.set_state(juliaos.AgentState.RUNNING)
                log_agent_action(agent_id, "created", {"type": "analysis", "status": "running"})
                portfolio_logger.info(f"Created portfolio analysis agent: {agent_id}")
                return agent
            
        except Exception as e:
            portfolio_logger.error(f"Error creating analysis agent: {e}")
            return None
    
    async def _create_arbitrage_swarm(self, conn) -> List[juliaos.Agent]:
        """Create cross-chain arbitrage swarm agents."""
        try:
            agents = []
            chains = ["solana", "ethereum"]
            
            for i, chain in enumerate(chains):
                agent_config = get_agent_config("arbitrage")
                
                blueprint = juliaos.AgentBlueprint(
                    tools=[
                        juliaos.ToolBlueprint(
                            name="llm_chat",
                            config={}
                        ),
                        juliaos.ToolBlueprint(
                            name="ping",
                            config={}
                        )
                    ],
                    strategy=juliaos.StrategyBlueprint(
                        name="plan_execute",
                        config={
                            "strategy_type": "arbitrage",
                            "target_chain": chain,
                            "min_profit_threshold": 0.005,
                            "max_trade_size": 1000
                        }
                    ),
                    trigger=juliaos.TriggerConfig(
                        type="webhook",
                        params={}
                    )
                )
                
                agent_id = f"arbitrage-{chain}-agent"
                agent_name = f"Arbitrage Agent ({chain.title()})"
                agent_description = f"Cross-chain arbitrage agent monitoring {chain} opportunities"
                
                # Clean up existing
                try:
                    existing_agent = juliaos.Agent.load(conn, agent_id)
                    if existing_agent:
                        existing_agent.delete()
                except:
                    pass
                
                # Create new agent
                agent = juliaos.Agent.create(conn, blueprint, agent_id, agent_name, agent_description)
                if agent:
                    agent.set_state(juliaos.AgentState.RUNNING)
                    agents.append(agent)
                    log_agent_action(agent_id, "created", {"type": "arbitrage", "chain": chain, "status": "running"})
                    portfolio_logger.info(f"Created arbitrage agent for {chain}: {agent_id}")
            
            return agents
            
        except Exception as e:
            portfolio_logger.error(f"Error creating arbitrage swarm: {e}")
            return []
    
    async def _create_market_making_agent(self, conn) -> Optional[juliaos.Agent]:
        """Create market making agent."""
        try:
            agent_config = get_agent_config("market_making")
            
            blueprint = juliaos.AgentBlueprint(
                tools=[
                    juliaos.ToolBlueprint(
                        name="llm_chat",
                        config={}
                    ),
                    juliaos.ToolBlueprint(
                        name="ping",
                        config={}
                    )
                ],
                strategy=juliaos.StrategyBlueprint(
                    name="plan_execute",
                    config={
                        "strategy_type": "market_making",
                        "spread_target": 0.002,
                        "inventory_target": 0.5,
                        "rebalance_threshold": 0.1
                    }
                ),
                trigger=juliaos.TriggerConfig(
                    type="webhook",
                    params={}
                )
            )
            
            agent_id = "market-making-agent"
            agent_name = "Market Making Agent"
            agent_description = "AI agent providing liquidity across DEXs with optimal spreads"
            
            # Clean up existing
            try:
                existing_agent = juliaos.Agent.load(conn, agent_id)
                if existing_agent:
                    existing_agent.delete()
            except:
                pass
            
            # Create new agent
            agent = juliaos.Agent.create(conn, blueprint, agent_id, agent_name, agent_description)
            if agent:
                agent.set_state(juliaos.AgentState.RUNNING)
                log_agent_action(agent_id, "created", {"type": "market_making", "status": "running"})
                portfolio_logger.info(f"Created market making agent: {agent_id}")
                return agent
                
        except Exception as e:
            portfolio_logger.error(f"Error creating market making agent: {e}")
            return None
    
    async def _create_staking_agent(self, conn) -> Optional[juliaos.Agent]:
        """Create staking optimization agent."""
        try:
            agent_config = get_agent_config("staking")
            
            blueprint = juliaos.AgentBlueprint(
                tools=[
                    juliaos.ToolBlueprint(
                        name="llm_chat",
                        config={}
                    ),
                    juliaos.ToolBlueprint(
                        name="ping",
                        config={}
                    )
                ],
                strategy=juliaos.StrategyBlueprint(
                    name="plan_execute",
                    config={
                        "strategy_type": "staking",
                        "min_yield": 0.05,
                        "max_lockup_days": 365,
                        "diversification_limit": 0.25
                    }
                ),
                trigger=juliaos.TriggerConfig(
                    type="webhook",
                    params={}
                )
            )
            
            agent_id = "staking-optimizer-agent"
            agent_name = "Staking Optimizer Agent"
            agent_description = "AI agent optimizing staking rewards across multiple protocols"
            
            # Clean up existing
            try:
                existing_agent = juliaos.Agent.load(conn, agent_id)
                if existing_agent:
                    existing_agent.delete()
            except:
                pass
            
            # Create new agent
            agent = juliaos.Agent.create(conn, blueprint, agent_id, agent_name, agent_description)
            if agent:
                agent.set_state(juliaos.AgentState.RUNNING)
                log_agent_action(agent_id, "created", {"type": "staking", "status": "running"})
                portfolio_logger.info(f"Created staking agent: {agent_id}")
                return agent
                
        except Exception as e:
            portfolio_logger.error(f"Error creating staking agent: {e}")
            return None
    
    async def _create_governance_agent(self, conn) -> Optional[juliaos.Agent]:
        """Create DAO governance advisor agent."""
        try:
            agent_config = get_agent_config("governance")
            
            blueprint = juliaos.AgentBlueprint(
                tools=[
                    juliaos.ToolBlueprint(
                        name="llm_chat",
                        config={}
                    ),
                    juliaos.ToolBlueprint(
                        name="ping",
                        config={}
                    )
                ],
                strategy=juliaos.StrategyBlueprint(
                    name="plan_execute",
                    config={
                        "strategy_type": "governance",
                        "voting_threshold": 0.7,
                        "analysis_depth": "detailed",
                        "auto_vote": False
                    }
                ),
                trigger=juliaos.TriggerConfig(
                    type="webhook",
                    params={}
                )
            )
            
            agent_id = "dao-governance-agent"
            agent_name = "DAO Governance Advisor"
            agent_description = "AI agent analyzing DAO proposals and providing voting recommendations"
            
            # Clean up existing
            try:
                existing_agent = juliaos.Agent.load(conn, agent_id)
                if existing_agent:
                    existing_agent.delete()
            except:
                pass
            
            # Create new agent
            agent = juliaos.Agent.create(conn, blueprint, agent_id, agent_name, agent_description)
            if agent:
                agent.set_state(juliaos.AgentState.RUNNING)
                log_agent_action(agent_id, "created", {"type": "governance", "status": "running"})
                portfolio_logger.info(f"Created governance agent: {agent_id}")
                return agent
                
        except Exception as e:
            portfolio_logger.error(f"Error creating governance agent: {e}")
            return None
    
    async def _create_gaming_agent(self, conn) -> Optional[juliaos.Agent]:
        """Create Web3 gaming companion agent."""
        try:
            blueprint = juliaos.AgentBlueprint(
                tools=[
                    juliaos.ToolBlueprint(
                        name="llm_chat",
                        config={}
                    ),
                    juliaos.ToolBlueprint(
                        name="ping",
                        config={}
                    )
                ],
                strategy=juliaos.StrategyBlueprint(
                    name="plan_execute",
                    config={
                        "strategy_type": "gaming",
                        "focus_areas": ["nft_optimization", "token_management", "play_to_earn"],
                        "risk_tolerance": "moderate"
                    }
                ),
                trigger=juliaos.TriggerConfig(
                    type="webhook",
                    params={}
                )
            )
            
            agent_id = "web3-gaming-agent"
            agent_name = "Web3 Gaming Companion"
            agent_description = "AI agent optimizing gaming assets and play-to-earn strategies"
            
            # Clean up existing
            try:
                existing_agent = juliaos.Agent.load(conn, agent_id)
                if existing_agent:
                    existing_agent.delete()
            except:
                pass
            
            # Create new agent
            agent = juliaos.Agent.create(conn, blueprint, agent_id, agent_name, agent_description)
            if agent:
                agent.set_state(juliaos.AgentState.RUNNING)
                log_agent_action(agent_id, "created", {"type": "gaming", "status": "running"})
                portfolio_logger.info(f"Created gaming agent: {agent_id}")
                return agent
                
        except Exception as e:
            portfolio_logger.error(f"Error creating gaming agent: {e}")
            return None
    
    async def _create_compliance_agent(self, conn) -> Optional[juliaos.Agent]:
        """Create transaction compliance agent."""
        try:
            blueprint = juliaos.AgentBlueprint(
                tools=[
                    juliaos.ToolBlueprint(
                        name="llm_chat",
                        config={}
                    ),
                    juliaos.ToolBlueprint(
                        name="ping",
                        config={}
                    )
                ],
                strategy=juliaos.StrategyBlueprint(
                    name="plan_execute",
                    config={
                        "strategy_type": "compliance",
                        "monitoring_scope": ["transaction_tracing", "risk_assessment", "aml_screening"],
                        "alert_threshold": "medium"
                    }
                ),
                trigger=juliaos.TriggerConfig(
                    type="webhook",
                    params={}
                )
            )
            
            agent_id = "compliance-monitor-agent"
            agent_name = "Compliance Monitor Agent"
            agent_description = "AI agent monitoring transactions for compliance and risk assessment"
            
            # Clean up existing
            try:
                existing_agent = juliaos.Agent.load(conn, agent_id)
                if existing_agent:
                    existing_agent.delete()
            except:
                pass
            
            # Create new agent
            agent = juliaos.Agent.create(conn, blueprint, agent_id, agent_name, agent_description)
            if agent:
                agent.set_state(juliaos.AgentState.RUNNING)
                log_agent_action(agent_id, "created", {"type": "compliance", "status": "running"})
                portfolio_logger.info(f"Created compliance agent: {agent_id}")
                return agent
                
        except Exception as e:
            portfolio_logger.error(f"Error creating compliance agent: {e}")
            return None
    
    async def execute_agent_task(self, agent_type: str, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a task on a specific agent."""
        try:
            if agent_type not in self.agents:
                return {"error": f"Agent type {agent_type} not found"}
            
            agent = self.agents[agent_type]
            if isinstance(agent, list):
                # For swarm agents, execute on first agent
                agent = agent[0]
            
            result = agent.call_webhook(task_data)
            
            log_agent_action(
                agent.id, 
                "task_executed", 
                {"task_type": agent_type, "task_data": task_data, "result": result}
            )
            
            return {"success": True, "result": result, "agent_id": agent.id}
            
        except Exception as e:
            portfolio_logger.error(f"Error executing task on {agent_type}: {e}")
            return {"error": str(e)}
    
    async def get_agent_status(self) -> Dict[str, Any]:
        """Get status of all agents."""
        status = {}
        
        for agent_type, agent in self.agents.items():
            if isinstance(agent, list):
                # For swarm agents
                status[agent_type] = [
                    {
                        "id": a.id,
                        "summary": a.get_summary()
                    } for a in agent
                ]
            else:
                # For single agents
                status[agent_type] = {
                    "id": agent.id,
                    "summary": agent.get_summary()
                }
        
        return status
    
    async def cleanup_agents(self):
        """Clean up all agents."""
        portfolio_logger.info("Cleaning up portfolio agents")
        
        for agent_type, agent in self.agents.items():
            try:
                if isinstance(agent, list):
                    for a in agent:
                        a.delete()
                        log_agent_action(a.id, "deleted", {"type": agent_type})
                else:
                    agent.delete()
                    log_agent_action(agent.id, "deleted", {"type": agent_type})
            except Exception as e:
                portfolio_logger.error(f"Error cleaning up {agent_type} agent: {e}")


async def main():
    """Test agent creation and management."""
    portfolio_logger.info("Testing Portfolio Agent Manager")
    
    try:
        async with PortfolioAgentManager() as manager:
            # Initialize all agents
            results = await manager.initialize_portfolio_agents()
            portfolio_logger.info(f"Agent initialization results: {results}")
            
            # Test agent execution
            if "analysis_agent" in results:
                test_task = {
                    "task": "analyze_portfolio",
                    "target_allocation": 10000,
                    "risk_tolerance": "moderate"
                }
                
                result = await manager.execute_agent_task("analysis", test_task)
                portfolio_logger.info(f"Analysis agent test result: {result}")
            
            # Get agent status
            status = await manager.get_agent_status()
            portfolio_logger.info(f"All agents status: {status}")
            
    except Exception as e:
        portfolio_logger.error(f"Error in agent manager test: {e}")


if __name__ == "__main__":
    asyncio.run(main())
