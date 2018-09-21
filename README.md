# rainfall_data
Code to process rainfall data from mystery site in Pennsylvania. 

The code can be run through a terminal like so: $python data_processing.py accumRainfall.csv
We could also modify the input to pull from and inject to a SQL table or some other method.

# DATA INPUT:
Two column csv file, first column being a unixtimestamp and the second being the value of rainfall rate (presumed to be inches per hour)

# DATA OUTPUT:
Two csv files:
    - A two column csv of the deaccumulated data spanning the total time range of observation at a resolution of 1 minute intervals with 
      the rainfall value in inches per second
    - A three column csv; the first two columns are the start and finish times of the 30 minute interval (as unix time stamp) calculated 
      to have the greatest  
      amount of rainfall. The last column is the calculated amount of rainfall (in inches)

# DATA CONTSTRAINTS:

The code assumes a csv file input with row 0 being the column headers. Any deviation from this will result in an error; extending the code to account for this is trivial.

# ASSUMPTIONS:

- I have assumed that the values are measured in inches given that the site location is in the USA.
- I have used an interpolation method from scipy to model the data. Obviously this has a number of drawbacks and is highly dependent on  
  the number of data points supplied. The method I used is scipy.interpolate.Rbf which uses a radial basis function. The method chosen was 
  gaussian as I felt this can most closely model the behaviour of rainfall on a location i.e. discrete with reasonably clear boundaries 
  between rain and no rain. The gaussian method has two hyperparameters, 'epsilon' and 'smooth', which can be finetuned to produce a more 
  realistic result.

# EXTENDING THE CODE:

The code currently takes a single input but could be modified to be run incrementally as new data comes in. If run in the terminal like above it could be modified to accomodate two inputs: the original full data set and the new data. The code would currently require that the new data be apended to the original set and the interpolation and integration calculations rerun. This would be time consuming, but if the new data is only coming in on the order of the same frequency ( > 24 hrs between data points) as the original data set then it is probably not an issue.

Only data required would be new unix timestamp and the rainfall value (in inches per hour)
