# Welcome to Cloud Functions for Firebase for Python!
# To get started, simply uncomment the below code or create your own.
# Deploy with `firebase deploy`

from firebase_functions import https_fn, options
from firebase_admin import initialize_app
import base64
from werkzeug.datastructures import FileStorage
from werkzeug.utils import secure_filename
import io
import json
import os
from pydub import AudioSegment

#initialize_app()

@https_fn.on_request(
    cors=options.CorsOptions(
        cors_origins="*", 
        cors_methods=["post"]))

def extractAudioData(req: https_fn.Request) -> https_fn.Response:

    if req.method != "POST":
        return https_fn.Response(json.dumps({"response": "Invalid request type, only POST requests are allowed"}), mimetype="application/json", status=405)
    try:
        content_type = req.headers.get('Content-Type', '')
    except:
        return https_fn.Response("Invalid content type in the request", status=500)
    
    if 'multipart/form-data' in content_type:
        if 'audio' in req.files and req.files['audio'].filename != '':

            filename, fileExtension = os.path.splitext(secure_filename(req.files['audio'].filename))


            
            audiofile = req.files['audio']
            req.files['audio'].save(f"tmp/{audiofile.filename}")

            file_path = os.path.join("tmp", audiofile.filename)
            with open(file_path, "rb") as audiofile:
                audioBinary = audiofile.read()



            encodedBytes = base64.b64encode(audioBinary).decode('utf-8')

            response_data = {
                "audio": { 
                "content": encodedBytes,
                "extension": fileExtension,
                "length": "a"
                },
                "length": {

                },
                "result": 1
            }

            


            return https_fn.Response(json.dumps(response_data), mimetype="application/json", status=200)
        else:
            return https_fn.Response("No audio file in the request", status=400)
    
    #This return will execute if the request failed
    return https_fn.Response("internal error", status=500)
        
