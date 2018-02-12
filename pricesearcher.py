#!.*/venv/bin/python

# Importing modules
from flask import Flask
import os
import gzip
import json
import urllib2
# Importing cfg File
try:
    import cfg
except:
    print("Error: can\'t import cfg.py file")
    raise
else:
    print("cfg.py successfully imported")

# Calling Flask
app = Flask(__name__)


# Function to set the cfg variables of the app
def set_cfg():
    # Setting Global Dictionary to store items information
    global d_items
    d_items = {}

    # Setting the path of the csv file >>> cvs_path
    try:
        if cfg.cvs_path == "":
            raise
        else:
            global csv_path
            # importing cvs_path from cfg.py
            csv_path = cfg.cvs_path
    except:
        print("Error: cvs_path not found on cfg.py or it is empty. "
              " >>> NO csv can be imported.")
        raise
    else:
        print("csv_path successfully imported: csv_path = " + csv_path + "\n")

    # Setting the url of the AWS file >>> aws_url
    try:
        if cfg.aws_url == "":
            raise
        else:
            global aws_url
            # importing aws_url from cfg.py
            aws_url = cfg.aws_url
    except:
        print("Error: aws_url not found on cfg.py or it is empty. "
              " >>> NO aws_url can be imported.")
        raise
    else:
        print("aws_url successfully imported: aws_url = " + aws_url + "\n")


# Function to import the csv to the dictionary >> d_items
def import_csv():
    # Is the csv_path correct ?
    if os.path.exists(csv_path) is False:
        print("Error: csv_path is not a valid path >>> '" + csv_path + "'")
        raise

    # Unziping and Opening the file
    csv_ungz = gzip.open(csv_path)

    # p counts the number of items in the csv
    p = 0
    for i in csv_ungz:
        p += 1
        # First line is the header, so we are skipping it:
        if p > 1:
            try:
                # get rid of the \n
                i = i.rstrip("\n")
                # Split the row
                i = i.split(b",")

                # Getting the wanted values
                # Getting the id and skipping if the id is not valid
                i_id = i[0].strip()[1:-1].strip()
                if i_id is None or i_id == "":
                    p -= 1
                    continue
                # Getting the name
                i_name = i[1].strip()[1:-1].strip()
                # Getting the brand
                i_brand = i[2].strip()[1:-1].strip()
                # Getting the retailer
                i_retailer = i[3].strip()[1:-1].strip()
                # Getting the price (later check if it is bool)
                i_price = i[4].strip()[1:-1].strip()
                # Getting the in_stock
                i_in_stock = i[5].strip()[1:-1].strip()

                # Converting i_in_stock to a bool if it isn't
                if type(i_in_stock) is None:
                    pass
                elif type(i_in_stock) is bool:
                    pass
                elif type(i_in_stock) is str or type(i_in_stock) is unicode:
                    if i_in_stock.upper() in ("Y", "YES"):
                        i_in_stock = True
                    elif i_in_stock.upper() in ("N", "NO"):
                        i_in_stock = False
                    else:
                        i_in_stock = None
                else:
                    i_in_stock = None

                d_items[i_id] = (i_name, i_brand, i_retailer, i_price,
                                 i_in_stock)

            except:
                print("Error: Something was wrong while inserting line " +
                      str(p) + " of the csv")
                raise

    print(str(p) + " items inserted from the csv.")


def import_json():
    # Retrieving the json
    req = urllib2.Request(aws_url)
    opener = urllib2.build_opener()
    f = opener.open(req)
    aws_json = json.loads(f.read())

    # Parsing the json
    for d in aws_json:
        try:
            # Getting the values
            # Getting the id. If not valid, skipping to next one.
            try:
                i_id = d["id"] if (d["id"] is not None and d["id"] != "") else None
                if i_id is None or i_id == "":
                    continue

            except KeyError:
                i_id = None
            # Getting the name
            try:
                i_name = d[u"name"] if (d[u"name"] is not None and d[u"name"] != "") else None
            except KeyError:
                i_name = None
            # Getting the brand
            try:
                i_brand = d["brand"] if (d["brand"] is not None and d["brand"] != "") else None
            except KeyError:
                i_brand = None
            # Getting the retailer
            try:
                i_retailer = d["retailer"] if (d["retailer"] is not None and d["retailer"] != "") else None
            except KeyError:
                i_retailer = None
            # Getting the price (later check if it is bool)
            try:
                i_price = d["price"] if (d["price"] is not None and d["price"] != "") else None
            except KeyError:
                i_price = None
            # Getting the in_stock
            try:
                i_in_stock = d["in_stock"]
            except KeyError:
                i_in_stock = None

            # Converting i_in_stock to a bool if it isn't
            if type(i_in_stock) is None:
                pass
            elif type(i_in_stock) is bool:
                pass
            elif type(i_in_stock) is str or type(i_in_stock) is unicode:
                if i_in_stock.upper() in ("Y", "YES"):
                    i_in_stock = True
                elif i_in_stock.upper() in ("N", "NO"):
                    i_in_stock = False
                else:
                    i_in_stock = None
            else:
                i_in_stock = None

            # Inserting item in the dictionary
            d_items[i_id] = (i_name, i_brand, i_retailer, i_price,
                             i_in_stock)
        except:
            print("Error: An error was raised while inserting: " + str(d))
            raise


# api pricesearcher
@app.route('/get_item/<item_id>', methods=['GET'])
def index(item_id):
    try:
        # Searching the item
        item_row = d_items[item_id]
    except KeyError:
        print("Error: item_id given doesn't exit")
        msg = "item_id '" + str(item_id) + "' has not been found in our list"
        data_item_d = {'id': item_id, 'Error': "ERR_ID_NOT_FOUND", 'msg': msg}
        data_json = json.dumps(data_item_d)
        return data_json
    except:
        print("Error: Something was wrong while searching item_id '"  + item_id + "'")
        msg = "Something was wrong while searching item_id '" + item_id + "'"
        data_item_d = {'id': item_id, 'Error': "ERR_UNKNOWN", 'msg': msg}
        data_json = json.dumps(data_item_d)
        return data_json

    # Getting the final values we'll sent (item_price turn into float)
    item_name = item_row[0] if (item_row[0] != None and item_row[0] != "") else None
    item_brand = item_row[1] if (item_row[1] != None and item_row[1] != "") else None
    item_retailer = item_row[2] if (item_row[2] != None and item_row[2] != "") else None
    item_price = float(item_row[3]) if (item_row[3] != None and item_row[3] != "") else None
    item_in_stock = item_row[4] if (item_row[4] != None and item_row[4] != "") else None

    # Wrapping the info in a dictonary
    data_item_d = {'id': item_id, 'name': item_name, 'brand': item_brand,
                   'retailer': item_retailer, 'price': item_price,
                   'in_stock': item_in_stock}

    # Converting dict. data_item_d  in a json and sending it out
    data_json = json.dumps(data_item_d)
    return data_json

if __name__ == "__main__":
    print("****************************")
    print("Starting pricesearch.py ....")
    print("****************************")

    # Setting cfg variables
    print("****************************")
    print("Setting cfg variables ....")
    print("****************************")
    set_cfg()
    print("****************************")
    print("cfg variables successfuly set")
    print("****************************")

    # Getting the csv data
    print("****************************")
    print("Starting to Import csv file ....")
    print("****************************")
    import_csv()
    print("****************************")
    print("csv successfully imported")
    print("****************************")

    # Getting the AWS data
    print("****************************")
    print("Starting to Import json data ....")
    print("****************************")
    import_json()
    print("****************************")
    print("json data successfully imported")
    print("****************************")

    # Start the API
    app.run(debug=True)
