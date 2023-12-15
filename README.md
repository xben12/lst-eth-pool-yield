# lst-eth-pool-yield

Comparing Curve stETH/ETH pool and MAV swETH/ETH Pool
* main_lst_pool_eval.py to get metrics of pool (curve steth-eth, mav sweth-weth)
* library_pool_data.py use alchemy (need your own api key)  and coingecko  api to download pool tx and token price data. data also pre-saved in csv in output folder for logic to run without downloading.
* library_pool_logic.py compile/clean the data into dataframe and calculate metrics
* library_constant.py predefined wallet address, token, abi
code not optimised, with a lot of print in between to cross check results. 