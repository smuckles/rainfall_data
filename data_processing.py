def main():    
    
    #### Importing packages:
    
    import numpy as np
    import pandas as pd
    import datetime
    import seaborn as sb
    import matplotlib.pyplot as plt
    from scipy import interpolate
    from scipy import integrate
    
    #### import data set -- in this case as a csv file -- however, could easily be adjusted to take input from SQL db
    df_raw = pd.read_csv('../input/accumRainfall.csv')
    
    #### data preprocessing: check for nulls and nonsensical values i.e. value or unixdatetime < 0
    #Fill na to fill any null/NA values; in this case we will choose value as 0 but could also choose mean/median etc.
    df_raw['value'].fillna(value = 0, inplace = True)
    #drop any negative valued value or unixdatetime since we can't infer what they should be
    df_raw.loc[~(df_raw['value'] > 0), 'value'] = np.nan
    df_raw.loc[~(df_raw['unixdatetime'] > 0), 'unixdatetime'] = np.nan
    #We will drop any unixdatetime values that are NA/null as we cannot infer what they should be
    df_raw.dropna(axis = 0, how = 'any', inplace = True)
    
    '''
    #EDA: good to have a look and get an idea of how the data looks:
    
    df_raw['UTC_datetime'] = df_raw['unixdatetime'].apply(datetime.datetime.utcfromtimestamp)
    plt.xlim(df_raw['UTC_datetime'].iloc[0], df_raw['UTC_datetime'].iloc[-1])
    sb.scatterplot('UTC_datetime', 'value', data = df_raw)
    plt.show()
    
    '''
    #First create an array of evenly spaced times: in this case we will use a resolution of minutes
    total_num_min = int( (df_raw['unixdatetime'].iloc[-1] - df_raw['unixdatetime'].iloc[0]) / 60 ) #total number of minutes between first obs and last
    time_array = np.linspace(df_raw['unixdatetime'].iloc[0], df_raw['unixdatetime'].iloc[-1], total_num_min) 
    
    #next we interpolate using the raw data; first we convert the value which is a rate in hours eg. inches per hour to inches per second
    #take sqrt as part of making sure intepolation only returns positive values
    df_raw['value'] = np.sqrt(df_raw['value']/3600)
    
    # the choice of interpolation method matters here: I chose a gaussian method because I felt like that is more accurate to weather behaviour i.e. rain clouds
    # are discrete generally, not continuous
    # the parameters epsilon and smooth require finetuning to achieve a realistic interpolation.
    f = interpolate.Rbf(df_raw['unixdatetime'], df_raw['value'], epsilon = 43200, function = 'gaussian', smooth = 0.5)
    #this function below counters the sqrt above
    def f_squared(x):
        return np.square(f(x))
    #the interpolated data with the time_array input:
    rainfall = f_squared(time_array)
    
    #creating an output dataframe which we will will use as the output data
    df_processed = pd.DataFrame( {'TimeStamp' : time_array, 'Value' : rainfall} )
    
    '''
    #more EDA: in this case, get a visual idea of how the interpolation function is behaving which I then used to inform my choices of epsilon and smooth
    df_processed['UTCTime'] = df_processed['TimeStamp'].apply(datetime.datetime.utcfromtimestamp)
    plt.xlim(df_processed['UTCTime'].iloc[0], df_processed['UTCTime'].iloc[-1])
    sb.lineplot('UTCTime', 'Value', data = df_processed)
    plt.show()
    '''
    
    #The below function determines the 30 minute period with the largest amount of rainfall
    #The method is simply to scan through the generated data range and integrate 30 minute periods
    #update the max_30_time and max_30_amt any time a new integral is greater than the current recorded one
    def find_max_30():
        #this takes a while, performs a large number of integrals
        for time in range(0, total_num_min - 30):
            if time == 0:
                max_30_time = [df_processed['TimeStamp'].iloc[time], df_processed['TimeStamp'].iloc[time + 30]]
                max_30_amt = integrate.quad(func = f_squared, a = df_processed['TimeStamp'].iloc[time], b = df_processed['TimeStamp'].iloc[time + 30])
            else:
                temp_int = integrate.quad(func = f_squared, a = df_processed['TimeStamp'].iloc[time], b = df_processed['TimeStamp'].iloc[time + 30])
                if temp_int > max_30_amt:
                    max_30_time = [df_processed['TimeStamp'].iloc[time], df_processed['TimeStamp'].iloc[time + 30]]
                    max_30_amt = temp_int
                else:
                    pass
                
        print(max_30_time)
        print(max_30_amt)
    
    find_max_30()

    #Output the new de-accumulated data to a csv file; this can easily be changed to output to a SQL table etc.
    df_processed.to_csv('de_accumRainfall.csv')

if __name__ == "__main__":
    main()
