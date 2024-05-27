from firebase_functions import https_fn, options
from firebase_admin import initialize_app
import base64
from werkzeug.utils import secure_filename
import io
import json
import os
from pydub import AudioSegment
from pydub.silence import detect_nonsilent

initialize_app()

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
        try:

            filename, fileExtension = os.path.splitext(secure_filename(req.files['audio'].filename))

            audiofile = req.files['audio']

            #reading binary so it can be processed later
            audioBinary = audiofile.read()
            aseg = AudioSegment.from_file(io.BytesIO(audioBinary))

            
            non_silence_ranges = detect_nonsilent(aseg, min_silence_len=10, silence_thresh=-120)
            
            if non_silence_ranges:
                start_trim = non_silence_ranges[0][0]
                end_trim = non_silence_ranges[-1][-1]
                trimmed_audio = aseg[start_trim:end_trim]
                trimmed_audio.export(filename + fileExtension, format="mp4")
                aftertrim = AudioSegment.from_file(filename + fileExtension)

                with open(filename + fileExtension, "rb" ) as audiofile:
                    audioBinary = audiofile.read()
                encodedBytes = base64.b64encode(audioBinary).decode('utf-8')

            response_data = {
                "audio": { 
                "content": encodedBytes,
                "extension": fileExtension,
                }, 
                "length": len(aftertrim) / 1000,
                "result": 1
            }
            return https_fn.Response(json.dumps(response_data), mimetype="application/json", status=200)

        except Exception as e:
            response_data = {
                "result": 2,
                "message": e
            }
            
            return https_fn.Response(json.dumps(response_data), mimetype="application/json", status=400)
    
    #This return will execute if the request failed
    return https_fn.Response("internal error", status=500)
        
