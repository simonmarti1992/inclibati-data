import pandas as pd

class header():
    def __init__(self, epwPath = 'FRA_Paris.Orly.071490_IWEC.epw'):
        dat_txt = open(epwPath, "r")
        myList = dat_txt.readlines()
        dat_txt.close()
        self.head = myList[:7]

        
    

def get():
    columns = ['Year', 'Month', 'Day', 'Hour', 'Minute',
           'Data Source and Uncertainty Flags', 'Dry Bulb Temperature',
           'Dew Point Temperature', 'Relative Humidity',
           'Atmospheric Station Pressure', 'Extraterrestrial Horizontal Radiation',
           'Extraterrestrial Direct Normal Radiation',
           'Horizontal Infrared Radiation Intensity',
           'Global Horizontal Radiation', 'Direct Normal Radiation',
           'Diffuse Horizontal Radiation', 'Global Horizontal Illuminance',
           'Direct Normal Illuminance', 'Diffuse Horizontal Illuminance',
           'Zenith Luminance', 'Wind Direction', 'Wind Speed', 'Total Sky Cover',
           'Opaque Sky Cover (used if Horizontal IR Intensity missing)',
           'Visibility', 'Ceiling Height', 'Present Weather Observation',
           'Present Weather Codes', 'Precipitable Water', 'Aerosol Optical Depth',
           'Snow Depth', 'Days Since Last Snowfall', 'Albedo',
           'Liquid Precipitation Depth', 'Liquid Precipitation Quantity', '']
    return columns



def index():
    initRun = '2021-01-01 01:00:00'
    endRun = '2022-01-01 00:00:00'
    myIndex = pd.date_range(start=initRun, end=endRun, freq='1h')
    return myIndex