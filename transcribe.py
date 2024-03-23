'''
generate subtitle from mp4 
(mp4 to vtt)
fatahfd [at] gmail.com
23.02.2024
purpose : resolve error Google Web Speech API; recognition connection failed: [Errno 32] Broken pipe
'''

import moviepy.editor as mp
import speech_recognition as sr
import os
def extract_audio_chunks(video_path, audio_chunk_dir):
    # Load the video file
    video = mp.VideoFileClip(video_path)
    
    # Calculate total duration of the video
    total_duration = video.duration
    
    # Split audio into 20-second chunks
    chunk_times = [(start, min(start + 20, total_duration)) for start in range(0, int(total_duration), 20)]
    
    # Extract audio chunks
    for i, (start, end) in enumerate(chunk_times):
        audio_chunk = video.subclip(start, end)
        audio_chunk_path = f"{audio_chunk_dir}/chunk_{i+1}.wav"
        audio_chunk.audio.write_audiofile(audio_chunk_path)

def transcribe_audio_chunks(audio_chunk_dir):
    transcripts = []
    for i in range(1, 1000):  # Assuming there are fewer than 1000 audio chunks
        audio_chunk_path = f"{audio_chunk_dir}/chunk_{i}.wav"
        try:
            recognizer = sr.Recognizer()
            with sr.AudioFile(audio_chunk_path) as source:
                audio_data = recognizer.record(source)
                transcript = recognizer.recognize_google(audio_data)
                transcripts.append(transcript)
        except FileNotFoundError:
            break
    return transcripts

def generate_vtt(transcripts):
    vtt_content = "WEBVTT\n\n"
    start_time = 0
    for i, transcript in enumerate(transcripts):
        end_time = start_time + 20  # Each chunk is 20 seconds long
        vtt_content += f"{convert_to_vtt_time(start_time)} --> {convert_to_vtt_time(end_time)}\n"
        vtt_content += f"{transcript}\n\n"
        start_time = end_time
    return vtt_content

def convert_to_vtt_time(time):
    hours = int(time / 3600)
    minutes = int((time % 3600) / 60)
    seconds = int(time % 60)
    milliseconds = int((time - int(time)) * 1000)
    return f"{hours:02d}:{minutes:02d}:{seconds:02d}.{milliseconds:03d}"
def replace_extension(filename):
    if filename.endswith(".mp4"):
        return filename[:-4] + ".vtt"
    else:
        return filename
def delete_files_in_directory(directory):
    # Iterate over all files in the directory
    for filename in os.listdir(directory):
        # Construct the full file path
        file_path = os.path.join(directory, filename)
        # Check if the path is a file (not a directory)
        if os.path.isfile(file_path):
            # Delete the file
            os.remove(file_path)
            print(f"Deleted {file_path}")        
if __name__ == "__main__":
    import sys

    if len(sys.argv) != 2:
        print("Usage: python script.py <video_path> ")
    else:
        video_path = sys.argv[1]
        output_filename  = replace_extension(video_path)
        audio_chunk_dir = "/var/www/html/repo/audio_chunks"
        print("delete chunk audio")
        delete_files_in_directory(audio_chunk_dir)
        print("extract audio.")
        extract_audio_chunks(video_path, audio_chunk_dir)
        print("transcribe_audio_chunks")
        transcripts = transcribe_audio_chunks(audio_chunk_dir)
        print("generate_vtt")
        vtt_content = generate_vtt(transcripts)
        print("save file")
        with open(output_filename, "w") as f:
            f.write(vtt_content)
        print("WebVTT file generated successfully.")
 
