import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import library_pool_data as lib_data
import library_pool_logic as lib_logic


print('\n-- Get MAV SWETH/ETH Pool Data (only top 5 & bottom 5 row)---')
date_begin_str='20230909'
date_end_str = '20231208'
df_mav = lib_logic.get_mav_pool_daily_asset_hold_and_trade_vol(date_begin_str, date_end_str)
print(df_mav.head(2))
print(df_mav.tail(2))
standard_col_names = ['date', 'block_number', 'pool_name', 'staking_token', 'token_price_eth', 'tvl_eth',  'staking_asset_amt_eth', 'traded_amt_eth']
print('\n90d annualised trading fee only yield', df_mav['daily_turnover_rate'].mean()*365*0.0002)
print('30d annualised trading fee only yield', df_mav['daily_turnover_rate'].head(30).mean()*365*0.0002)
print('\n90d average staking %', df_mav['daily_staking_rate'].mean())
print('30d average staking %', df_mav['daily_staking_rate'].head(30).mean())
print('\n90d average daily turnover rate', df_mav['daily_turnover_rate'].mean())
print('30d average daily turnover rate', df_mav['daily_turnover_rate'].head(30).mean())

print('\n-- Get CURVE STETH/ETH Pool Data ---')
df_curve = lib_logic.get_curve_pool_daily_asset_hold_and_trade_vol(date_begin_str, date_end_str)
print(df_curve.head(2))
print(df_curve.tail(2))
standard_col_names = ['date', 'block_number', 'pool_name', 'staking_token', 'token_price_eth', 'tvl_eth',  'staking_asset_amt_eth', 'traded_amt_eth']
print('\n90d annualised trading fee only yield', df_curve['daily_turnover_rate'].mean()*365*0.0001)
print('30d annualised trading fee only yield', df_curve['daily_turnover_rate'].head(30).mean()*365*0.0001)
print('\n90d average staking %', df_curve['daily_staking_rate'].mean())
print('30d average staking %', df_curve['daily_staking_rate'].head(30).mean())
print('\n90d average daily turnover rate', df_curve['daily_turnover_rate'].mean())
print('30d average daily turnover rate', df_curve['daily_turnover_rate'].head(30).mean())



df = lib_data.get_curve_steth_pool_daily_data()
# 
df['lp_token_price'] = (df['eth_balance'] + df['token_balance']*df['close_price'])/df['token_totalsupply']
df.set_index("date_yyyymmdd", inplace=True)


selected_dates = ['20230909', '20231008', '20231108', '20231208']
date_begin_str = selected_dates[0]
date_end_str = selected_dates[-1]

df['start_date'] = date_begin_str
df['end_data'] = date_end_str
df['days_invest'] = (pd.to_datetime(df.index, format='%Y%m%d') - pd.to_datetime(date_begin_str, format='%Y%m%d')  ).days

lp_token_price_initial  = df.loc[date_begin_str, 'lp_token_price']
lp_token_price_30dayback  = df.loc[selected_dates[-2], 'lp_token_price']
lp_token_price_final  = df.loc[date_end_str, 'lp_token_price']
df['lp_token_price_initial'] = lp_token_price_initial
df['lp_token_price_final'] = lp_token_price_final

print("\n Curve pool (staking+fee) yield: ")
print("90d (staking+fee) yield ", (lp_token_price_final/lp_token_price_initial-1)*365/90 )
print("30d (staking+fee) yield ", (lp_token_price_final/lp_token_price_30dayback-1)*365/30 )




print("draw imp loss chart:")
# product the impermanent loss section picture

price_change_down_scen = np.arange( 0, -0.015, -0.0005)
price_change_up_scen = lib_logic.get_bin_price_range_same_liquidity(price_change_down_scen)
price_change_scen =  np.concatenate((np.flip(price_change_down_scen),price_change_up_scen )) 

# print("price change scenarios: ", price_change_scen)

price_range_down  = np.array([-0.01, -0.005, -0.003, -0.002]) # np.arange(-0.01, -0.003, 0.002) 

result_no_range = lib_logic.get_impermanent_loss(price_change_scen)
result_array = np.column_stack((price_change_scen, result_no_range[:,0]))
# print("result no range: ", result_array)

imp_loss_column_names = np.array(['Price Change', 'Full range LP'])

#print("price_range_down", price_range_down)

for price_range_down_i in price_range_down:
    loss_i = lib_logic.get_impermanent_loss_range_pos(price_change_scen, price_range_down_i)
    # print("shape",result_array.shape, loss_i.shape )
    result_array = np.column_stack((result_array,loss_i ))
    price_range_up_i = lib_logic.get_bin_price_range_same_liquidity(price_range_down_i)
    scen_label = "Bin Range [" + '{:.3f}'.format(price_range_down_i) + ","  + '{:.3f}'.format(price_range_up_i) + "]"
    imp_loss_column_names = np.append(imp_loss_column_names, scen_label) 

#print("all imp loss:",result_array.shape )

data = result_array
# Extract x-labels (column 0)
x_labels = data[:, 0]

# Extract data columns
data_columns = data[:, 1:]

# Sample labels
labels = imp_loss_column_names[1:]

# Plot each data column with labels
for i, column in enumerate(data_columns.T):
    plt.plot(x_labels, column, label=labels[i])

# Customize the plot
plt.title('Impermanent loss against price_change and bin_range_set')
plt.xlabel('swETH price change %')
plt.ylabel('Imp loss %')
plt.grid(True)
plt.legend()  # Show legend with labels
plt.show()




