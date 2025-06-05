from web3 import Web3
from dotenv import load_dotenv
import os
import plotly.graph_objects as go


ERC20_TOKENS = [
    {
        "symbol": "WETH",
        "address": "0xdd13E55209Fd76AfE204dBda4007C227904f0a81"
    },
    {
        "symbol": "DAI",
        "address": "0x27b2Fd0fEdfbA4a18B90dB4c746885A712C9057C"
    },
    {
        "symbol": "USDC",
        "address": "0x65aFADD39029741B3b8f0756952C74678c9cEC93"
    }
]


ERC20_ABI = [
    {
        "constant": True,
        "inputs": [{"name": "_owner", "type": "address"}],
        "name": "balanceOf",
        "outputs": [{"name": "balance", "type": "uint256"}],
        "type": "function",
    },
    {
        "constant": True,
        "inputs": [],
        "name": "decimals",
        "outputs": [{"name": "", "type": "uint8"}],
        "type": "function",
    },
]


load_dotenv()
INFURA_URL = os.getenv("INFURA_SEPOLIA_URL")
WALLET_ADDRESS = os.getenv("WALLET_ADDRESS")


web3 = Web3(Web3.HTTPProvider(INFURA_URL))
if not web3.is_connected():
    print("❌ Не вдалося підключитися до Sepolia")
    exit()


eth_balance_wei = web3.eth.get_balance(WALLET_ADDRESS)
eth_balance = float(web3.from_wei(eth_balance_wei, 'ether'))


labels = ["ETH"]
values = [eth_balance]


for token in ERC20_TOKENS:
    token_address = token.get("address")
    symbol = token.get("symbol", "UNKNOWN")


    if not token_address or not web3.is_address(token_address):
        print(f"⚠️ Невірна адреса токена {symbol}: {token_address}")
        continue

    try:
        contract = web3.eth.contract(address=token_address, abi=ERC20_ABI)
        balance = contract.functions.balanceOf(WALLET_ADDRESS).call()
        decimals = contract.functions.decimals().call()
        human_balance = balance / (10 ** decimals)

        labels.append(symbol)
        values.append(human_balance)
    except Exception as e:
        print(f"⚠️ Не вдалося отримати токен {symbol}: {e}")


fig = go.Figure(data=[go.Pie(
    labels=labels,
    values=values,
    hoverinfo='label+percent+value',
    textinfo='label+percent',
    marker=dict(colors=['green', 'yellow', 'orange', 'lightblue', 'pink'])
)])
fig.update_layout(title="Баланс ETH та токенів ERC-20 у Sepolia", height=600)


fig.write_image("eth_token_balance.png")
print("📁 Діаграму збережено у файл: eth_token_balance.png")


fig.show()
