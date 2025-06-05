from web3 import Web3
import requests

INFURA_URL = "https://mainnet.infura.io/v3/ab2a211f892746eaac884debeb26ca32"
web3 = Web3(Web3.HTTPProvider(INFURA_URL))

if not web3.is_connected():
    raise Exception("Не вдалося підключитися до мережі Ethereum")

wallet_address = "0x96FeF57e0dB8fEB445Af555a9A4768e1dB142946"


def get_balance(address):
    try:
        balance = web3.eth.get_balance(address)
        balance_eth = web3.from_wei(balance, 'ether')
        return balance_eth
    except Exception as e:
        return f"Помилка при отриманні балансу: {e}"


def get_transactions(address, api_key):
    etherscan_url = f"https://api.etherscan.io/api?module=account&action=txlist&address={address}&sort=desc&apikey={api_key}"
    try:
        response = requests.get(etherscan_url)
        data = response.json()
        if data['status'] == '1':
            return data['result'][:5]
        else:
            return f"Помилка Etherscan: {data['message']}"
    except Exception as e:
        return f"Помилка при отриманні транзакцій: {e}"


# Основна функція аналізатора
def analyze_wallet(address, etherscan_api_key):
    print(f"Аналіз гаманця: {address}")

    # Отримання балансу
    balance = get_balance(address)
    print(f"Баланс гаманця: {balance} ETH")

    # Отримання транзакцій
    transactions = get_transactions(address, etherscan_api_key)
    print("\nОстанні транзакції:")
    if isinstance(transactions, list):
        for tx in transactions:
            print(f"Хеш: {tx['hash']}")
            print(f"Від: {tx['from']}")
            print(f"До: {tx['to']}")
            print(f"Сума: {web3.from_wei(int(tx['value']), 'ether')} ETH")
            print(f"Час: {tx['timeStamp']}")
            print("-" * 50)
    else:
        print(transactions)


# Запуск аналізатора
if __name__ == "__main__":
    ETHERSCAN_API_KEY = "ab2a211f892746eaac884debeb26ca32"  # Замініть на ваш Etherscan API ключ
    analyze_wallet(wallet_address, ETHERSCAN_API_KEY)