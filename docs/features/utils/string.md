## String converter and utilities

### Remove duplicates from list

Returns a list of unique entries from `not_distinct_list`.

````python
from ambient_toolbox.utils.string import distinct

not_distinct_list = ['Beer', 'Wine', 'Whiskey', 'Beer']
distinct_list = distinct(not_distinct_list)

# Result: ['Whiskey', 'Wine', 'Beer']
````

Note that the order might change due to internal casting to a set.

### Slugify a filename

Turns a string into a nice slugified filename.

````python
from ambient_toolbox.utils.string import slugify_file_name

filename = 'hola and hello.txt'
slug = slugify_file_name(filename)
# Result: "hola_and_hello.txt"
````

You can pass a parameter to control how many characters the slug is supposed to have.

````python
from ambient_toolbox.utils.string import slugify_file_name

filename = 'a very long filename.txt'
slug = slugify_file_name(filename, 6)
# Result: "a_very.txt"
````

### Smart truncate

This helper cuts a string at a word-boundary and therefore keeps words intact. Similar to djangos
default-filter `truncatechars`, you can pass the desired string length.

````python
from ambient_toolbox.utils.string import smart_truncate

my_sentence = 'I am a very interesting sentence.'
truncated_str = smart_truncate(my_sentence, 10)
# Result: "I am a..."
````

By default, after cutting the string, it will append "..." which can be configured as follows:

````python
from ambient_toolbox.utils.string import smart_truncate

my_sentence = 'I am a very interesting sentence.'
truncated_str = smart_truncate(my_sentence, 10, '[...]')
# Result: "I am a[...]"
````

### Converting a float to a German-formatted string

If you have a float which you like to convert to a properly formatted string (German format), then you can do this:

````python
from ambient_toolbox.utils.string import float_to_string

float_str = float_to_string(1234.56)
# Result: "1234,56"
````

If you are not sure your float value will always be set, you can either use the default fallback or overwrite it with
something custom.

````python
from ambient_toolbox.utils.string import float_to_string

value = None

# Default fallback
fallback_result = float_to_string(value)
# Result: "0,00"

# Custom fallback
fallback_result = float_to_string(value, 'NaN')
# Result: "NaN"
````

### Converting a date object to string

If you want to easily convert a date object to a string in the given format, just use this helper:

````python
import datetime
from ambient_toolbox.utils.string import date_to_string

# Default format (German)
date_str = date_to_string(datetime.date(2020, 9, 19))
# Result: "19.09.1985"

# Custom format
date_str = date_to_string(datetime.date(2020, 9, 19), str_format='%Y-%m-%d')
# Result: "2020-09-19"
````

Again, you can set a replacement if the date object is `None`:

````python
import datetime
from ambient_toolbox.utils.string import date_to_string

# Default fallback
date_str = date_to_string(None)
# Result: "-"

# Custom fallback
date_str = date_to_string(None, 'no date')
# Result: "no date"
````

### Converting a datetime object to string

If you want to easily convert a datetime object to a string in the given format, just use this helper:

````python
import datetime
from ambient_toolbox.utils.string import datetime_to_string

# Default format (German)
datetime_str = datetime_to_string(datetime.datetime(2020, 9, 19, 8))
# Result: "19.09.1985"

# Custom format
datetime_str = datetime_to_string(datetime.datetime(2020, 9, 19, 8), str_format='%Y-%m-%d')
# Result: "2020-09-19"
````

Again, you can set a replacement if the datetime object is `None`:

````python
import datetime
from ambient_toolbox.utils.string import datetime_to_string

# Default fallback
datetime_str = datetime_to_string(None)
# Result: "-"

# Custom fallback
datetime_str = datetime_to_string(None, 'no datetime')
# Result: "no datetime"
````

### Converting numbers to string

If you have a float or int variable which you like to convert to a properly formatted string, then you can do this:

````python
from ambient_toolbox.utils.string import number_to_string

number_str = number_to_string(1234.56, decimal_digits=2)
# Result: "1,234.56"
````

If you are not sure your float value will always be set, you can either use the default fallback or overwrite it with
something custom.

````python
from ambient_toolbox.utils.string import number_to_string

value = None

# Default fallback
fallback_result = number_to_string(value)
# Result: "0,00"

# Custom fallback
fallback_result = number_to_string(value, replacement='NaN')
# Result: "NaN"
````

Furthermore, all values will be rounded to the number of `decimal_digits` passed. Defaults to 0. Note, that the
result will NOT be localised!

### Getting a value or a default

Similar to django filter `default`, this method will return the value if it is not equal to `None` and
will return the fallback value otherwise.

````python
from ambient_toolbox.utils.string import string_or_none_to_string

value = 'I am a string.'

# Value set
result = string_or_none_to_string(value)
# Result: "I am a string."

# Value not set, default fallback value
result = string_or_none_to_string(None)
# Result: "-"

# Value not set, custom fallback value
result = string_or_none_to_string(None, replacement='empty')
# Result: "empty"
````

### Lightweight XML to HTML converter

If you want a simple transformer from XML to HTML(-entities), you can use this helper:

````python
from ambient_toolbox.utils.string import encode_to_xml

value = '<tag>Something with an ampersand (&)</tag>'
result = encode_to_xml(value)
# Result: "'&lt;tag&gt;Something with an ampersand (&amp;)&lt;/tag&gt;'"
````

This method will replace all "<", ">" and "&" with their HTML representation.
