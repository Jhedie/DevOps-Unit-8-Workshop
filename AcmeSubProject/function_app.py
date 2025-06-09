import azure.functions as func
import datetime
import time
import json
import logging

import uuid


app = func.FunctionApp()


def translate(subtitle):
    # Simulate a translation process
    # In a real-world scenario, this would call an external translation service
    return subtitle[::-1]  # Just reversing the string for demonstration purposes

@app.table_output(
    arg_name="table",
    connection="AzureWebJobsStorage",
    table_name="AcmeTranslations",
    partition_key="table"
)
@app.route(route="AddSubtitle", auth_level=func.AuthLevel.ANONYMOUS)
def AddSubtitle(req: func.HttpRequest, table: func.Out[str]) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')

    start = time.time()

    req_body = req.get_json()
    subtitle = req_body.get('subtitle')
    row_key = str(uuid.uuid4())
    #create the table entity
    entity = {
        "PartitionKey": "table",
        "RowKey": row_key,
        "Subtitle": subtitle
    }
    # Add the entity to the table output
    table.set(json.dumps(entity))

    end = time.time()

    processing_time = end - start
    return func.HttpResponse(
            f"Translation is: {subtitle} and it took {processing_time} seconds to process.",
            status_code=200
    )
