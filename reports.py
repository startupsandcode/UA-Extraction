from io import StringIO
import datetime
import pandas as pd
from googleapiclient.discovery import build
from oauth2client.service_account import ServiceAccountCredentials
from timeit import default_timer as timer

# Create a new project in Google Cloud Platform and enable the Analytics Reporting API
# Generate a service account and a new credentials file
# https://developers.google.com/workspace/guides/create-credentials
SCOPES = ['https://www.googleapis.com/auth/analytics.readonly']
KEY_FILE_LOCATION = 'credentials.json' # Path to the credentials file

def initialize_analyticsreporting():
    """Initializes an Analytics Reporting API V4 service object.

  Returns:
    An authorized Analytics Reporting API V4 service object.
  """
    credentials = ServiceAccountCredentials.from_json_keyfile_name(
        KEY_FILE_LOCATION, SCOPES)

    # Build the service object.
    analytics = build('analyticsreporting', 'v4', credentials=credentials)
    return analytics


def get_report(analytics,
               view_id,
               start_date,
               end_date,
               metDims,
               nextPageToken=None):
    """Queries the Analytics Reporting API V4.

  Args:
    analytics: An authorized Analytics Reporting API V4 service object.
  Returns:
    The Analytics Reporting API V4 response.
  """
    try:
        if 'dimensionFilterClauses' in metDims:
            return analytics.reports().batchGet(
                body={
                    'reportRequests': [{
                        'viewId':
                        str(view_id),
                        'pageSize':
                        10000,
                        'pageToken':
                        nextPageToken,
                        'dateRanges': [{
                            'startDate': start_date,
                            'endDate': end_date
                        }],
                        'metrics': [metDims['metrics']],
                        'dimensions': [metDims['dimensions']],
                        'orderBys': [metDims['orderBy']]
                    }]
                }).execute()
        else:
            return analytics.reports().batchGet(
                body={
                    'reportRequests': [{
                        'viewId':
                        str(view_id),
                        'pageSize':
                        10000,
                        'pageToken':
                        nextPageToken,
                        'dateRanges': [{
                            'startDate': start_date,
                            'endDate': end_date
                        }],
                        'metrics': [metDims['metrics']],
                        'dimensions': [metDims['dimensions']]
                    }]
                }).execute()
    except Exception as inst:
        return 'Error: ' + str(inst)

def save_report_to_file(df, file_name):
    csv_buffer = StringIO()
    df.to_csv(csv_buffer, index=False)
    with open('./results/' + file_name, 'w') as f:
        f.write(csv_buffer.getvalue())

def append_report_to_file(df, file_name):
    csv_buffer = StringIO()
    df.to_csv(csv_buffer, index=False)
    with open('./results/' + file_name, 'a') as f:
        f.write(csv_buffer.getvalue())


def print_response(response):
    """Parses and prints the Analytics Reporting API V4 response.

  Args:
    response: An Analytics Reporting API V4 response.
  """
    curResults = []
    if type(response) == str:
        print('*' * 80)
        print(response)
        print('*' * 80)
        return curResults
    for report in response.get('reports', []):
        if 'nextPageToken' in report:
            nextPageToken = report['nextPageToken']

        columnHeader = report.get('columnHeader', {})
        dimensionHeaders = columnHeader.get('dimensions', [])
        metricHeaders = [
            x['name'] for x in columnHeader.get('metricHeader', {}).get(
                'metricHeaderEntries', [])
        ]
        report_headers = ['parsedDate'] + dimensionHeaders + metricHeaders
        curResults.append(report_headers)
        for row in report.get('data', {}).get('rows', []):
            dimensions = row.get('dimensions', [])
            metrics = row.get('metrics', [])
            curDate = datetime.datetime.strptime(dimensions[0], '%Y%m%d')
            curRow = []
            curRow.append(curDate.strftime('%m/%d/%Y'))
            curRow.extend(dimensions)
            curRow.extend(metrics.pop().get('values', []))
            curResults.append(curRow)
    return curResults


def getAllReports(analytics, view_id, start_date, file_name):

    keyMetricsDims = {
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

    locationDims = {
        'metrics': [{
            'expression': 'ga:users',
        },
        {
            'expression': 'ga:sessions',
        },
        {
            'expression': 'ga:pageviews',
        },
        {
            'expression': 'ga:sessionDuration',
        },
        {
            'expression': 'ga:bounces',
        }],
        'dimensions': [
        {
            'name': 'ga:date'
        },{
            'name': 'ga:continent'
        }, {
            'name': 'ga:country'
        }, {
            'name': 'ga:region'
        }, {
            'name': 'ga:city'
        }],
        'filename': 'locations'
    }

    deviceDims = {
        'metrics': [
        {
            'expression': 'ga:users',
        },
        {
            'expression': 'ga:sessions',
        },
        {
            'expression': 'ga:pageviews',
        },
        {
            'expression': 'ga:sessionDuration',
        },
        {
            'expression': 'ga:bounces',
        }
        ],
        'dimensions': [{
            'name': 'ga:date'
        }, {
            'name': 'ga:deviceCategory'
        }, {
            'name': 'ga:screenResolution'
        }, {
            'name': 'ga:browser'
        }, {
            'name': 'ga:operatingSystem'
        }, {
            'name': 'ga:hostname'
        }],
        'filename':
        'devices'
    }

    reportMetricDims = [
        keyMetricsDims, locationDims, deviceDims
    ]

    startDate = start_date
    endDate = datetime.datetime.now().strftime('%Y-%m-%d')
    viewId = view_id
    for index, metricDim in enumerate(reportMetricDims):
        report_data = get_report(analytics, viewId, startDate, endDate,
                                 metricDim)
        response = print_response(report_data)
        if len(response) == 0:
            continue
        df = pd.DataFrame(response[1:], columns=response[0])
        fileToWrite = file_name + '_' + metricDim['filename'] + '.csv'
        save_report_to_file(df, fileToWrite)
        if 'nextPageToken' in report_data['reports'][0]:
            nextPageToken = report_data['reports'][0]['nextPageToken']
            subIndex = 1
            while nextPageToken:
                report_data = get_report(analytics, viewId, startDate, endDate,
                                         metricDim, nextPageToken)
                response = print_response(report_data)
                if len(response) == 0:
                    continue
                df = pd.DataFrame(response[1:], columns=None)
                append_report_to_file(df, fileToWrite)
                subIndex += 1
                if 'nextPageToken' in report_data['reports'][0]:
                    nextPageToken = report_data['reports'][0]['nextPageToken']
                else:
                    nextPageToken = None

def main():
    analytics = initialize_analyticsreporting()

    #loop through the dataframe and print each row
    start = timer()
    print(start)
    df = pd.read_csv('uids.csv')
    
    indexToCheck = [] #use this to finish after a crash
    # I'm printing out the indexes in case an error happens and then you can use the indexToCheck to finish the loop
    
    for index, row in df.iterrows():
        #if index in indexToCheck: # for finishing after a crash
        print(str(index), row['View ID'], row['Start Date'], row['File'])
        getAllReports(analytics, row['View ID'], row['Start Date'], row['File'])
    end = timer()
    print(end - start)  # Time in seconds, e.g. 5.38091952400282
    return


if __name__ == '__main__':
    main()
