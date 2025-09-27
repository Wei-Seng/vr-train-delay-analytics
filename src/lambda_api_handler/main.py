import json
import boto3 # type: ignore
import time
import os

# --- CONFIGURATION ---
# These are set via environment variables in the Terraform script.
ATHENA_OUTPUT_LOCATION = os.environ['ATHENA_OUTPUT_LOCATION']
DATABASE_NAME = os.environ['ATHENA_DATABASE']
TABLE_NAME = os.environ['ATHENA_TABLE']
# ---

athena_client = boto3.client('athena')


def handler(event, context):
    """
    This function is triggered by API Gateway. It queries Athena for the top 5
    most delayed train types and returns the result.
    """

    # This SQL query runs on the clean data Person A created.
    query = f"""
    SELECT trainType, AVG(delay_minutes) as avg_delay
    FROM "{TABLE_NAME}"
    WHERE delay_minutes > 0
    GROUP BY trainType
    ORDER BY avg_delay DESC
    LIMIT 5;
    """

    print(f"Executing Athena query on table {TABLE_NAME}...")

    try:
        # Step 1: Start the query execution.
        response = athena_client.start_query_execution(
            QueryString=query,
            QueryExecutionContext={'Database': DATABASE_NAME},
            ResultConfiguration={'OutputLocation': ATHENA_OUTPUT_LOCATION}
        )
        query_execution_id = response['QueryExecutionId']

        # Step 2: Wait for the query to finish.
        while True:
            stats = athena_client.get_query_execution(QueryExecutionId=query_execution_id)
            status = stats['QueryExecution']['Status']['State']
            if status in ['SUCCEEDED', 'FAILED', 'CANCELLED']:
                if status != 'SUCCEEDED':
                    raise Exception(
                        f"Athena query failed: {stats['QueryExecution']['Status'].get('StateChangeReason')}"
                    )
                break
            time.sleep(1)

        # Step 3: Fetch and format the results.
        results_paginator = athena_client.get_paginator('get_query_results')
        results_iter = results_paginator.paginate(QueryExecutionId=query_execution_id)

        rows = []
        header = [
            col['Name']
            for col in results_iter.build_full_result()['ResultSet']['ResultSetMetadata']['ColumnInfo']
        ]

        for page in results_iter:
            for row in page['ResultSet']['Rows'][1:]:  # Skip header row
                values = [col.get('VarCharValue') for col in row['Data']]
                rows.append(dict(zip(header, values)))

        # Step 4: Return a successful HTTP response.
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps(rows, indent=2)
        }

    except Exception as e:
        print(f"Error: {e}")
        # Return an error HTTP response.
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }
