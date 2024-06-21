## Math

### Round to decimal

The helper function ``round_to_decimal(value, precision)`` will round a given value to a specific precision,
for example \*.5. So 5.4 will be rounded to 5.5, and 5.6 to 5.5 as well. The result is always a float.

````python
result = round_to_decimal(5.4, 0.5)
# result = 5.5

result = round_to_decimal(5.6, 0.5)
# result = 5.5
````

### Round up decimal

The helper function ``round_up_decimal(value, precision)`` will round a given value **up** to a specific precision,
for example *.5. So 5.4 will be rounded to 5.5, and 5.6 to 6 as well. The result is always a float.

````python
result = round_up_decimal(5.4, 0.5)
# result = 5.5

result = round_up_decimal(5.6, 0.5)
# result = 6.0
````
