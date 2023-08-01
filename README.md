# earecordsearch
EA record searcher


## Examples
```python
search = EARecordSearch("Osney Lock")

search.get_station_parameters()

search.set_parameter(observed_property="rainfall")
search.find_closest_record("2023-05-15", "12:15")
```
