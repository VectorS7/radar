# Audio Streaming Project

This project streams audio from a local client (e.g., Foobar2000 via VB-Audio Virtual Cable) to a remote server, which then broadcasts it via HTTP.

## Structure
- `server.py`: Server script to accept audio stream and serve it via HTTP.
- `client.py`: Client script to capture and send audio to the server.
- `requirements.txt`: Python dependencies.

## Setup
1. **Install Dependencies:**
   ```bash
   pip install -r requirements.txt
