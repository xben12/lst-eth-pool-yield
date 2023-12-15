import os
from dotenv import load_dotenv
from web3 import Web3
from alchemy import Alchemy, Network
from datetime import datetime, timedelta
import time
import pandas as pd
import numpy as np
import requests


import library_constant as CONST 


def get_web3_provider():
    load_dotenv()
    default_provider_url = "https://eth-mainnet.g.alchemy.com/v2/_gg7wSSi0KMBsdKnGVfHDueq6xMB9EkC"
    alchemy_api_key = os.getenv('ALCHEMY_API_KEY', "need to provide your alchemy key!")

    w3 = Web3(Web3.HTTPProvider(os.getenv('PROVIDER_URL', default_provider_url)))
    return w3, alchemy_api_key

def get_block_number_from_date(date_yyyymmdd):
    base_block = 18759246 # at date 20231211
    base_formatted_date = datetime.strptime("20231211", '%Y%m%d')
    target_formatted_date = datetime.strptime(date_yyyymmdd, '%Y%m%d')
    time_difference = target_formatted_date - base_formatted_date

    return base_block+time_difference.days*get_eth_blocks_per_day()

import math

def get_date_from_block_number(block_number):
    base_block = 18759246 # at date 20231211
    base_formatted_date = datetime.strptime("20231211", '%Y%m%d')

    days = (block_number - base_block)/get_eth_blocks_per_day();
    days = math.ceil(days)
    new_datetime = base_formatted_date + timedelta(days=days)
    return new_datetime.strftime("%Y%m%d")

def get_eth_blocks_per_day():
    return 7140


def get_date_and_blocknumber(start_date_str= "20230812", end_date_str= "20231211"):

    # Convert start and end dates to datetime objects
    start_date = datetime.strptime(start_date_str, "%Y%m%d")
    end_date = datetime.strptime(end_date_str, "%Y%m%d")

    # Generate an array of string dates without a loop
    date_array = [(start_date + timedelta(days=i)).strftime("%Y%m%d") for i in range((end_date - start_date).days + 1)]
    date_array.reverse()
    blocknumber_array = [get_block_number_from_date(str_date) for str_date in date_array]
    df = pd.DataFrame(data = date_array, columns=["date_yyyymmdd"])
    df["block_number"] = blocknumber_array
    return df


def get_eth_balance_in_blocks(w3, wallet_addr, block_list = ["latest"]):  
    result_array = []
    for block_num in block_list:
        token_balance = w3.eth.get_balance(wallet_addr,block_num)
        result_array = np.append(result_array, token_balance/1e18)
        time.sleep(CONST.API_WAIT_NEXT_CALL) # wait for next API call

    df=pd.DataFrame(data = block_list, columns=["block_number"])
    df['eth_balance'] = result_array
    df.to_csv("output/eth_balanceof_wallet_"+wallet_addr+".csv",index=False)
    return df


def get_balanceof_in_blocks(w3, wallet_addr, token_erc20_addr, block_list = ["latest"]):
    token_contract = w3.eth.contract(address=token_erc20_addr, abi=CONST.ERC20_ABI)

    result_array = []
    for block_num in block_list:
        token_balance = token_contract.functions.balanceOf(wallet_addr).call({},block_num)
        result_array = np.append(result_array, token_balance/1e18)
        time.sleep(CONST.API_WAIT_NEXT_CALL) # wait for next API call

    df=pd.DataFrame(data = block_list, columns=["block_number"])
    df['token_balance'] = result_array
    df.to_csv("output/balanceof_wallet_"+wallet_addr+"erc20_"+token_erc20_addr+".csv",index=False)
    return df


def get_totalsupply_in_blocks(w3, token_erc20_addr, block_list = ["latest"]):
    token_contract = w3.eth.contract(address=token_erc20_addr, abi=CONST.ERC20_ABI)

    result_array = []
    for block_num in block_list:
        total_supply = token_contract.functions.totalSupply().call({},block_num)
        result_array = np.append(result_array, total_supply/1e18)
        time.sleep(CONST.API_WAIT_NEXT_CALL) # wait for next API call

    df=pd.DataFrame(data = block_list, columns=["block_number"])
    df['token_totalsupply'] = result_array
    df.to_csv("output/totalsupply_erc20_"+token_erc20_addr+".csv",index=False)
    return df


def get_hist_daily_crypto_price(token_name, token, start_date_yyyymmdd, end_date_yyyymmdd,  vs_currency='usd'):
    start_date = datetime.strptime(start_date_yyyymmdd, "%Y%m%d")
    end_date = datetime.strptime(end_date_yyyymmdd, "%Y%m%d")
    days_btw = (end_date - start_date).days+10 # get a few more days and later fitler out

    url = f"https://api.coingecko.com/api/v3/coins/{token_name}/market_chart"
    params = {
        'vs_currency': vs_currency,
        'from': int(start_date.timestamp()),
        'to': int(end_date.timestamp()),
        'interval': 'daily',
        'days': days_btw
    }

    response = requests.get(url, params=params)
    if(response.status_code != 200) : # error of request
        print(f"Error: {response.status_code}")
        print(response.text)
        return None
    
    data = response.json()
    prices = data.get('prices', [])

    df = pd.DataFrame(columns=['date', 'date_yyyymmdd', 'token', 'vs_currency', 'close_price'])
    for price in prices:
        timestamp, value = price
        dt_object = datetime.utcfromtimestamp(timestamp / 1000)
        date_str = dt_object.strftime('%Y%m%d')
        df.loc[len(df)] = [date_str,date_str, token.upper(), vs_currency, value]

    df.set_index('date', inplace=True)
    df.sort_values(by='date_yyyymmdd', ascending=False, inplace=True)

    # Remove duplicates by taking the last value for each date
    df = df[~df.index.duplicated(keep='last')]
    df = df[(df.index>= start_date_yyyymmdd) & (df.index<= end_date_yyyymmdd)]
    df.to_csv("output/price_"+token+"_vs_"+vs_currency+".csv",index=False)
    return df


def get_curve_steth_pool_daily_data(start_date_str= "20230801", end_date_str= "20231211"):
    df_dateblock = get_date_and_blocknumber(start_date_str, end_date_str )
    df_dateblock.set_index("block_number", inplace=True)

    file_pool_eth_qty = "output/eth_balanceof_wallet_0xDC24316b9AE028F1497c275EB9192a3Ea0f67022.csv"
    df_eth_qty = pd.read_csv(file_pool_eth_qty)
    df_eth_qty.set_index("block_number", inplace=True)

    file_pool_steth_qty = "output/balanceof_wallet_0xDC24316b9AE028F1497c275EB9192a3Ea0f67022erc20_0xae7ab96520DE3A18E5e111B5EaAb095312D7fE84.csv"
    df_steth_qty = pd.read_csv(file_pool_steth_qty)
    df_steth_qty.set_index("block_number", inplace=True)

    file_lp_token_supply = "output/totalsupply_erc20_0x06325440D014e39736583c165C2963BA99fAf14E.csv"
    df_lp_token_supply = pd.read_csv(file_lp_token_supply)
    df_lp_token_supply.set_index("block_number", inplace=True)

    df_block = pd.concat([df_dateblock, df_eth_qty, df_steth_qty, df_lp_token_supply], axis=1)
    df_block = df_block.reset_index()

    # now concatenate with price
    file_price_steth = "output/price_STETH_vs_eth.csv"
    df_price = pd.read_csv(file_price_steth)
    df_price['date_yyyymmdd'] = df_price['date_yyyymmdd'].astype(str)

    df = pd.merge(df_block, df_price, on='date_yyyymmdd')

    df['tvl'] = df['eth_balance'] + df['token_balance']*df['close_price']
    df['lp_token_price'] = df['tvl']/df['token_totalsupply']
    return df



def hexstr2int(x):
    return int( x, 16)

def get_df_asset_transfer_from_alchemy_result(alchemy_result, col_name_prefix = None):
    df = pd.DataFrame(alchemy_result) 
    expanded_df = df['raw_contract'].apply(pd.Series)

    df['block_number'] = df['block_num'].apply(hexstr2int)
    df['date_yyyymmdd'] =  df['block_number'].apply(get_date_from_block_number)  
    df['hex_value'] = expanded_df['value'].apply(hexstr2int) 
    df['decimal'] = expanded_df['decimal'].apply(hexstr2int)
    df['asset_amt'] =  df['hex_value']/ 10**df['decimal']

    columns = ['block_number', 'date_yyyymmdd', 'hash', 'frm', 'to', 'value', 'asset', 'asset_amt'] #, 'hex_value', 'decimal'
    df = df[columns]

    if(col_name_prefix is not None) :
        col_name_before_chg = ['frm', 'to', 'value', 'asset', 'asset_amt']
        col_name_after_chg = list(map(lambda x: col_name_prefix + x, col_name_before_chg))
        name_chg = dict(zip(col_name_before_chg, col_name_after_chg))
        df.rename(columns=name_chg, inplace=True)

    return df


def get_contract_token_transfer_by_alchemy(contract_addr, date_end_str, date_begin_str, b_direction_to = True, alchemy = None, tx_category = ["erc20"]):

    if(alchemy is None):
        w3, alchemy_api_key = get_web3_provider()
        alchemy = Alchemy(alchemy_api_key, Network.ETH_MAINNET, max_retries=3)


    block_begin = get_block_number_from_date(date_begin_str)
    block_end = get_block_number_from_date(date_end_str)

    direct_prefix = ""
    block_now = block_begin

    df_list =list()

    while block_now <= block_end:
        time.sleep(CONST.API_WAIT_NEXT_CALL)
        cur_block_end = min(block_end, block_now+get_eth_blocks_per_day() )
        if(b_direction_to):
            result_data = alchemy.core.get_asset_transfers(
                category = tx_category, # [ "erc20"],
                from_block = block_now,
                to_block= cur_block_end, #"latest"
                to_address= contract_addr
                ) 
            direct_prefix = 'in_leg_'
        else: 
            result_data = alchemy.core.get_asset_transfers(
            category = tx_category, # [ "erc20"], # "external", "internal",
            from_block = block_now,
            to_block= cur_block_end, #"latest"
            from_address=contract_addr
            ) 
            direct_prefix = 'out_leg_'

        df_now =  get_df_asset_transfer_from_alchemy_result(result_data['transfers'], direct_prefix)
        df_list.append(df_now)
        block_now = cur_block_end+1
    
    df = pd.concat(df_list)
    if(len(tx_category) ==1 and tx_category[0] == "erc20" ):
        file_csv = "output/token_txs_" + direct_prefix + "_" + contract_addr + ".csv"
    else:
        # tx_category = ["external", "internal"]
        name_addon = "_".join(tx_category)
        file_csv = "output/token_txs_" +name_addon + direct_prefix + "_" + contract_addr + ".csv"

    df.to_csv(file_csv)
    return df





if __name__ == '__main__':
    print("\ntest get_block_number_from_date---")
    print('block of 20230912 (should be ~18116543-7140*30) : --> ', get_block_number_from_date('20230912') )
    
    print("\ntest get_date_and_blocknumber---")
    df_dateblock = get_date_and_blocknumber(start_date_str= "20230801", end_date_str= "20231211" )
    print(df_dateblock)

    print("\ntest get w3")
    w3, alchemy_key = get_web3_provider()

    print("\ntest get_balanceof_in_blocks---")
    wallet_addr = CONST.CURVE_POOL_STETH_ETH
    token_erc20_addr = CONST.STETH_ADDR
    block_list = df_dateblock['block_number'].tolist()
    print("the results have been saved into CSV")
    # df_curvep_steth_balance=get_balanceof_in_blocks(w3, wallet_addr, token_erc20_addr, block_list)
    # print(df_curvep_steth_balance)

    print("\ntest get_balanceof_in_blocks---")
    wallet_addr = CONST.MAV_POOL_ETH_SWETH
    token_erc20_addr = CONST.ERC20_WETH
    block_list = df_dateblock['block_number'].tolist()
    print("the results have been saved into CSV")
    df_token_balance=get_balanceof_in_blocks(w3, wallet_addr, token_erc20_addr, block_list)
    # print(df_curvep_steth_balance)

    print("\ntest get_balanceof_in_blocks---")
    wallet_addr = CONST.MAV_POOL_ETH_SWETH
    token_erc20_addr = CONST.TOKEN_SWETH
    block_list = df_dateblock['block_number'].tolist()
    print("the results have been saved into CSV")
    df_token_balance=get_balanceof_in_blocks(w3, wallet_addr, token_erc20_addr, block_list)
    # print(df_curvep_steth_balance)


    print("\ntest get_eth_balance_in_blocks---")
    wallet_addr = CONST.CURVE_POOL_STETH_ETH
    block_list =  df_dateblock['block_number'].tolist() # [18116543, 18116543-7140*30] #
    print("the results have been saved into CSV")
    #df_curvep_eth_balance=get_eth_balance_in_blocks(w3, wallet_addr, block_list)
    #print(df_curvep_eth_balance)

    print("\ntest get_totalsupply_in_blocks---")
    token_steCRV = CONST.ERC20_STE_CURVE  # ERC-20 token address
    block_list = df_dateblock['block_number'].tolist() # [18116543, 18116543-7140*30] # 
    print("the results have been saved into CSV")
    # df_curvep_ste_supply=get_totalsupply_in_blocks(w3, token_steCRV, block_list)
    # print(df_curvep_ste_supply)

    print("\ntest get_hist_daily_crypto_price---")
    start_date = "20230801"
    end_date = "20231211"
    # print("the results have been saved into CSV")
    # df_price_steth_eth = get_hist_daily_crypto_price('staked-ether','STETH', start_date, end_date, vs_currency='eth')
    # print(df_price_steth_eth)

    print("\ntest get_hist_daily_crypto_price---")
    start_date = "20230801"
    end_date = "20231211"
    print("the results have been saved into CSV")
    # df_price_in_eth = get_hist_daily_crypto_price('sweth','swETH', start_date, end_date, vs_currency='eth')
    # print(df_price_in_eth)

