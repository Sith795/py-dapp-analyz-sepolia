from web3 import Web3
import requests
import json
import matplotlib.pyplot as plt
from time import sleep
from datetime import datetime

# Налаштування підключення до Ethereum
INFURA_URL = "https://mainnet.infura.io/v3/ab2a211f892746eaac884debeb26ca32"  # Замініть на ваш Infura Project ID
INFURA_WS_URL = "wss://mainnet.infura.io/ws/v3/ab2a211f892746eaac884debeb26ca32"  # WebSocket URL
ETHERSCAN_API_KEY = "ab2a211f892746eaac884debeb26ca32"  # Замініть на ваш Etherscan API ключ
web3 = Web3(Web3.HTTPProvider(INFURA_URL))

# Перевірка підключення
if not web3.is_connected():
    raise Exception("Не вдалося підключитися до мережі Ethereum")

# Адреса гаманця для аналізу
wallet_address = "0x96FeF57e0dB8fEB445Af555a9A4768e1dB142946"  # Замініть на потрібну адресу

# ABI для ERC-20 токенів (спрощений)
ERC20_ABI = json.loads('''
[
    {"constant":true,"inputs":[{"name":"_owner","type":"address"}],"name":"balanceOf","outputs":[{"name":"balance","type":"uint256"}],"type":"function"}
]
''')

# Популярні токени ERC-20 (адреси контрактів)
TOKENS = {
    "USDT": "0xdAC17F958D2ee523a2206206994597C13D831ec7",
    "USDC": "0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48",
    "DAI": "0x6B175474E89094C44Da98b954EedeAC495271d0F"
}


# Функція для отримання балансу ETH
def get_eth_balance(address):
    try:
        balance = web3.eth.get_balance(address)
        return web3.from_wei(balance, 'ether')
    except Exception as e:
        return f"Помилка при отриманні балансу ETH: {e}"


# Функція для отримання балансів ERC-20 токенів
def get_erc20_balances(address, tokens):
    balances = {}
    for token_name, token_address in tokens.items():
        try:
            contract = web3.eth.contract(address=token_address, abi=ERC20_ABI)
            balance = contract.functions.balanceOf(address).call()
            balances[token_name] = balance / 10 ** 6  # Припускаємо 6 знаків для USDT/USDC/DAI
        except Exception as e:
            balances[token_name] = f"Помилка: {e}"
    return balances


# Функція для отримання останніх транзакцій через Etherscan
def get_transactions(address, api_key):
    etherscan_url = f"https://api.etherscan.io/api?module=account&action=txlist&address={address}&sort=desc&apikey={api_key}"
    try:
        response = requests.get(etherscan_url)
        data = response.json()
        if data['status'] == '1':
            return data['result'][:5]  # Останні 5 транзакцій
        else:
            return f"Помилка Etherscan: {data['message']}"
    except Exception as e:
        return f"Помилка при отриманні транзакцій: {e}"


# Функція для перевірки, чи є адреса смарт-контрактом
def is_contract(address):
    try:
        code = web3.eth.get_code(address)
        return len(code) > 0  # Якщо є байт-код, це контракт
    except Exception as e:
        return f"Помилка при перевірці контракту: {e}"


# Функція для аналізу смарт-контрактів, пов’язаних із гаманцем
def analyze_contracts(address, transactions):
    contracts = set()
    if isinstance(transactions, list):
        for tx in transactions:
            if tx['to'] and is_contract(tx['to']):
                contracts.add(tx['to'])
    return contracts


# Функція для відстеження транзакцій у реальному часі через WebSocket
def track_transactions_realtime(address):
    from websocket import create_connection
    ws = create_connection(INFURA_WS_URL)
    subscription = {
        "id": 1,
        "method": "eth_subscribe",
        "params": ["newPendingTransactions"]
    }
    ws.send(json.dumps(subscription))
    print("Відстеження нових транзакцій у реальному часі (Ctrl+C для зупинки)...")
    try:
        while True:
            result = json.loads(ws.recv())
            if 'params' in result and 'result' in result['params']:
                tx_hash = result['params']['result']
                try:
                    tx = web3.eth.get_transaction(tx_hash)
                    if tx['from'].lower() == address.lower() or tx['to'].lower() == address.lower():
                        print(f"\nНова транзакція: {tx_hash}")
                        print(f"Від: {tx['from']}")
                        print(f"До: {tx['to']}")
                        print(f"Сума: {web3.from_wei(tx['value'], 'ether')} ETH")
                except Exception:
                    continue
    except KeyboardInterrupt:
        ws.close()
        print("Відстеження зупинено.")


# Функція для візуалізації даних
def visualize_data(eth_balance, erc20_balances, transactions):
    # Графік балансів
    plt.figure(figsize=(10, 5))

    # Баланс ETH + ERC-20
    labels = ['ETH'] + list(erc20_balances.keys())
    balances = [eth_balance] + [b for b in erc20_balances.values() if isinstance(b, (int, float))]
    plt.subplot(1, 2, 1)
    plt.bar(labels, balances, color=['blue'] + ['green'] * len(erc20_balances))
    plt.title("Баланси гаманця")
    plt.ylabel("Сума")

    # Графік сум транзакцій
    if isinstance(transactions, list):
        tx_values = [web3.from_wei(int(tx['value']), 'ether') for tx in transactions]
        tx_times = [datetime.fromtimestamp(int(tx['timeStamp'])) for tx in transactions]
        plt.subplot(1, 2, 2)
        plt.plot(tx_times, tx_values, marker='o')
        plt.title("Суми останніх транзакцій")
        plt.xlabel("Час")
        plt.ylabel("Сума (ETH)")
        plt.xticks(rotation=45)

    plt.tight_layout()
    plt.show()


# Основна функція аналізатора
def analyze_wallet(address, etherscan_api_key):
    print(f"\nАналіз гаманця: {address}")

    # Отримання балансу ETH
    eth_balance = get_eth_balance(address)
    print(f"Баланс ETH: {eth_balance} ETH")

    # Отримання балансів ERC-20
    erc20_balances = get_erc20_balances(address, TOKENS)
    print("\nБаланси ERC-20 токенів:")
    for token, balance in erc20_balances.items():
        print(f"{token}: {balance}")

    # Перевірка, чи є адреса контрактом
    contract_status = is_contract(address)
    print(f"\nЧи є адреса смарт-контрактом? {contract_status}")

    # Отримання транзакцій
    transactions = get_transactions(address, etherscan_api_key)
    print("\nОстанні транзакції:")
    if isinstance(transactions, list):
        for tx in transactions:
            print(f"Хеш: {tx['hash']}")
            print(f"Від: {tx['from']}")
            print(f"До: {tx['to']}")
            print(f"Сума: {web3.from_wei(int(tx['value']), 'ether')} ETH")
            print(f"Час: {datetime.fromtimestamp(int(tx['timeStamp']))}")
            print("-" * 50)
    else:
        print(transactions)

    # Аналіз смарт-контрактів у транзакціях
    contracts = analyze_contracts(address, transactions)
    print("\nСмарт-контракти, з якими взаємодіяв гаманець:")
    print(contracts if contracts else "Не знайдено")

    # Візуалізація даних
    print("\nГенерація графіків...")
    visualize_data(eth_balance, erc20_balances, transactions)

    # Відстеження транзакцій у реальному часі
    print("\nЗапуск відстеження транзакцій у реальному часі...")
    track_transactions_realtime(address)


# Запуск аналізатора
if __name__ == "__main__":
    analyze_wallet(wallet_address, ETHERSCAN_API_KEY)