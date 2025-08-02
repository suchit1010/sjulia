"""
Real Wallet Integrations for Cross-Chain Arbitrage Dashboard
Connects to actual Solana wallets, MetaMask (Ethereum), and Binance accounts
"""
import asyncio
import json
import os
from typing import Dict, List, Optional, Any
from decimal import Decimal
import logging
from datetime import datetime
import requests

# Solana imports
try:
    from solana.rpc.async_api import AsyncClient
    from solders.pubkey import Pubkey
    SOLANA_AVAILABLE = True
except ImportError:
    AsyncClient = None
    Pubkey = None
    SOLANA_AVAILABLE = False
    print("⚠️ Solana libraries not available")

# Ethereum/Web3 imports  
try:
    from web3 import Web3
    WEB3_AVAILABLE = True
except ImportError:
    Web3 = None
    WEB3_AVAILABLE = False
    print("⚠️ Web3 libraries not available")

# Binance imports
try:
    from binance.client import Client as BinanceClient
    from binance.exceptions import BinanceAPIException
    BINANCE_AVAILABLE = True
except ImportError:
    BinanceClient = None
    BinanceAPIException = Exception
    BINANCE_AVAILABLE = False
    print("⚠️ Binance libraries not available")

# Price data
try:
    import ccxt
    CCXT_AVAILABLE = True
except ImportError:
    ccxt = None
    CCXT_AVAILABLE = False
    print("⚠️ CCXT libraries not available")

try:
    import aiohttp
    AIOHTTP_AVAILABLE = True
except ImportError:
    aiohttp = None
    AIOHTTP_AVAILABLE = False
    print("⚠️ Aiohttp not available")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class RealWalletManager:
    """Manages real wallet connections and portfolio data"""
    
    def __init__(self):
        self.solana_client = None
        self.ethereum_client = None
        self.binance_client = None
        self.ccxt_exchanges = {}
        
        # Load configuration from environment or config file
        self.load_config()
        
    def load_config(self):
        """Load wallet configuration from environment variables or config file"""
        try:
            # Try to load from .env file first
            if os.path.exists('.env'):
                from dotenv import load_dotenv
                load_dotenv()
            
            # Solana configuration
            self.solana_rpc_url = os.getenv('SOLANA_RPC_URL', 'https://api.mainnet-beta.solana.com')
            self.solana_wallet_address = os.getenv('SOLANA_WALLET_ADDRESS')
            
            # Ethereum configuration
            self.ethereum_rpc_url = os.getenv('ETHEREUM_RPC_URL', 'https://eth-mainnet.g.alchemy.com/v2/your-api-key')
            self.ethereum_wallet_address = os.getenv('ETHEREUM_WALLET_ADDRESS')
            
            # Binance configuration
            self.binance_api_key = os.getenv('BINANCE_API_KEY')
            self.binance_api_secret = os.getenv('BINANCE_API_SECRET')
            
            logger.info("Configuration loaded successfully")
            
        except Exception as e:
            logger.error(f"Error loading configuration: {e}")
    
    async def initialize_clients(self):
        """Initialize all wallet clients"""
        try:
            # Initialize Solana client
            if SOLANA_AVAILABLE and self.solana_wallet_address:
                self.solana_client = AsyncClient(self.solana_rpc_url)
                logger.info("Solana client initialized")
            elif self.solana_wallet_address:
                logger.warning("Solana wallet configured but library not available")
            
            # Initialize Ethereum client
            if WEB3_AVAILABLE and self.ethereum_wallet_address and self.ethereum_rpc_url:
                self.ethereum_client = Web3(Web3.HTTPProvider(self.ethereum_rpc_url))
                if self.ethereum_client.is_connected():
                    logger.info("Ethereum client connected")
                else:
                    logger.warning("Ethereum client connection failed")
            elif self.ethereum_wallet_address:
                logger.warning("Ethereum wallet configured but library not available")
            
            # Initialize Binance client
            if BINANCE_AVAILABLE and self.binance_api_key and self.binance_api_secret:
                self.binance_client = BinanceClient(
                    api_key=self.binance_api_key,
                    api_secret=self.binance_api_secret
                )
                # Test connection
                account_info = self.binance_client.get_account()
                logger.info("Binance client initialized successfully")
            elif self.binance_api_key:
                logger.warning("Binance API keys configured but library not available")
            
            # Initialize CCXT exchanges for price data
            if CCXT_AVAILABLE:
                self.ccxt_exchanges = {
                    'binance': ccxt.binance(),
                    'kraken': ccxt.kraken(),
                }
                # Note: coinbasepro is deprecated, using coinbase instead
                try:
                    self.ccxt_exchanges['coinbase'] = ccxt.coinbase()
                except AttributeError:
                    logger.info("Coinbase exchange not available in this CCXT version")
            
            logger.info("All available wallet clients initialized")
            
        except Exception as e:
            logger.error(f"Error initializing clients: {e}")
    
    async def get_solana_portfolio(self) -> Dict[str, Any]:
        """Get real Solana wallet portfolio"""
        try:
            if not SOLANA_AVAILABLE or not self.solana_client or not self.solana_wallet_address:
                return {"error": "Solana wallet not configured or library not available"}
            
            # Convert string address to PublicKey
            wallet_pubkey = Pubkey.from_string(self.solana_wallet_address)
            
            # Get SOL balance
            sol_balance_response = await self.solana_client.get_balance(wallet_pubkey)
            sol_balance = sol_balance_response.value / 1e9  # Convert lamports to SOL
            
            # Get token accounts (SPL tokens)
            token_accounts_response = await self.solana_client.get_token_accounts_by_owner(
                wallet_pubkey,
                {"programId": Pubkey.from_string("TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA")}
            )
            
            tokens = []
            total_usd_value = 0
            
            # Get SOL price
            sol_price = await self.get_token_price("SOL")
            sol_usd_value = sol_balance * sol_price
            total_usd_value += sol_usd_value
            
            portfolio = {
                "sol_balance": sol_balance,
                "sol_price": sol_price,
                "sol_usd_value": sol_usd_value,
                "tokens": tokens,
                "total_usd_value": total_usd_value,
                "last_updated": datetime.now().isoformat()
            }
            
            # Process token accounts
            if token_accounts_response.value:
                for token_account in token_accounts_response.value:
                    try:
                        token_info = await self.solana_client.get_token_account_balance(
                            Pubkey.from_string(str(token_account.pubkey))
                        )
                        
                        if token_info.value.ui_amount and token_info.value.ui_amount > 0:
                            mint_address = token_account.account.data.parsed["info"]["mint"]
                            
                            # Get token metadata if available
                            token_data = {
                                "mint": mint_address,
                                "balance": token_info.value.ui_amount,
                                "decimals": token_info.value.decimals
                            }
                            
                            tokens.append(token_data)
                    
                    except Exception as e:
                        logger.warning(f"Error processing token account: {e}")
            
            return portfolio
            
        except Exception as e:
            logger.error(f"Error getting Solana portfolio: {e}")
            return {"error": str(e)}
    
    async def get_ethereum_portfolio(self) -> Dict[str, Any]:
        """Get real Ethereum wallet portfolio"""
        try:
            if not self.ethereum_client or not self.ethereum_wallet_address:
                return {"error": "Ethereum wallet not configured"}
            
            # Check if address is valid
            if not Web3.is_address(self.ethereum_wallet_address):
                return {"error": "Invalid Ethereum address"}
            
            # Get ETH balance
            eth_balance_wei = self.ethereum_client.eth.get_balance(self.ethereum_wallet_address)
            eth_balance = Web3.from_wei(eth_balance_wei, 'ether')
            
            # Get ETH price
            eth_price = await self.get_token_price("ETH")
            eth_usd_value = float(eth_balance) * eth_price
            
            # ERC-20 token balances (common tokens)
            erc20_tokens = await self.get_erc20_balances(self.ethereum_wallet_address)
            
            total_usd_value = eth_usd_value
            for token in erc20_tokens:
                total_usd_value += token.get('usd_value', 0)
            
            portfolio = {
                "eth_balance": float(eth_balance),
                "eth_price": eth_price,
                "eth_usd_value": eth_usd_value,
                "erc20_tokens": erc20_tokens,
                "total_usd_value": total_usd_value,
                "last_updated": datetime.now().isoformat()
            }
            
            return portfolio
            
        except Exception as e:
            logger.error(f"Error getting Ethereum portfolio: {e}")
            return {"error": str(e)}
    
    async def get_erc20_balances(self, wallet_address: str) -> List[Dict]:
        """Get ERC-20 token balances for Ethereum wallet"""
        tokens = []
        
        # Common ERC-20 token contracts
        token_contracts = {
            "USDC": "0xA0b86a33E6441B8C942E8a20E08E30E54bA42ceA",
            "USDT": "0xdAC17F958D2ee523a2206206994597C13D831ec7",
            "DAI": "0x6B175474E89094C44Da98b954EedeAC495271d0F",
            "WETH": "0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2"
        }
        
        # Standard ERC-20 ABI for balanceOf function
        erc20_abi = [
            {
                "constant": True,
                "inputs": [{"name": "_owner", "type": "address"}],
                "name": "balanceOf",
                "outputs": [{"name": "balance", "type": "uint256"}],
                "type": "function"
            },
            {
                "constant": True,
                "inputs": [],
                "name": "decimals",
                "outputs": [{"name": "", "type": "uint8"}],
                "type": "function"
            }
        ]
        
        try:
            for token_name, contract_address in token_contracts.items():
                try:
                    contract = self.ethereum_client.eth.contract(
                        address=Web3.to_checksum_address(contract_address),
                        abi=erc20_abi
                    )
                    
                    balance = contract.functions.balanceOf(wallet_address).call()
                    decimals = contract.functions.decimals().call()
                    
                    if balance > 0:
                        token_balance = balance / (10 ** decimals)
                        token_price = await self.get_token_price(token_name)
                        usd_value = token_balance * token_price
                        
                        tokens.append({
                            "name": token_name,
                            "contract": contract_address,
                            "balance": token_balance,
                            "price": token_price,
                            "usd_value": usd_value
                        })
                
                except Exception as e:
                    logger.warning(f"Error getting {token_name} balance: {e}")
            
        except Exception as e:
            logger.error(f"Error getting ERC-20 balances: {e}")
        
        return tokens
    
    async def get_binance_portfolio(self) -> Dict[str, Any]:
        """Get real Binance account portfolio"""
        try:
            if not self.binance_client:
                return {"error": "Binance client not configured"}
            
            # Get account information
            account_info = self.binance_client.get_account()
            
            balances = []
            total_btc_value = 0
            total_usd_value = 0
            
            # Get all non-zero balances
            for balance in account_info['balances']:
                free = float(balance['free'])
                locked = float(balance['locked'])
                total = free + locked
                
                if total > 0:
                    asset = balance['asset']
                    
                    # Get price in BTC and USD
                    try:
                        if asset == 'BTC':
                            btc_value = total
                            usd_price = await self.get_token_price('BTC')
                            usd_value = total * usd_price
                        elif asset == 'USDT' or asset == 'USDC':
                            btc_price = await self.get_token_price('BTC')
                            btc_value = total / btc_price
                            usd_value = total
                        else:
                            # Try to get price from Binance
                            try:
                                ticker = self.binance_client.get_symbol_ticker(symbol=f"{asset}USDT")
                                usd_price = float(ticker['price'])
                                usd_value = total * usd_price
                                btc_price = await self.get_token_price('BTC')
                                btc_value = usd_value / btc_price
                            except:
                                try:
                                    ticker = self.binance_client.get_symbol_ticker(symbol=f"{asset}BTC")
                                    btc_price = float(ticker['price'])
                                    btc_value = total * btc_price
                                    usd_btc_price = await self.get_token_price('BTC')
                                    usd_value = btc_value * usd_btc_price
                                except:
                                    btc_value = 0
                                    usd_value = 0
                        
                        if usd_value > 1:  # Only include assets worth more than $1
                            balances.append({
                                "asset": asset,
                                "free": free,
                                "locked": locked,
                                "total": total,
                                "btc_value": btc_value,
                                "usd_value": usd_value
                            })
                            
                            total_btc_value += btc_value
                            total_usd_value += usd_value
                    
                    except Exception as e:
                        logger.warning(f"Error processing {asset}: {e}")
            
            portfolio = {
                "balances": balances,
                "total_btc_value": total_btc_value,
                "total_usd_value": total_usd_value,
                "account_type": account_info.get('accountType', 'SPOT'),
                "last_updated": datetime.now().isoformat()
            }
            
            return portfolio
            
        except BinanceAPIException as e:
            logger.error(f"Binance API error: {e}")
            return {"error": f"Binance API error: {e.message}"}
        except Exception as e:
            logger.error(f"Error getting Binance portfolio: {e}")
            return {"error": str(e)}
    
    async def get_token_price(self, symbol: str) -> float:
        """Get real-time token price from multiple exchanges"""
        try:
            # Try different exchanges for price data
            for exchange_name, exchange in self.ccxt_exchanges.items():
                try:
                    if symbol == "SOL":
                        ticker = exchange.fetch_ticker('SOL/USDT')
                    elif symbol == "ETH":
                        ticker = exchange.fetch_ticker('ETH/USDT')
                    elif symbol == "BTC":
                        ticker = exchange.fetch_ticker('BTC/USDT')
                    else:
                        ticker = exchange.fetch_ticker(f'{symbol}/USDT')
                    
                    return float(ticker['last'])
                
                except Exception as e:
                    logger.warning(f"Error getting price from {exchange_name}: {e}")
                    continue
            
            # Fallback to CoinGecko API
            async with aiohttp.ClientSession() as session:
                symbol_map = {
                    'SOL': 'solana',
                    'ETH': 'ethereum', 
                    'BTC': 'bitcoin',
                    'USDC': 'usd-coin',
                    'USDT': 'tether',
                    'DAI': 'dai'
                }
                
                coin_id = symbol_map.get(symbol, symbol.lower())
                url = f"https://api.coingecko.com/api/v3/simple/price?ids={coin_id}&vs_currencies=usd"
                
                async with session.get(url) as response:
                    data = await response.json()
                    return float(data[coin_id]['usd'])
        
        except Exception as e:
            logger.error(f"Error getting price for {symbol}: {e}")
            return 0.0
    
    async def get_comprehensive_portfolio(self) -> Dict[str, Any]:
        """Get portfolio data from all connected wallets"""
        portfolio_data = {
            "solana": None,
            "ethereum": None,
            "binance": None,
            "total_usd_value": 0,
            "last_updated": datetime.now().isoformat(),
            "errors": []
        }
        
        # Get Solana portfolio
        if self.solana_wallet_address:
            try:
                solana_data = await self.get_solana_portfolio()
                if "error" not in solana_data:
                    portfolio_data["solana"] = solana_data
                    portfolio_data["total_usd_value"] += solana_data.get("total_usd_value", 0)
                else:
                    portfolio_data["errors"].append(f"Solana: {solana_data['error']}")
            except Exception as e:
                portfolio_data["errors"].append(f"Solana: {str(e)}")
        
        # Get Ethereum portfolio
        if self.ethereum_wallet_address:
            try:
                ethereum_data = await self.get_ethereum_portfolio()
                if "error" not in ethereum_data:
                    portfolio_data["ethereum"] = ethereum_data
                    portfolio_data["total_usd_value"] += ethereum_data.get("total_usd_value", 0)
                else:
                    portfolio_data["errors"].append(f"Ethereum: {ethereum_data['error']}")
            except Exception as e:
                portfolio_data["errors"].append(f"Ethereum: {str(e)}")
        
        # Get Binance portfolio
        if self.binance_api_key and self.binance_api_secret:
            try:
                binance_data = await self.get_binance_portfolio()
                if "error" not in binance_data:
                    portfolio_data["binance"] = binance_data
                    portfolio_data["total_usd_value"] += binance_data.get("total_usd_value", 0)
                else:
                    portfolio_data["errors"].append(f"Binance: {binance_data['error']}")
            except Exception as e:
                portfolio_data["errors"].append(f"Binance: {str(e)}")
        
        return portfolio_data

# Global wallet manager instance
wallet_manager = RealWalletManager()
