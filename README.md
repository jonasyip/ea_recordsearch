# ea_recordsearch
A Python package that fetches hydrology data from the Environment Agency Hydrology Data Explorer (https://environment.data.gov.uk/hydrology/explore).


## Installation 

Clone this repository into a directory on your computer. Navigate to that directory and run: 

```
pip install .
```

You can now import the package as normal, e.g., `from earecordsearch.searcher import EARecordSearch`.

## Example of use
```python
from earecordsearch.searcher import EARecordSearch
stationName = "Osney Lock"
search = EARecordSearch(stationName)

station_parameters = search.get_station_parameters()
print(station_parameters)

search.set_parameter(observed_property="rainfall", min_date="2023-07-08", max_date="2023-08-07")
record = search.find_closest_record("2023-05-15", "12:15")
#or
record = search.find_closest_record(dateTime="2023-05-15T12:15")
print(record)

data = search.get_parameter_data()
print(data)

```

To install, do `pip install .`

### Observed property list
```python
{waterFlow|waterLevel|rainfall|groundwaterLevel|dissolved-oxygen|fdom|bga|turbidity|chlorophyll|conductivity|temperature|ammonium|nitrate|ph}
```
### periodName
```python
{15min|daily|sub-daily}
```
