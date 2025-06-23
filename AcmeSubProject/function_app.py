import azure.functions as func
import datetime
import json
import logging
import uuid
import typing

app = func.FunctionApp()


@app.route(route="AddSubtitle", auth_level=func.AuthLevel.ANONYMOUS)
@app.table_output(
    arg_name="table",
    connection="AzureWebJobsStorage",
    table_name="AcmeTranslations",
    partition_key="Subtitles"
)
@app.queue_output(
    arg_name="queue",
    queue_name="acmesub-translations-queue",
    connection="AzureWebJobsStorage"
)
def AddSubtitle(req: func.HttpRequest, table: func.Out[str], queue: func.Out[typing.List[str]]) -> func.HttpResponse:
    logging.info('Processing AddSubtitle request.')
    try:
        req_body = req.get_json()
        subtitle = req_body.get('subtitle')
        languages = req_body.get('languages')

        if not subtitle or not languages:
            return func.HttpResponse("Invalid request: subtitle and languages are required", status_code=400)

        row_key = str(uuid.uuid4())

        # Create entity with required RowKey
        entity = {
            "rowKey": row_key,
            "subtitle": subtitle,
            "partitionKey": "Subtitles",
        }
        table.set(entity)  # Pass dictionary directly
        logging.info(f"Subtitle added with RowKey: {row_key}")
        # Prepare queue messages
        queue_messages = []
        for language in languages:
            message = {
                "rowKey": row_key,
                "languageCode": language,
            }
            queue_messages.append(json.dumps(message))

        queue.set(queue_messages)

        return func.HttpResponse("OK", status_code=200)

    except Exception as e:
        logging.error(f"Error processing request: {str(e)}")
        return func.HttpResponse("Internal server error", status_code=500)





@app.queue_trigger(arg_name="queue",
    queue_name="acmesub-translations-queue",
    connection="AzureWebJobsStorage"
)
def MyQueueTrigger(queue: func.QueueMessage):
    logging.info('Python Queue trigger processed a message: %s',
                queue.get_body().decode('utf-8'))
    # log messages to console
    message = json.loads(queue.get_body().decode('utf-8'))
    logging.info(f"Processing translation for RowKey: {message['rowKey']} in language: {message['languageCode']}")
    
