# pricesearcher

### Functionalities
* After starting, first:
  * Reads a csv from local. The csv used was taken from [pricesearcher-code-tests](https://github.com/pricesearcher-code-tests/python-software-developer).
  * Reads a json [products.json](https://s3-eu-west-1.amazonaws.com/pricesearcher-code-tests/python-software-developer/products.json).
* Then, the **api** starts. Send an **item_id** to it, and the **api** returns the information of that item.

### Libraries
It has been used *python*.
Libraries used were:
* os
* gzip
* json
* urllib2

It has been used the framework **flask**.

### Files
* **pricesearcher.py**: The app.
* **cfg.py**: On this file must be set the url of the *json* and the path of the csv. It is imported by **pricesearcher.py**.
