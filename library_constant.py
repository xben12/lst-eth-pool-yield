
API_WAIT_NEXT_CALL = 1.5 #seconds

# related token address. note that they may just implement part of ERC20 interfaces
STETH_ADDR = '0xae7ab96520DE3A18E5e111B5EaAb095312D7fE84'
ERC20_STE_CURVE = '0x06325440D014e39736583c165C2963BA99fAf14E'
ERC20_WETH = '0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2'
TOKEN_SWETH = '0xf951E335afb289353dc249e82926178EaC7DEd78'

# pool address
CURVE_POOL_STETH_ETH = '0xDC24316b9AE028F1497c275EB9192a3Ea0f67022'
MAV_POOL_ETH_SWETH = '0x0CE176E1b11A8f88a4Ba2535De80E81F88592bad'



ERC20_ABI = [
    {
        "constant": True,
        "inputs": [{"name": "_owner", "type": "address"}],
        "name": "balanceOf",
        "outputs": [{"name": "balance", "type": "uint256"}],
        "payable": False,
        "stateMutability": "view",
        "type": "function",
    },
    {
        "constant": True,
        "inputs": [],
        "name": "totalSupply",
        "outputs": [{"name": "totalSupply", "type": "uint256"}],
        "payable": False,
        "stateMutability": "view",
        "type": "function",
    }
]
