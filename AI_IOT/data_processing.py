import statsmodels.api as sm
import numpy as np

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
    #print(results.summary())
    # constant_term + AR(1)*y(t-1) + ... + AR(p)*y(t-p) + MA(1)*e(t-1) + ... + MA(q)*e(t-q) + e(t)constconstant_term + AR(1)*y(t-1) + ... + AR(p)*y(t-p) + MA(1)*e(t-1) + ... + MA(q)*e(t-q) + e(t)
    #print(results.params)
    #print(results.arparams)
    #print(results.maparams)
    forecast = results.predict(start=len(arr), end=len(arr) + predictNum)
    print(forecast)

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

if __name__ == '__main__':
    np.random.seed(42)
    y = np.random.randn(100)

    # print(sm.robust.scale.mad(y))
    print(y)
    print(MAPE_detect(y, 1))
    #testingARMA()
    