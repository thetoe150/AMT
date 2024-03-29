import statsmodels.api as sm
import numpy as np

import warnings
from statsmodels.tools.sm_exceptions import ConvergenceWarning
warnings.simplefilter('ignore', ConvergenceWarning)
warnings.simplefilter('ignore', category=UserWarning)

# K is a scale factor which assumes normally distributed data.
K = 1.4826 
    
def MAD_detect(arr, threshold=3.5):
    """
    Compute the median absolute deviation (MAD) of an array and return the indices
    of elements that are "abnormal" based on a given threshold.
    
    Parameters:
        arr (numpy.ndarray): Input array
        threshold (float): Threshold value to determine abnormality
        
    Returns:
        numpy.ndarray: Indices of abnormal elements in the input array
    """

    med = np.median(arr)
    mad = np.median(np.abs(arr - med)) * K
    z_scores = np.abs((arr - med) / mad)
    return np.where(z_scores > threshold)[0]

def ARMA_forecast(arr, predictNum=1):
    # Fit an ARMA(1,1) model
    model = sm.tsa.ARIMA(arr, order=(1, 0, 1), seasonal_order=(1, 0, 1, 12))
    results = model.fit()

    # Print the model summary
    print(results.summary())

    # constant_term + AR(1)*y(t-1) + ... + AR(p)*y(t-p) + MA(1)*e(t-1) + ... + MA(q)*e(t-q) + e(t)constconstant_term + AR(1)*y(t-1) + ... + AR(p)*y(t-p) + MA(1)*e(t-1) + ... + MA(q)*e(t-q) + e(t)
    #print(results.params)
    #print(results.arparams)
    #print(results.maparams)
    forecast = results.predict(start=len(arr), end=len(arr) + predictNum)
    return forecast

def MAPE_detect(y_true, y_pred):
    """
    Calculate the mean absolute percentage error between y_true and y_pred.
    
    Args:
        y_true: array-like of shape (n_samples,)
            Ground truth target values.
        y_pred: array-like of shape (n_samples,)
            Estimated target values.
            
    Returns:
        mean_absolute_percentage_error: float
            The mean absolute percentage error between y_true and y_pred.
    """
    y_true = np.asarray(y_true)
    #print((y_true - y_pred))
    return np.mean(np.abs((y_true - y_pred) / y_true)) * 100

def testingARMA():
    np.random.seed(42)

    y = np.random.randint(20, 39, size= 70)
    print('y value: ',y)
    # Fit an ARMA(1,1) model
    model = sm.tsa.ARIMA(y, order=(1, 0, 1))
    results = model.fit()

    forecast = results.predict(start=len(arr), end=len(arr) + 8)
    print('forecast value: ', forecast)

    # generate predictions with 95% confidence intervals
    pred_ci = results.conf_int(alpha=0.02)

    # print the predicted values and their confidence intervals
    print('prediction confident interval: ', pred_ci)

    # Print the model summary
    print(results.summary())

if __name__ == '__main__':
    np.random.seed(42)
    y = np.random.randn(100)

    arr = np.random.randint(27,37, size=10)
    print(arr)

    #print(ARMA_forecast(arr, 5))

    #arr = [27]
    #print(MAPE_detect(arr, 30))
    testingARMA()

    # print(sm.robust.scale.mad(y))
    #print(y)
    #print(MAPE_detect(y, 1))
    #testingARMA()
