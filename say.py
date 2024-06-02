import pandas as pd
from gtts import gTTS
import os
from pydub import AudioSegment

# Function to generate TTS for a given text
def generate_tts(text, filename):
    tts = gTTS(text=text, lang='en')
    tts.save(filename)

# Function to change the speed of an audio segment
def change_speed(audio_segment, speed=1.0):
    return audio_segment._spawn(audio_segment.raw_data, overrides={
        "frame_rate": int(audio_segment.frame_rate * speed)
    }).set_frame_rate(audio_segment.frame_rate)

# Read the CSV file
file_path = '~/Downloads/words.csv'  # Replace with the path to your CSV file
df = pd.read_csv(file_path)

# Initialize an empty AudioSegment
combined = AudioSegment.silent(duration=0)

# Iterate through each row in the DataFrame
for index, row in df.iterrows():
    word = row['word']
    meaning = row['meaning']
    usage = row['usage example']
    synonyms = row['synonym']

    print(f"Running for word {index}: {word}")
    # Create filenames for word, meaning, usage, and synonyms
    word_filename = f"word_{index}.mp3"
    meaning_filename = f"meaning_{index}.mp3"
    usage_filename = f"usage_{index}.mp3"
    synonyms_filename = f"synonyms_{index}.mp3"

    # Generate TTS for word with its index
    generate_tts(f"{index + 1}. {word}", word_filename)

    # Generate TTS for meaning
    generate_tts(meaning, meaning_filename)

    # Load the audio files
    word_audio = AudioSegment.from_file(word_filename)
    meaning_audio = AudioSegment.from_file(meaning_filename)

    # Increase the speed of the audio by 25%
    word_audio = change_speed(word_audio, 1.25)
    meaning_audio = change_speed(meaning_audio, 1.25)

    # Append to the combined audio segment
    combined += word_audio
    combined += AudioSegment.silent(duration=3000)  # 3 seconds silence before meaning
    combined += meaning_audio
    combined += AudioSegment.silent(duration=1000)  # 1 second silence after meaning

    # Process usage example if not null/empty
    if pd.notnull(usage) or (isinstance(usage, str) and usage.strip()):
        generate_tts("Usage", usage_filename)
        generate_tts(usage, f"usage_text_{index}.mp3")

        usage_audio = AudioSegment.from_file(usage_filename)
        usage_text_audio = AudioSegment.from_file(f"usage_text_{index}.mp3")

        usage_audio = change_speed(usage_audio, 1.25)
        usage_text_audio = change_speed(usage_text_audio, 1.25)

        combined += usage_audio
        combined += AudioSegment.silent(duration=1000)  # 1 second silence before usage example
        combined += usage_text_audio
        combined += AudioSegment.silent(duration=1000)  # 1 second silence after usage example

        os.remove(usage_filename)
        os.remove(f"usage_text_{index}.mp3")

    # Process synonyms if not null/empty
    if pd.notnull(synonyms) or (isinstance(synonyms, str) and synonyms.strip()):
        generate_tts("Synonyms", synonyms_filename)
        generate_tts(synonyms, f"synonyms_text_{index}.mp3")

        synonyms_audio = AudioSegment.from_file(synonyms_filename)
        synonyms_text_audio = AudioSegment.from_file(f"synonyms_text_{index}.mp3")

        synonyms_audio = change_speed(synonyms_audio, 1.25)
        synonyms_text_audio = change_speed(synonyms_text_audio, 1.25)

        combined += synonyms_audio
        combined += AudioSegment.silent(duration=1000)  # 1 second silence before synonyms
        combined += synonyms_text_audio
        combined += AudioSegment.silent(duration=1000)  # 1 second silence after synonyms

        os.remove(synonyms_filename)
        os.remove(f"synonyms_text_{index}.mp3")

    # Remove temporary files for word and meaning
    os.remove(word_filename)
    os.remove(meaning_filename)

# Export the combined audio
output_filename = "combined_audio.mp3"
combined.export(output_filename, format='mp3')

print(f"Combined audio file created: {output_filename}")
