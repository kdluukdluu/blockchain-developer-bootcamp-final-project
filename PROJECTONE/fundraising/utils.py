from web3 import Web3
from solcx import compile_standard
import json
from django.conf import settings

# setting the provider
provider = settings.PROVIDER
web3 = Web3(Web3.HTTPProvider(provider))
chain_id = settings.CHAIN_ID

# public and private key for admin
my_address = settings.MY_PUBLIC_KEY
private_key = settings.MY_PRIVATE_KEY
nonce = web3.eth.getTransactionCount(my_address)

# compiling the contract to extract bytecode and abi - this is running only at launch
with open(
    "fundraising\\contracts\\Fundraising.sol",
    "r",
) as file:
    fundraising_file = file.read()

compiled_sol = compile_standard(
    {
        "language": "Solidity",
        "sources": {"Fundraising.sol": {"content": fundraising_file}},
        "settings": {
            "outputSelection": {
                "*": {"*": ["abi", "metadata", "evm.bytecode", "evm.sourceMap"]}
            }
        },
    },
    solc_version="0.8.0",
)

with open("compiled_code.json", "w") as file:
    json.dump(compiled_sol, file)

bytecode = compiled_sol["contracts"]["Fundraising.sol"]["Fundraising"]["evm"][
    "bytecode"
]["object"]

abi = compiled_sol["contracts"]["Fundraising.sol"]["Fundraising"]["abi"]


def getBalance(contractAddress):
    address = contractAddress
    project_contract = web3.eth.contract(abi=abi, address=address)
    balance = project_contract.functions.getBalance().call()
    return balance

def getRaisedAmount(contractAddress):
    address = contractAddress
    project_contract = web3.eth.contract(abi=abi, address=address)
    raised_amount = project_contract.functions.getRaisedAmount().call()
    return raised_amount    

def getNumberOfVoters(contractAddress, requestNo):
    address = contractAddress
    project_contract = web3.eth.contract(abi=abi, address=address)
    NumberOfVoters = project_contract.functions.getRequestInfo(requestNo).call()
    return NumberOfVoters[4]

def getNumberOfDonors(contractAddress):
    address = contractAddress
    project_contract = web3.eth.contract(abi=abi, address=address)
    numberOfDonors = project_contract.functions.numberOfDonors().call()
    return numberOfDonors

