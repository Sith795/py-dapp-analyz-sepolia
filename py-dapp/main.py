import json
import os
from dotenv import load_dotenv
from web3 import Web3
import plotly.express as px

load_dotenv()
INFURA_URL = os.getenv("INFURA_URL")
CONTRACT_ADDRESS = "0x3d41a2CAFd48ea81c80e2C8532B925aE859FE081"


web3 = Web3(Web3.HTTPProvider(INFURA_URL))
if not web3.is_connected():
    raise Exception("Не вдалося підключитися до Ethereum мережі")


with open("abi/MyContract.json") as f:
    abi = json.load(f)

contract = web3.eth.contract(address=CONTRACT_ADDRESS, abi=abi)


value = contract.functions.getValue().call()
print(f"Значення value у контракті: {value}")


labels = ['value', 'Інше']

val_for_chart = min(value, 100)
values = [val_for_chart, max(0, 100 - val_for_chart)]

fig = px.pie(
    names=labels,
    values=values,
    title=f"Значення value у контракті",
    color_discrete_sequence=["green", "gold"]
)
fig.update_traces(textinfo='percent+label', pull=[0.1, 0])
fig.write_image("value_chart.png", engine="kaleido")
fig.show()
