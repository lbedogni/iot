# iot

milestone 1:
unify service records by grouping them onto a database with pre defined fields
|| UNIQUE ID || uuid?, incremental?
|| FRIENDLY NAME ||
|| LOCATION || GPS coordinates, radius error
|| CREATED || timestamp date of creation
|| UPDATED || timestamp last update
|| TAG ARRAY || array of tags

(in another table)
|| ID UNIQUE || another unique id for the measure itself
|| ID SERVICE || pointer to the previous table
|| DATA UNIQUE ID || pretty much an unique ID characterizing the data measured. I would like to use rather an array of meta info stating the measure, the unit and other infos (e.g. [temperature,indoor,farenheit])
|| VALUE(s) ||
|| TIMESTAMP ||

Question 1: assume multiple data sensor (an unique measure giving both temperature and humidity). in my head in the second table we would use two separate records. Do we agree on that?

Question 2: we store data, what about services? what if i have an iot closed ecosystem that i may access in different ways? or simply a fog layer giving me some functionalities that are built-in? I need another table/database as a service registry (providing data on how to access the service itself.)
