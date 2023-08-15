from datetime import datetime
import pandas as pd
import requests


class EARecordSearch:
    def __init__(self, station_name : str) -> None:
        """

        Parameters
        ----------
        station_name : string
            Station's name
        """
        
        self._station_name = station_name

        self._observed_property = None

        self._min_date = None
        self._max_date = None
        self._periodName = None

        self._station_wiskiID = None
        self._station_notation = None
        self._search_notation = None
        self._fetched_data = None
        self._isWQ_station = None

        self._notWQ_property = ["waterFlow", "waterLevel", "rainfall", "groundwaterLevel"]
        self._WQ_property = ["dissolved-oxygen", "fdom", "bga", "turbidity", "chlorophyll", "conductivity", "temperature", "ammonium", "nitrate", "ph"]
        self._properties = ["waterFlow", "waterLevel", "rainfall", "groundwaterLevel", "dissolved-oxygen", "fdom", "bga", "turbidity", "chlorophyll", "conductivity", "temperature", "ammonium", "nitrate", "ph"]
        
        self._periodName_list = ["15min", "daily", "sub-daily"]          
        
    

    @property
    def station_name(self) -> str:
        
        return self._station_name
    
    @property
    def observed_property(self) -> str:

        return self._observed_property

    @property
    def min_date(self) -> str:

        return self._min_date
    
    @property
    def max_date(self) -> str:

        return self._max_date
    
    @property
    def periodName(self) -> str:

        return self._periodName
    
    @property
    def station_wiskiID(self) -> str:

        return self._station_wiskiID
    
    @property
    def station_notation(self) -> str:

        return self._station_notation
    
    @property
    def search_notation(self) -> str:

        return self._search_notation

    @property
    def isWQ_station(self) -> bool:

        return self._isWQ_station

    @property
    def fetched_data(self) -> pd.DataFrame:

        return self._fetched_data
    
    @property
    def notWQ_property(self) -> list:

        return self._notWQ_property
    
    @property
    def WQ_property(self) -> list:

        return self._WQ_property
    
    @property
    def properties(self) -> list:

        return self._properties
    
    @property
    def periodName_list(self) -> list:

        return self._periodName_list
    

    def set_parameter(self, observed_property : str, periodName : str = None, min_date : str = None, max_date : str = None):
        """
        Set parameters for record searching.
        
        Parameters
        ----------
        observed_property : string
            - {waterFlow|waterLevel|rainfall|groundwaterLevel|dissolved-oxygen|fdom|bga|turbidity|chlorophyll|conductivity|temperature|ammonium|nitrate|ph}
        
        periodName : string
            periodName
            - {15min|daily|sub-daily}
            
        min_date : string
            Search from date, format as "yyyy-mm-dd".
            Default set as today - 6 months.

        max_date : string
            Search to date, format as "yyyy-mm-dd".
            Default set as today.

        raise ValueError if observed_property is not list of observed properties.

        raise ValueError if periodName is not in list of periodName_list.
        
        """

        if observed_property not in self._properties:
            raise ValueError("observed_property \"{0}\" not in {1}".format(observed_property, self._properties))
        
        if periodName is None:
            periodName = "15min"

        if periodName not in self._periodName_list: 
            raise ValueError("periodName \"{0}\" not in {1}".format(periodName, self._periodName_list))

        self._observed_property = observed_property
        self._periodName = periodName

        if self._observed_property in self._notWQ_property:
            self._isWQ_station = False
            self._station_wiskiID = self._find_wiskiID()
        else:
            self._isWQ_station = True
            self._station_notation = self._find_notation()
            self._periodName = "sub-daily"

        if min_date is None:
            self._min_date = datetime(datetime.today().year, (datetime.today().month - 6), datetime.today().day).strftime("%Y-%m-%d")
            print("Min date set as: {0}".format(self._min_date))
        else:
            self._min_date = min_date 

        if max_date is None:
            self._max_date = datetime.now().strftime("%Y-%m-%d") #Today's date
            print("Max date set as: {0} (today)".format(self._max_date))
        else:
            self._max_date = max_date

        self._fetched_data = self._fetch_data()

    
    def _fetch_data(self) -> pd.DataFrame:
        """
        Fetch data of a given station.

        Returns
        -------
        df : pd.DataFrame
            Measurement data.

        raise Exception if r.status code is other than 200.
        """
        url = "http://environment.data.gov.uk/hydrology/id/measures/{measure}/readings"

        if self.isWQ_station == False:
            payload = {"station.wiskiID" : self._station_wiskiID,
                    "observedProperty" : self.observed_property,
                    "periodName" : self.periodName,
                    "min-date" : self.min_date,
                    "max-date" : self.max_date
                    }
        else:
            payload = {"station" : self._station_notation,
                    "observedProperty" : self.observed_property,
                    "periodName" : self.periodName,
                    "min-date" : self.min_date,
                    "max-date" : self.max_date,
                    }
        
        r = requests.get(url, params=payload)
        if r.status_code == 200:
            df = pd.json_normalize(r.json(), "items")
            return df
        else:
            raise Exception("Request failed. Status code {0} with message {1}".format(r.status_code, r.json()))
    

    def _check_staiton(self) -> None:
        """
        Checks if station_name provided, exists.

        raise Exception if r.status code is other than 200.

        raise ValueError if the station's notation was not found.

        """
        url = "http://environment.data.gov.uk/hydrology/id/stations"
        payload = {"search" : self.station_name}
        r = requests.get(url, params=payload)
        if r.status_code == 200:
            df = pd.json_normalize(r.json(), "items")
        else:
            raise Exception("Request failed. Status code {0} with message {1}".format(r.status_code, r.json()))
        
        if "notation" in df.keys():
            self._search_notation = df["notation"]
        else:
            raise ValueError("Notation not found for station {0}".format(self.station_name))
        
        
    def _find_wiskiID(self) -> str:
        """
        Find's an instrument unique wisikiID identifier with it's station name and property of observation.

        Returns
        -------
        wiskiID : string
            Instrument's unique identifier.

        raise Exception if r.status code is other than 200.

        raise ValueError if the station's wiskiID was not found.
        """
        url = "http://environment.data.gov.uk/hydrology/id/stations"

        payload = {"search" : self.station_name,
                   "observedProperty" : self.observed_property
                   }

        r = requests.get(url, params=payload)
        if r.status_code == 200:
            df = pd.json_normalize(r.json(), "items")
        else:
            raise Exception("Request failed. Status code {0} with message {1}".format(r.status_code, r.json()))

        if len(df) > 0:
            wiskiID = df["wiskiID"][0]
            return wiskiID
        else:
            raise KeyError("Station `{0}' with observed property `{1}' wiskiID was not found".format(self.station_name, self.observed_property))

    def _find_notation(self) -> str:
        """
        Find's a Water Quality (WQ) station notation (identifier) from it's station name and property of observation.

        Returns
        -------
        notation : string
            Water Quality station's notation.

        raise Exception if r.status code is other than 200.

        raise ValueError if the station's notation was not found.
        """
        url = "http://environment.data.gov.uk/hydrology/id/stations"
        payload = {"search" : self.station_name,
                   "observedProperty" : self.observed_property
                   }
        
        r = requests.get(url, params=payload)
        if r.status_code == 200:
            df = pd.json_normalize(r.json(), "items")
        else:
            raise Exception("Request failed. Status code {0} with message {1}".format(r.status_code, r.json()))
        
        if len(df) > 0:
            notation = df["notation"][0]
            return notation
        else:
            raise KeyError("Station `{0}' with observed property `{1}' notation was not found. \n Observed properties at this station are: {2}".format(self.station_name, self.observed_property))

    def get_station_parameters(self) -> pd.DataFrame:
        """
        Fetches the station parameters.

        Returns
        -------
        params : pd.DataFrame
            Station's parameters.
            - Index [parameter, unitName, periodName, valueType, label]
        
        raise Exception if r.status code is other than 200.
        """
        self._check_staiton()

        url = "http://environment.data.gov.uk/hydrology/id/measures"
        payload = {"station" : self._search_notation}

        r = requests.get(url, params=payload)
        if r.status_code == 200:
            df = pd.json_normalize(r.json(), "items")
            params = pd.DataFrame({'parameter' : df["parameter"].tolist(),
                                'unitName' : df["unitName"].tolist(), 
                                'periodName' : df["periodName"].tolist(),  
                                'valueType' : df["valueType"].tolist(),
                                'label' : df["label"].tolist()})
            return params
        else:
            raise Exception("Request failed. Status code {0} with message {1}".format(r.status_code, r.json()))
        
    def get_parameter_data(self) -> pd.DataFrame:
        """
        Returns a station's record data of a given property; parameters are set by set_parameter().

        Returns
        -------
        fetched_data : pd.DataFrame
            Returns fetched data from set_parameter(). 
        
        """


        if self._fetched_data is None:
            raise ValueError("Data was not fetched, set_parameter() first.")
        
        return self._fetched_data

    
    def find_closest_record(self, date: str = None, time : str = None, dateTime : str = None) -> pd.DataFrame:
        """
        Find's the closest measurement record for a stated date and time.

        Parameters
        ----------
        date : string
            Search date in the format of "yyyy-mm-dd".

        time : string
            Search time in the format of "hh:mm" or "hh:mm:ss".

        dateTime : string
            ISO8601 dateTime format.
            * "YYYY-mm-ddTHH:MM:SS" i.e "2023-07-07T12:00:00".

        Returns
        -------
        df_record : pd.DataFrame
            Record of the closest or exact dateTime searched.

        raise ValueError if fetched_data is None
        """
        if self._fetched_data is None:
            raise ValueError("Data was not fetched, set_parameter() first.")

        if dateTime is not None:
            target_datetime = pd.to_datetime(dateTime)
        elif date is not None and time is not None:
            target_datetime = pd.to_datetime("%sT%s" % (date, time)) #ISO 8601
        else:
            raise ValueError("Provide either date and time or dateTime.")

        df_record = self._fetched_data

        search_datetimes = pd.to_datetime(df_record["dateTime"])
        closest_index = (search_datetimes - target_datetime).abs().idxmin()
        # Print difference in time, in minutes, between target and closest
        time_diff = (search_datetimes[closest_index] - target_datetime).total_seconds() / 60
        # print("Time difference to closest record: %.2f minutes" % time_diff)
        return pd.DataFrame(df_record.loc[closest_index]).transpose()