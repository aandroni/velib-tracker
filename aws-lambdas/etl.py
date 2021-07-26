import boto3
import urllib3
import json
import time

# Address of public Velib API
API_ADDRESS = "https://velib-metropole-opendata.smoove.pro/opendata/Velib_Metropole/station_status.json"

# Station closest to me is "41605", to find a station see: https://www.velib-metropole.fr/map#/
MY_STATION_CODE = "41605"

# More info about API (in French) at: https://www.velib-metropole.fr/donnees-open-data-gbfs-du-service-velib-metropole

# Connect to DynamoDB
db = boto3.resource("dynamodb")
table = db.Table("bikes")

def download_data():
    '''
    Download data from Velib public API
    '''
    http = urllib3.PoolManager()

    # Download data from API (retry for max 3 times)
    full_data = {}
    try:
        r = http.request("GET", API_ADDRESS, retries=urllib3.util.Retry(3))
        full_data = json.loads(r.data.decode("utf8"))
    except urllib3.exceptions.MaxRetryError as e:
        print(f"API unavailable at {API_ADDRESS}", e)

    return full_data

def etl(event, context):
    '''
    ETL function to get number of bikes available at the station of interest
    '''
    # Get data from all stations
    full_data = download_data()

    # Filter station of interest
    n_bikes = -1
    for entry in full_data["data"]["stations"]:
        if entry["stationCode"] == MY_STATION_CODE:
            # Mechanical (normal) bikes
            n_mechanical = entry["num_bikes_available_types"][0]["mechanical"]
            # Electric bikes
            n_electric = entry["num_bikes_available_types"][1]["ebike"]
            n_bikes = n_mechanical + n_electric
            break
    if n_bikes == -1:
        raise Exception(f"Invalid station code: {MY_STATION_CODE}")

    # Insert into DynamoDB table
    print("Uploading to AWS...")
    table.put_item(Item={
        "timestamp": int(time.time()),
        "n_mechanical": n_mechanical,
        "n_electric": n_electric
    })
    print("Done!")

    return {"statusCode": 200}
