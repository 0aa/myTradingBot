from multiprocessing import Pool
import time
from finta.finta import TA


class Tes:
    def __init__(self):
        self.a = None
        self.b = None
class Tes2:
    def __init__(self):
        self.a = None
        self.b = None
        self.c = None

cls = Tes()
cls2 = Tes2()
cls.a = 1
cls.b = 3
vr = vars(cls)
print(vr)
# v = {'a': 1, 'b': 3}

for i in vr:
    print('i',i, vr[i])

print(vars(cls2))

    # start 4 worker processes
    # with Pool(processes=4) as pool:



"""
    '''
        # print "[0, 1, 4,..., 81]"
        print(pool.map(f, range(10)))

        # print same numbers in arbitrary order
        for i in pool.imap_unordered(f, range(10)):
            print(i)

        # evaluate "f(10)" asynchronously
        res = pool.apply_async(f, [10])
        print(res.get(timeout=1))             # prints "100"

        # make worker sleep for 10 secs
        res = pool.apply_async(sleep, [10])
        print(res.get(timeout=1))             # raises multiprocessing.TimeoutError

    # exiting the 'with'-block has stopped the pool
    '''
"""

"""
    #initial test with Monte-Carlo method 

def run_test(prepared_df):
    lend=len(prepared_df)
    prepared_df['hcc']=[None]*lend
    prepared_df['lcc']=[None]*lend

    for i in range(4,lend-1):
        if isHCC(prepared_df,i)>0:
            prepared_df.at[i,'hcc']=prepared_df['close'][i]
        if isLCC(prepared_df,i)>0:
            prepared_df.at[i,'lcc']=prepared_df['close'][i]
    position=0
    eth_proffit_array=[[20,1],[40,1],[60,2],[80,2],[100,2],[150,1],[200,1],[200,0]]
    deal=0
    prepared_df['deal_o']=[None]*lend
    prepared_df['deal_c']=[None]*lend
    prepared_df['earn']=[None]*lend

    #optimization
    #random lot size
    lot_size = np.round((np.random.exponential(scale=1, size=1)),3)
    #take profit
    take_profit_array = pd.DataFrame(columns=['Price', 'Lot'])
    random_price = pd.DataFrame(np.random.dirichlet(np.ones(5), size=1)[0],columns = ['Price']).sort_values(by='Price')
    random_lot = pd.DataFrame(np.random.dirichlet(np.ones(5), size=1)[0],columns = ['Lot'])
    #max take profit is also randomized
    max_take_profit = round(np.random.uniform(0.01, 1),2)
    take_profit_array['Price'] = np.round(random_price*max_take_profit,2)
    take_profit_array['Lot'] = np.round((lot_size*random_lot),3)
    #######
    #stop loss price is also randomized
    max_stop_loss_percent = np.random.uniform(0.001, 0.1)
    stop_loss_percent = round(np.random.uniform(0.001, max_stop_loss_percent),3)
    #random params to open a position
    #tandom slope
    random_slope = np.random.uniform(10, 90)
    short_slope= 100 - np.random.default_rng().noncentral_chisquare(3, random_slope)
    long_slope= 0 - np.random.default_rng().noncentral_chisquare(3, random_slope)
    #random pos in shannel
    random_pos_in_channel = np.random.uniform(0, 50)
    short_pos_in_channel= (100 - np.random.default_rng().noncentral_chisquare(3, random_pos_in_channel))*0.01
    long_pos_in_channel= np.random.default_rng().noncentral_chisquare(3, random_pos_in_channel)*0.01

    
    #eth_proffit_array = take_profit_array.values.tolist()
    
    

    for i in range(4,lend-1):
        prepared_df.at[i,'earn']=deal
        
        
        if position>0:
            # add profit/loss for long
            if(prepared_df['close'][i]<stop_price):
                # stop loss
                deal=deal+(prepared_df['close'][i]-open_price)*position
                prepared_df.at[i,'deal_c']=prepared_df['close'][i]
                position=0
            else:
                temp_arr=copy.copy(proffit_array)
                for j in range(0,len(temp_arr)-1):
                    delta=temp_arr[j][0]
                    contracts=temp_arr[j][1]
                    if(prepared_df['close'][i]>(open_price+delta)):
                    # take profit
                        prepared_df.at[i,'deal_c']=prepared_df['close'][i]
                        deal=deal+(prepared_df['close'][i]-open_price)*contracts
                        position=position-contracts
                        del proffit_array[0]

        elif position<0:
            # add profit/loss for short
            if(prepared_df['close'][i]>stop_price):
                # stop loss
                deal=deal+(open_price-prepared_df['close'][i])*position
                prepared_df.at[i,'deal_c']=prepared_df['close'][i]
                position=0
            else:
                temp_arr=copy.copy(proffit_array)
                for j in range(0,len(temp_arr)-1):
                    delta=temp_arr[j][0]
                    contracts=temp_arr[j][1]
                    if((open_price-prepared_df['close'][i])>delta):
                    # take profit
                        prepared_df.at[i,'deal_c']=prepared_df['close'][i]
                        deal=deal+(open_price-prepared_df['close'][i])*contracts
                        position=position+contracts
                        del proffit_array[0]

        else:
        # try to find enter point
            if prepared_df['lcc'][i-1]!=None:
               # found bottom - OPEN LONG
                if prepared_df['position_in_channel'][i-1]<long_pos_in_channel:
                    # close to top of channel
                    if prepared_df['slope'][i-1]<long_slope:
                        # found a good enter point
                        if position==0:
                            proffit_array=copy.copy(eth_proffit_array)
                            position=lot_size
                            open_price=prepared_df['close'][i]
                            stop_price=prepared_df['close'][i]*(1-stop_loss_percent)
                            prepared_df.at[i,'deal_o']=prepared_df['close'][i]
            if prepared_df['hcc'][i-1]!=None:
               # found top - OPEN SHORT
                if prepared_df['position_in_channel'][i-1]>short_pos_in_channel:
                    # close to top of channel
                    if prepared_df['slope'][i-1]>short_slope:
                        # found a good enter point
                        if position==0:
                            proffit_array=copy.copy(eth_proffit_array)
                            position=-lot_size
                            open_price=prepared_df['close'][i]
                            stop_price=prepared_df['close'][i]*(1+stop_loss_percent)
                            prepared_df.at[i,'deal_o']=prepared_df['close'][i]

    temp_result = pd.DataFrame(columns=['stop_loss_percent',
                                           'long_slope',
                                           'short_slope',
                                           'long_pos_in_channel',
                                           'short_pos_in_channel',
                                           'lot_size',
                                           'total_profit']) 

    
    temp_result['lot_size']=pd.DataFrame([lot_size],columns = ['lot_size'])
    temp_result['stop_loss_percent']=pd.DataFrame([stop_loss_percent],columns = ['stop_loss_percent'])
    temp_result['long_slope']=pd.DataFrame([long_slope],columns = ['long_slope'])
    temp_result['short_slope']=pd.DataFrame([short_slope],columns = ['short_slope'])
    temp_result['long_pos_in_channel']=pd.DataFrame([long_pos_in_channel],columns = ['long_pos_in_channel'])
    temp_result['short_pos_in_channel']=pd.DataFrame([short_pos_in_channel],columns = ['short_pos_in_channel'])
    temp_result['total_profit']=pd.DataFrame([int(deal)],columns = ['total_profit'])
    temp_result['num_of_deals']=pd.DataFrame([prepared_df['deal_c'].count()],columns = ['num_of_deals'])
    return temp_result, prepared_df,take_profit_array

    

results_array = pd.DataFrame(columns=['stop_loss_percent',
                                           'long_slope',
                                           'short_slope',
                                           'long_pos_in_channel',
                                           'short_pos_in_channel',
                                           'lot_size',
                                           'total_profit'])

for i in range(10):
    t = time.perf_counter()
    prepared_df = PrepareDF(df_train)
    temp_result, temp_df, take_profit_array = run_test(prepared_df)
    results_array = pd.concat([results_array, temp_result], sort=False, ignore_index=True)
    print("Iteration",i+1,time.perf_counter()-t)
"""