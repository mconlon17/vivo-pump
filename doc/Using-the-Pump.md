The Pump can be used from the command line, using a delivered main program called Simple VIVO (`sv`)

```bash
python sv.py -defn my_definition_file.json -src my_spreadsheet_file.csv -a get
```

By default, Simple VIVO reads parameters from a configuration file.  The configuration file tells Simple VIVO the address of your VIVO and the username and password needed to perform updates.

The Pump can also be used from a Python program by importing the pump, creating a pump object and calling
a method on it.  In the example below, a Pump object is created with a definition file and a source file.
The `get()` method uses the definition file to build queries that are run in your VIVO and produce the 
source file.

```python
import pump
p = Pump(defn='my_def.json', src='my_src.txt')
p.get()
```

In the example below, a Pump is created with a definition file name and a source file name.  An update is performed.
The update uses the definition to identify data in VIVO and compares it to data in the source file.  Source file
data values are used to update VIVO.  Following the update, VIVO contains the values from the source file.

```python
import pump
p = Pump(defn='my_def.json', src='my_src.txt')
p.update()
```