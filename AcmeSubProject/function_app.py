import azure.functions as func
import datetime
import time
import json
import logging

app = func.FunctionApp()


def translate(subtitle):
    # Simulate a translation process
    # In a real-world scenario, this would call an external translation service
    return subtitle[::-1]  # Just reversing the string for demonstration purposes

@app.route(route="AddSubtitle", auth_level=func.AuthLevel.ANONYMOUS)
def AddSubtitle(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')

    start = time.time()

    req_body = req.get_json()
    subtitle = req_body.get('subtitle')
    
    translated = translate(subtitle)

    time.sleep(5)  # Simulating 5 seconds of cpu-intensive processing
    end = time.time()

    processing_time = end - start 
    return func.HttpResponse(
            f"Processing took {str(processing_time)} seconds. Translation is: {translated}",
            status_code=200
    )
