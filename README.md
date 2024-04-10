# Simple Library for parsing China Holidays

A simple & easy to use library for parsing China Holidays and check if a date is a workday. It does three things:

- Crawls the China Holidays from the specified URL
- Parses the holidays and stores them into a file
- Checks if a date is a holiday or a workday

## Usage

```python
    from holidays import Holiday

    # first if the holidays are not already stored
    Holiday.generate_holiday_file(2023)

    holiday = Holiday(2023)
    # init the holiday object
    holiday.init_data_source()

    assert "2023-10-06" in holiday
    assert "2023-10-08" in holiday
    assert holiday.is_working_day("2023-10-07")
```
