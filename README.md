# lst-eth-pool-yield

Comparing MAV swETH/ETH Pool vs Curve stETH/ETH pool
* library_pool_data.py use alchemy (need your own api) and coingecko  api to download. For easier usage, some data has been saved in csv in output folder that other py file can direct use.
* library_pool_logic.py compile/clean the data into dataframe and calculate metrics
* main_doc.ipynb is for chart