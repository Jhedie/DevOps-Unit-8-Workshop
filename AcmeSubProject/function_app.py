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
@app.table_input(arg_name="table",
    connection="AzureWebJobsStorage",
    table_name="AcmeTranslations",
    partition_key="Subtitles")
@app.table_output(arg_name="output",
    connection="AzureWebJobsStorage",
    table_name="AcmeTranslatedSubtitles",
    partition_key="TranslatedSubtitles")
def MyQueueTrigger(queue: func.QueueMessage, table: str, output: func.Out[str]) -> None:
    logging.info('Python Queue trigger processed a message: %s',
                queue.get_body().decode('utf-8'))

    try:
        # Parse the queue message
        message_body = queue.get_body().decode('utf-8')
        message = json.loads(message_body)
        
        logging.info(f"Parsed message: {message}")
        logging.info(f"Message type: {type(message)}")

        # Extract rowKey and languageCode from the message
        row_key = message.get('rowKey') if isinstance(message, dict) else None
        language_code = message.get('languageCode') if isinstance(message, dict) else None
        
        if not row_key or not language_code:
            logging.error(f"Invalid message format. Expected dict with rowKey and languageCode, got: {message}")
            return
        
        table_data = json.loads(table)
        # Retrieve the subtitle entity from the table
        logging.info(f"Retrieved table data: {table_data}")
        if len(table_data) > 0:
            # Find the entity with matching rowKey
            subtitle_entity = None
            for entity in table_data:
                if entity.get('RowKey') == row_key or entity.get('rowKey') == row_key:
                    subtitle_entity = entity
                    break
            if not subtitle_entity:
                # If no exact match, take the first one (fallback)
                subtitle_entity = table_data[0]
                logging.warning(f"No exact rowKey match found, using first entity")
        else:
            logging.error("Table data array is empty")
            return

        if not subtitle_entity:
            logging.error(f"No subtitle entity found for RowKey: {row_key}")
            return
        
        # Simulate translation (in a real scenario, you would call an external translation service)
        translated_subtitle = subtitle_entity['subtitle'].upper()
        logging.info(f"Translated subtitle: {translated_subtitle}")
        
        # Create the output entity
        output_entity = {
            "rowKey": str(uuid.uuid4()),
            "languageCode": language_code,
            "translatedSubtitle": translated_subtitle,
            "partitionKey": "TranslatedSubtitles",
            "timestamp": datetime.datetime.utcnow().isoformat()
        }
        # Set the output entity to the output binding
        output.set(output_entity)
        logging.info(f"Output entity set: {output_entity}")


    except json.JSONDecodeError as e:
        logging.error(f"Error parsing JSON: {str(e)}")
    except Exception as e:
        logging.error(f"Error processing queue message: {str(e)}")
        logging.error(f"Queue message content: {queue.get_body().decode('utf-8')}")
