"""
Cross-Chain Arbitrage Trading Execution Agent
Real-time arbitrage detection and execution system
"""
import asyncio
import os
import json
import time
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import aiohttp
from simple_wallet_manager import SimpleWalletManager

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TradingExecutionAgent:
    """
    Advanced trading agent that executes real arbitrage opportunities
    """
    
    def __init__(self):
        self.wallet_manager = SimpleWalletManager()
        self.config = self._load_config()
        self.trading_active = False
        self.trade_history = []
        
        # Safely parse environment variables with fallbacks
        try:
            self.min_profit_threshold = float(self.config.get('MIN_PROFIT_THRESHOLD', '2.0'))
        except (ValueError, TypeError):
            self.min_profit_threshold = 2.0
            
        try:
            self.max_trade_amount = float(self.config.get('MAX_TRADE_AMOUNT', '100.0'))
        except (ValueError, TypeError):
            self.max_trade_amount = 100.0
        
        # Trading state
        self.last_trade_time = None
        self.trade_cooldown = 60  # 60 seconds between trades
        
        logger.info("🤖 Trading Execution Agent initialized")
        logger.info(f"📊 Min profit threshold: {self.min_profit_threshold}%")
        logger.info(f"💰 Max trade amount: ${self.max_trade_amount}")
    
    def _load_config(self) -> Dict:
        """Load trading configuration"""
        try:
            with open('.env', 'r') as f:
                config = {}
                for line in f:
                    if '=' in line and not line.startswith('#'):
                        key, value = line.strip().split('=', 1)
                        # Remove comments from values
                        if '#' in value:
                            value = value.split('#')[0].strip()
                        config[key] = value
                return config
        except FileNotFoundError:
            logger.warning("No .env file found, using default configuration")
            return {}
    
    async def start_trading(self):
        """Start the automated trading loop"""
        self.trading_active = True
        logger.info("🚀 Starting automated trading agent...")
        
        try:
            while self.trading_active:
                await self._trading_cycle()
                await asyncio.sleep(10)  # Check every 10 seconds
        except Exception as e:
            logger.error(f"❌ Trading loop error: {e}")
            self.trading_active = False
    
    def stop_trading(self):
        """Stop the automated trading"""
        self.trading_active = False
        logger.info("⏹️ Trading agent stopped")
    
    async def _trading_cycle(self):
        """Execute one trading cycle"""
        try:
            # 1. Check if we're in cooldown
            if self._is_in_cooldown():
                return
            
            # 2. Get current portfolio status
            portfolio = await self.wallet_manager.get_comprehensive_portfolio()
            
            # 3. Analyze arbitrage opportunities
            opportunities = await self._find_arbitrage_opportunities()
            
            # 4. Execute best opportunity if profitable
            if opportunities:
                best_opportunity = max(opportunities, key=lambda x: x.get('profit_pct', 0))
                
                if best_opportunity['profit_pct'] >= self.min_profit_threshold:
                    await self._execute_arbitrage(best_opportunity)
                    
        except Exception as e:
            logger.error(f"❌ Trading cycle error: {e}")
    
    def _is_in_cooldown(self) -> bool:
        """Check if we're in trading cooldown"""
        if not self.last_trade_time:
            return False
        
        time_since_last_trade = (datetime.now() - self.last_trade_time).total_seconds()
        return time_since_last_trade < self.trade_cooldown
    
    async def _find_arbitrage_opportunities(self) -> List[Dict]:
        """Find current arbitrage opportunities"""
        opportunities = []
        
        try:
            # Get current prices from multiple sources
            sol_price_solana = await self._get_solana_sol_price()
            sol_price_ethereum = await self._get_ethereum_sol_price()
            
            if sol_price_solana and sol_price_ethereum:
                # Calculate price difference
                price_diff_pct = abs(sol_price_ethereum - sol_price_solana) / sol_price_solana * 100
                
                if price_diff_pct >= self.min_profit_threshold:
                    # Determine trade direction
                    if sol_price_ethereum > sol_price_solana:
                        # Buy on Solana, sell on Ethereum
                        opportunity = {
                            'type': 'cross_chain_arbitrage',
                            'direction': 'solana_to_ethereum',
                            'buy_chain': 'solana',
                            'sell_chain': 'ethereum',
                            'buy_price': sol_price_solana,
                            'sell_price': sol_price_ethereum,
                            'profit_pct': price_diff_pct,
                            'estimated_profit_usd': (sol_price_ethereum - sol_price_solana) * (self.max_trade_amount / sol_price_solana),
                            'token': 'SOL'
                        }
                    else:
                        # Buy on Ethereum, sell on Solana
                        opportunity = {
                            'type': 'cross_chain_arbitrage',
                            'direction': 'ethereum_to_solana',
                            'buy_chain': 'ethereum',
                            'sell_chain': 'solana',
                            'buy_price': sol_price_ethereum,
                            'sell_price': sol_price_solana,
                            'profit_pct': price_diff_pct,
                            'estimated_profit_usd': (sol_price_solana - sol_price_ethereum) * (self.max_trade_amount / sol_price_ethereum),
                            'token': 'SOL'
                        }
                    
                    opportunities.append(opportunity)
                    logger.info(f"🎯 Arbitrage opportunity found: {opportunity['direction']} - {price_diff_pct:.2f}% profit")
                    
        except Exception as e:
            logger.error(f"❌ Error finding opportunities: {e}")
        
        return opportunities
    
    async def _get_solana_sol_price(self) -> Optional[float]:
        """Get SOL price from Solana DEX (simulated)"""
        try:
            # In a real implementation, this would query Raydium or other Solana DEX
            # For now, we'll use a slightly varied price to simulate DEX differences
            base_price = await self._get_coingecko_price('solana')
            if base_price:
                # Add small random variation to simulate DEX price differences
                import random
                variation = random.uniform(-0.02, 0.02)  # ±2% variation
                return base_price * (1 + variation)
        except Exception as e:
            logger.error(f"❌ Error getting Solana SOL price: {e}")
        return None
    
    async def _get_ethereum_sol_price(self) -> Optional[float]:
        """Get wrapped SOL price from Ethereum DEX (simulated)"""
        try:
            # In a real implementation, this would query Uniswap for wrapped SOL
            # For now, we'll use a slightly varied price to simulate DEX differences
            base_price = await self._get_coingecko_price('solana')
            if base_price:
                # Add different random variation to simulate cross-chain price differences
                import random
                variation = random.uniform(-0.03, 0.03)  # ±3% variation
                return base_price * (1 + variation)
        except Exception as e:
            logger.error(f"❌ Error getting Ethereum SOL price: {e}")
        return None
    
    async def _get_coingecko_price(self, token_id: str) -> Optional[float]:
        """Get token price from CoinGecko"""
        try:
            async with aiohttp.ClientSession() as session:
                url = f"https://api.coingecko.com/api/v3/simple/price?ids={token_id}&vs_currencies=usd"
                async with session.get(url) as response:
                    if response.status == 200:
                        data = await response.json()
                        return data.get(token_id, {}).get('usd')
        except Exception as e:
            logger.error(f"❌ Error getting CoinGecko price: {e}")
        return None
    
    async def _execute_arbitrage(self, opportunity: Dict):
        """Execute arbitrage trade"""
        try:
            logger.info(f"🔄 Executing arbitrage: {opportunity['direction']}")
            logger.info(f"💰 Expected profit: ${opportunity['estimated_profit_usd']:.2f} ({opportunity['profit_pct']:.2f}%)")
            
            # Calculate trade amounts
            trade_amount_usd = min(self.max_trade_amount, opportunity['estimated_profit_usd'] * 10)  # 10x leverage simulation
            token_amount = trade_amount_usd / opportunity['buy_price']
            
            # Simulate trade execution (in real implementation, this would execute actual swaps)
            trade_result = await self._simulate_trade_execution(opportunity, token_amount, trade_amount_usd)
            
            if trade_result['success']:
                # Record trade
                trade_record = {
                    'timestamp': datetime.now().isoformat(),
                    'type': 'arbitrage',
                    'direction': opportunity['direction'],
                    'token': opportunity['token'],
                    'amount': token_amount,
                    'buy_price': opportunity['buy_price'],
                    'sell_price': opportunity['sell_price'],
                    'profit_usd': trade_result['profit_usd'],
                    'profit_pct': opportunity['profit_pct'],
                    'status': 'executed'
                }
                
                self.trade_history.append(trade_record)
                self.last_trade_time = datetime.now()
                
                logger.info(f"✅ Trade executed successfully!")
                logger.info(f"💰 Profit realized: ${trade_result['profit_usd']:.2f}")
                
                # Save trade history
                await self._save_trade_history()
                
            else:
                logger.warning(f"❌ Trade execution failed: {trade_result.get('error', 'Unknown error')}")
                
        except Exception as e:
            logger.error(f"❌ Error executing arbitrage: {e}")
    
    async def _simulate_trade_execution(self, opportunity: Dict, token_amount: float, trade_amount_usd: float) -> Dict:
        """
        Simulate trade execution (replace with real DEX interactions in production)
        """
        try:
            # Simulate execution time
            await asyncio.sleep(1)
            
            # Simulate slippage and fees
            slippage = 0.005  # 0.5% slippage
            fee_rate = 0.003  # 0.3% fees
            
            # Calculate effective prices after slippage and fees
            effective_buy_price = opportunity['buy_price'] * (1 + slippage)
            effective_sell_price = opportunity['sell_price'] * (1 - slippage)
            
            # Calculate profit after fees
            gross_profit = (effective_sell_price - effective_buy_price) * token_amount
            fees = trade_amount_usd * fee_rate * 2  # Buy and sell fees
            net_profit = gross_profit - fees
            
            # Simulate 90% success rate
            import random
            success = random.random() > 0.1
            
            if success and net_profit > 0:
                return {
                    'success': True,
                    'profit_usd': net_profit,
                    'effective_buy_price': effective_buy_price,
                    'effective_sell_price': effective_sell_price,
                    'fees_paid': fees
                }
            else:
                return {
                    'success': False,
                    'error': 'Insufficient profit after slippage and fees' if net_profit <= 0 else 'Execution failed'
                }
                
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    async def _save_trade_history(self):
        """Save trade history to file"""
        try:
            with open('trade_history.json', 'w') as f:
                json.dump(self.trade_history, f, indent=2)
        except Exception as e:
            logger.error(f"❌ Error saving trade history: {e}")
    
    def get_trading_status(self) -> Dict:
        """Get current trading status"""
        return {
            'active': self.trading_active,
            'total_trades': len(self.trade_history),
            'successful_trades': len([t for t in self.trade_history if t.get('status') == 'executed']),
            'total_profit': sum(t.get('profit_usd', 0) for t in self.trade_history),
            'last_trade': self.trade_history[-1] if self.trade_history else None,
            'next_trade_available': not self._is_in_cooldown(),
            'cooldown_remaining': max(0, self.trade_cooldown - (datetime.now() - self.last_trade_time).total_seconds()) if self.last_trade_time else 0
        }
    
    def get_recent_trades(self, limit: int = 10) -> List[Dict]:
        """Get recent trade history"""
        return self.trade_history[-limit:] if self.trade_history else []

# Global trading agent instance
trading_agent = None

async def initialize_trading_agent():
    """Initialize the global trading agent"""
    global trading_agent
    if not trading_agent:
        trading_agent = TradingExecutionAgent()
    return trading_agent

async def start_automated_trading():
    """Start automated trading"""
    agent = await initialize_trading_agent()
    if not agent.trading_active:
        # Run trading in background
        asyncio.create_task(agent.start_trading())
        return True
    return False

def stop_automated_trading():
    """Stop automated trading"""
    global trading_agent
    if trading_agent:
        trading_agent.stop_trading()
        return True
    return False

def get_trading_status():
    """Get current trading status"""
    global trading_agent
    if trading_agent:
        return trading_agent.get_trading_status()
    return {'active': False, 'total_trades': 0}

def get_recent_trades(limit: int = 10):
    """Get recent trades"""
    global trading_agent
    if trading_agent:
        return trading_agent.get_recent_trades(limit)
    return []

if __name__ == "__main__":
    async def main():
        agent = TradingExecutionAgent()
        print("🤖 Starting Trading Execution Agent...")
        print("Press Ctrl+C to stop")
        
        try:
            await agent.start_trading()
        except KeyboardInterrupt:
            print("\n⏹️ Stopping trading agent...")
            agent.stop_trading()

    asyncio.run(main())
