# Voice Notes Transcription Setup Guide

## Prerequisites

- Mac Mini M4 (Apple Silicon)
- macOS with Homebrew installed
- Python 3.9 or higher
- Git

## 1. Install mlx-voxtral

mlx-voxtral is an optimized voice transcription library for Apple Silicon that runs natively without requiring Ollama.

### Install via pip
```bash
pip install mlx-voxtral
```

Or using Bun:
```bash
bun install mlx-voxtral
```

### Verify Installation
```bash
python -c "from mlx_voxtral.transcriber import Transcriber; print('mlx-voxtral installed successfully')"
```

On first use, the model will be downloaded automatically to your local cache. This may take a few minutes on first run.

## 2. Install Ollama

Ollama is used only for summarization and title generation.

### Download and Install
```bash
curl -fsSL https://ollama.com/install.sh | sh
```

Or download from: https://ollama.com/download

### Start Ollama Service
```bash
ollama serve
```

This will start the Ollama server on `http://localhost:11434`

### Pull Summarization Model

**Mistral Model (for summarization):**
```bash
ollama pull mistral
```

### Verify Model
```bash
ollama list
```

You should see `mistral` in the list.

### Configure Ollama to Run at Startup

Create a launchd plist for Ollama:
```bash
cat > ~/Library/LaunchAgents/com.ollama.server.plist <<EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.ollama.server</string>
    <key>ProgramArguments</key>
    <array>
        <string>/usr/local/bin/ollama</string>
        <string>serve</string>
    </array>
    <key>RunAtLoad</key>
    <true/>
    <key>KeepAlive</key>
    <true/>
    <key>StandardOutPath</key>
    <string>/tmp/ollama.out</string>
    <key>StandardErrorPath</key>
    <string>/tmp/ollama.err</string>
</dict>
</plist>
EOF

launchctl load ~/Library/LaunchAgents/com.ollama.server.plist
```

## 3. Repository Setup

### Clone or Copy Repository
```bash
cd ~/Documents
git clone https://github.com/mischewu/voice-notes-transcriber.git
cd voice-notes-transcriber
```

Or if copying manually:
```bash
cp -r /path/to/voice-notes-transcriber ./
cd voice-notes-transcriber
```

### Install Python Dependencies
```bash
pip install mlx-voxtral ollama
```

Or using Bun:
```bash
bun install mlx-voxtral ollama
```

### Configure Paths

Edit `processor.py` and update the following path variables:

```python
QUEUE_DIR = "/Users/yourusername/Documents/voice-notes/queue"
ARCHIVE_DIR = "/Users/yourusername/Documents/voice-notes/archive"
OBSIDIAN_OUTPUT_DIR = "/Users/yourusername/Documents/ObsidianVault/VoiceNotes"
OBSIDIAN_TEMPLATE_PATH = "/Users/yourusername/Documents/ObsidianVault/Templates/voice-note-template.md"
```

### Create Directory Structure
```bash
mkdir -p ~/Documents/voice-notes/queue
mkdir -p ~/Documents/voice-notes/archive
mkdir -p ~/Documents/ObsidianVault/VoiceNotes
mkdir -p ~/Documents/ObsidianVault/Templates
```

## 4. Create Obsidian Template

Create the template file at your configured `OBSIDIAN_TEMPLATE_PATH`:

```markdown
---
created: {{DATE}}
type: voice-note
original: {{ORIGINAL_FILE}}
---

# {{TITLE}}

**Date:** {{DATE}}
**Time:** {{TIME}}
**Original File:** {{ORIGINAL_FILE}}

## Transcript

{{TRANSCRIPT}}
```

## 5. Test the Processor

Test manually before setting up the service:

```bash
python processor.py
```

Drop a test audio file into your queue directory and verify:
- Transcription occurs (using mlx-voxtral)
- Summary is generated (using Ollama Mistral)
- Note is created in Obsidian directory
- Original file is moved to archive

Press `Ctrl+C` to stop the test.

## 6. Install as System Service

### Update setup_service.sh

Edit `setup_service.sh` and update the paths:

```bash
<string>/usr/local/bin/python3</string>
<string>/Users/yourusername/Documents/voice-notes-transcriber/processor.py</string>
```

Find your Python path:
```bash
which python3
```

### Run Setup Script
```bash
chmod +x setup_service.sh
./setup_service.sh
```

### Verify Service is Running
```bash
launchctl list | grep voicenotes
```

### Check Logs
```bash
tail -f /tmp/voicenotes.out
tail -f /tmp/voicenotes.err
```

## 7. Managing the Service

### Stop Service
```bash
launchctl unload ~/Library/LaunchAgents/com.local.voicenotes.plist
```

### Start Service
```bash
launchctl load ~/Library/LaunchAgents/com.local.voicenotes.plist
```

### Restart Service
```bash
launchctl unload ~/Library/LaunchAgents/com.local.voicenotes.plist
launchctl load ~/Library/LaunchAgents/com.local.voicenotes.plist
```

## Troubleshooting

### mlx-voxtral Not Working

```bash
# Verify installation
python -c "from mlx_voxtral.transcriber import Transcriber; t = Transcriber(); print('mlx-voxtral working')"

# Check for sufficient disk space (models require ~1-2GB)
df -h

# Reinstall if needed
pip install --upgrade mlx-voxtral
```

### Ollama Not Responding
```bash
# Check if Ollama is running
ps aux | grep ollama

# Restart Ollama
launchctl unload ~/Library/LaunchAgents/com.ollama.server.plist
launchctl load ~/Library/LaunchAgents/com.ollama.server.plist

# Test Ollama connection
curl http://localhost:11434/api/tags
```

### Mistral Model Not Found
```bash
# Re-pull the model
ollama pull mistral

# Verify it's installed
ollama list
```

### Processor Not Starting
```bash
# Check error logs
cat /tmp/voicenotes.err

# Test Python script manually
python3 processor.py

# Check for Python dependency issues
python3 -c "import mlx_voxtral; import ollama; print('All dependencies OK')"
```

### Permission Issues
```bash
# Ensure directories are writable
chmod -R 755 ~/Documents/voice-notes
chmod -R 755 ~/Documents/ObsidianVault
```

### Audio Files Not Processing

Check that file extensions are lowercase. The processor looks for:
- `.mp3`, `.m4a`, `.wav`, `.m4v`, `.opus`, `.flac`

If files use uppercase extensions (`.MP3`), either rename them or add the extensions to `AUDIO_EXTENSIONS` in `processor.py`.

## Model Selection

### Transcription
mlx-voxtral uses the **Voxtral Mini 3B** model, which is optimized for Apple Silicon and offers excellent performance on M4 Macs.

### Summarization
To use a different summarization model, edit `processor.py`:

```python
SUMMARIZATION_MODEL = "mistral"  # or "llama2", "neural-chat", "orca-mini", etc.
```

Then pull the new model:
```bash
ollama pull <model-name>
```

## Performance Notes

- **First run:** mlx-voxtral will download the model (~1-2GB) on first use. Subsequent runs will be faster.
- **Transcription speed:** Varies with audio length. A 5-minute audio file typically takes 1-2 minutes on M4.
- **Summarization speed:** Typically 5-30 seconds depending on transcript length and Ollama model.

## Syncthing Integration

If using Syncthing to sync the queue directory:

1. Ensure the 2-second delay in `is_file_ready()` is sufficient
2. Consider increasing the delay if files are large:
   ```python
   time.sleep(5)  # Increase from 2 to 5 seconds
   ```

3. Syncthing should be configured to ignore temporary files:
   ```
   .syncthing.*
   .stfolder
   ```
