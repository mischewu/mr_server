import os
import time
import shutil
import re
from datetime import datetime
from mlx_voxtral.transcriber import Transcriber
from ollama import Client

QUEUE_DIR = "/path/to/queue"
ARCHIVE_DIR = "/path/to/archive"
OBSIDIAN_OUTPUT_DIR = "/path/to/obsidian"
OBSIDIAN_TEMPLATE_PATH = "/path/to/template.md"

SUMMARIZATION_MODEL = "mistral"

AUDIO_EXTENSIONS = [".mp3", ".m4a", ".wav", ".m4v", ".opus", ".flac"]

transcriber = Transcriber()
ollama_client = Client()

def transcribe_audio(file_path):
    try:
        result = transcriber.transcribe(file_path)
        return result['text']
    except Exception as e:
        print(f"Transcription error for {file_path}: {e}")
        raise

def generate_summary(transcript):
    try:
        prompt = f"""Generate a strict 2-4 word title for this transcript. 
Only return the title, nothing else.

Transcript: {transcript}"""
        
        response = ollama_client.generate(
            model=SUMMARIZATION_MODEL,
            prompt=prompt
        )
        
        summary = response['response'].strip()
        return summary
    except Exception as e:
        print(f"Summarization error: {e}")
        return "voice-note"

def sanitize_filename(text):
    text = text.lower()
    text = text.replace(" ", "-")
    text = re.sub(r'[^a-z0-9-]', '', text)
    text = text[:50] if text else "voice-note"
    
    if not text or len(text) < 2:
        text = "voice-note"
    
    return text

def create_note(file_path, title, transcript):
    try:
        if not os.path.exists(OBSIDIAN_TEMPLATE_PATH):
            raise FileNotFoundError(f"Template not found: {OBSIDIAN_TEMPLATE_PATH}")
        
        with open(OBSIDIAN_TEMPLATE_PATH, 'r') as template_file:
            template = template_file.read()
        
        date_str = datetime.now().strftime("%Y-%m-%d")
        time_str = datetime.now().strftime("%H:%M:%S")
        
        note_content = template.replace("{{DATE}}", date_str)
        note_content = note_content.replace("{{TIME}}", time_str)
        note_content = note_content.replace("{{ORIGINAL_FILE}}", os.path.basename(file_path))
        note_content = note_content.replace("{{TITLE}}", title)
        note_content = note_content.replace("{{TRANSCRIPT}}", transcript)
        
        return note_content
    except Exception as e:
        print(f"Error creating note: {e}")
        raise

def save_note(content, title):
    try:
        os.makedirs(OBSIDIAN_OUTPUT_DIR, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        note_filename = f"{timestamp}-{title}.md"
        note_path = os.path.join(OBSIDIAN_OUTPUT_DIR, note_filename)
        
        with open(note_path, 'w') as note_file:
            note_file.write(content)
        
        print(f"Note saved: {note_path}")
    except Exception as e:
        print(f"Error saving note: {e}")
        raise

def archive_file(file_path):
    try:
        os.makedirs(ARCHIVE_DIR, exist_ok=True)
        
        filename = os.path.basename(file_path)
        archive_path = os.path.join(ARCHIVE_DIR, filename)
        
        if os.path.exists(archive_path):
            timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
            name, ext = os.path.splitext(filename)
            archive_path = os.path.join(ARCHIVE_DIR, f"{name}-{timestamp}{ext}")
        
        shutil.move(file_path, archive_path)
        print(f"File archived: {archive_path}")
    except Exception as e:
        print(f"Error archiving file: {e}")
        raise

def process_audio_file(file_path):
    try:
        print(f"Processing: {file_path}")
        
        transcript = transcribe_audio(file_path)
        print(f"Transcription complete")
        
        summary = generate_summary(transcript)
        print(f"Summary generated: {summary}")
        
        sanitized_title = sanitize_filename(summary)
        print(f"Sanitized title: {sanitized_title}")
        
        note_content = create_note(file_path, sanitized_title, transcript)
        
        save_note(note_content, sanitized_title)
        
        archive_file(file_path)
        
        print(f"Successfully processed: {file_path}\n")
        
    except Exception as e:
        print(f"Failed to process {file_path}: {e}")
        print("Continuing to next file...\n")

def is_file_ready(file_path):
    try:
        initial_size = os.path.getsize(file_path)
        time.sleep(2)
        final_size = os.path.getsize(file_path)
        return initial_size == final_size
    except:
        return False

def main():
    print("Voice notes processor started")
    print(f"Watching: {QUEUE_DIR}")
    print(f"Archive: {ARCHIVE_DIR}")
    print(f"Output: {OBSIDIAN_OUTPUT_DIR}")
    print(f"Template: {OBSIDIAN_TEMPLATE_PATH}\n")
    
    os.makedirs(QUEUE_DIR, exist_ok=True)
    os.makedirs(ARCHIVE_DIR, exist_ok=True)
    os.makedirs(OBSIDIAN_OUTPUT_DIR, exist_ok=True)
    
    while True:
        try:
            if not os.path.exists(QUEUE_DIR):
                print(f"Queue directory not found: {QUEUE_DIR}")
                time.sleep(10)
                continue
            
            files = os.listdir(QUEUE_DIR)
            audio_files = [f for f in files if any(f.lower().endswith(ext) for ext in AUDIO_EXTENSIONS)]
            
            for filename in audio_files:
                file_path = os.path.join(QUEUE_DIR, filename)
                
                if os.path.isfile(file_path) and is_file_ready(file_path):
                    process_audio_file(file_path)
            
            time.sleep(5)
            
        except KeyboardInterrupt:
            print("\nShutting down processor...")
            break
        except Exception as e:
            print(f"Error in main loop: {e}")
            time.sleep(10)

if __name__ == "__main__":
    main()
