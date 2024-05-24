from pydub import AudioSegment
import os
import io


script_dir = os.path.dirname(__file__)
file_path = os.path.join(script_dir, './tmp/10001100-213.mp4')


data = open(file_path, 'rb').read()

#AudioSegment.from_file(io.BytesIO(data), format="mp4")