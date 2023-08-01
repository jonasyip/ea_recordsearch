# earecordsearch
A Python package that searches for observed property values in the Environment Agency Hydrology dataset.


## Installation 

Clone this repository into a directory on your computer. Navigate to that directory and run: 

```
pip install .
```

You can now import the package as normal, e.g., `import earecordsearch`.

## Example of use
```python
from earecordsearch.searcher import EARecordSearch
search = EARecordSearch("Osney Lock")

search.get_station_parameters()

search.set_parameter(observed_property="rainfall")
search.find_closest_record("2023-05-15", "12:15")
```
