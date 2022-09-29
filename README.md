# Simple Python China Holidays Library

A simple & easy to use library for checking whether a date is a China holiday or a work day.

## Usage

``` python
    holiday = Holiday(2022)
    assert "2022-10-01" in holiday
    assert "2022-10-08" in holiday
    assert holiday.is_workday("2022-10-09")
```
