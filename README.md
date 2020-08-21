
# Web Scraper of COVID-19 data for Poland

Python package [covid19poland](https://pypi.org/project/covid19poland/) is part of MFRatio project.

It provides access to death data in Poland due to COVID-19 as well as overall deaths data.

## Setup and usage

Install from [pip](https://pypi.org/project/covid19poland/) with

```python
pip install covid19poland
```

Several data sources are in current version
* Covid-19 deaths in Poland (offline) - manually checked
* Parser of Twitter of Polish Ministery of Health
* Covid-19 deaths from Wikipedia


Package is regularly updated. Update with

```bash
pip install --upgrade covid19poland
```

### Covid-19 deaths

Deaths can be acquired as dataframe of separate death cases with attributes

```python
import covid19poland as PL

x = PL.covid_death_cases()
```

or as death counts aggregated over 5y age groups, sex and region.

```python
x = PL.covid_deaths()
```

Granularity of the region is parametrizable as 0 (whole Poland), 2 (NUTS-2) or 3 (NUTS-3, default).

```python
x = PL.covid_deaths(level = 2) # setting region to be NUTS-2
```

The NUTS-2 and NUTS-3 classification is done using offline clone of file from
https://ec.europa.eu/eurostat/web/nuts/local-administrative-units.

**Online reading**

It is recommended to use the offline data, since they have been acquired
this way and manually checked. The data is offline acquirable with the package `covid19poland`.

If online data from Twitter is wanted, it can be downloaded and parsed as well.


```python
data,filtered,checklist = PL.twitter(start = "2020-06-01", end = "2020-07-01")
```

Turn on logs by typing following code before the `twitter()` function call.

```python
import logging
logging.basicConfig(level = logging.INFO)
```

The result of the `twitter()` call are three values

* data - containing the deceased people with their place and date of death
* filtered - tweets, that were filtered out. Just for validation that nothing was missed.
* checklist - list of dates that the parser is not sure about

The data can be saved to output files with 

```python
with open("data/6_in.json", "w") as fd:
    json.dump(data, fd)
with open("data/6_out.json", "w") as fd:
    json.dump(filtered, fd)
print(checklist)
```

Offline data can be validated towards deaths from `covid19dh` package,
the mismatching days are acquired by

```python
x = PL.mismatching_days()
```


### Deaths

The `covid19poland` can also fetch death data from GUS (*Główny Urząd Statystyczny*
or Central Statistical Office of Poland). The data is taken from http://demografia.stat.gov.pl/bazademografia/Tables.aspx
and it is deaths per month and gender in years 2010 - 2018.


```python
x = PL.deaths()
```

Local copy of the data in the package is used. To live-parse the data from the source, type

```python
x = PL.deaths(offline = False)
```

### Wikipedia

*Obsolete*

The table comes from version from beginning of June on Wikipedia page
https://en.wikipedia.org/wiki/COVID-19_pandemic_in_Poland

```python
x = PL.wiki()
```

Once better tabular source is found, it will replace the current one.

Level is a setting for granularity of data

1. Country level (default)
2. State level

```python
# country level
x1 = PL.fetch(level = 1)
# state level
x2 = PL.fetch(level = 2)
```

## Contribution

Developed by [Martin Benes](https://github.com/martinbenes1996).

Join on [GitHub](https://github.com/martinbenes1996/covid19poland).


