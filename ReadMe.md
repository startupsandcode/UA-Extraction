# UA Extraction

This is a simple repo that allows you to extract your google analytics UA metrics and dimensions into a csv file.  

You will need to setup a project in GCP and create a service account with the correct permissions.  You will then need to download the credentials.json file and place it in the root of the repo.  

### Here are instructions on how to do that part:  
https://developers.google.com/docs/api/quickstart/python

## How to use

1. Clone the repo
2. Create a virtual environment: `python3 -m venv venv`
3. Activate the virtual environment: `source venv/bin/activate`
4. Install the requirements: `pip install -r requirements.txt`
5. Create a credentials.json file in the root of the repo (see above)
6. Create a uids.csv file in the root of the repo 
7. Add the report objects to the reports.py file in the GetAllReports function (see below)
7. Run the script: `python reports.py`

### UID File
The Uids.csv file should have the following format:

```
View ID,Start Date,File
123456789,2019-01-01,myWebSite
```

### Report Objects
The report objects are created using the Google Analytics Reporting API v4.  You can find the documentation here: https://developers.google.com/analytics/devguides/reporting/core/v4/rest/v4/reports/batchGet
You can browse all the metrics/dimensions here: https://developers.google.com/analytics/devguides/reporting/core/dimsmets

Here is an example of a report object for this repo:  
NOTE: Do not forget to add the filename to the report object.  This will be used to name the csv file.
```
{
        'metrics': [{
            'expression': 'ga:users',
        }, {
            'expression': 'ga:bounces',
        }, {
            'expression': 'ga:sessions',
        }, {
            'expression': 'ga:pageviews',
        }, {
            'expression': 'ga:pageviewsPerSession',
        }, {
            'expression': 'ga:sessionDuration',
        }],
        'dimensions': [{
            'name': 'ga:date'
        }],
        'filename':
        'key_metrics'
    }
```


