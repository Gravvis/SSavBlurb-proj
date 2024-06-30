import streamlit as st
import os
import socket
import time
from datetime import datetime, timedelta
import json
import http.server
import socketserver
import threading

PORT = 8000
SAVE_INTERVAL = 3  # Save every 3 seconds

def save_text(text):
    current_time = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    filename = f"saved_text_{current_time}.json"
    with open(filename, "w") as f:
        json.dump({"text": text}, f)

def load_text():
    files = [f for f in os.listdir() if f.startswith("saved_text_")]
    if files:
        latest_file = max(files, key=lambda x: os.path.getmtime(x))
        with open(latest_file, "r") as f:
            data = json.load(f)
            return data["text"]
    return ""

def main():
    st.set_page_config(page_title="SSavBlurb", layout="wide")

    # Set the background color and font styles
    st.markdown(
        """
        <style>
        body {
            background-color: #f0f8ff;
            font-family: 'Montserrat', sans-serif;
        }
        h1 {
            color: #6495ed;
            font-family: 'Pacifico', cursive;
        }
        p {
            color: #778899;
        }
        textarea {
            background-color: #f0f8ff;
            border: 1px solid #6495ed;
            border-radius: 5px;
            font-family: 'Montserrat', sans-serif;
        }
        button {
            background-color: #6495ed;
            color: white;
            border: none;
            border-radius: 5px;
            padding: 10px 20px;
            font-family: 'Montserrat', sans-serif;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    st.title("SSavBlurb")
    st.write("A simple tool to share text across devices on the same Wi-Fi network.")

    host_name = socket.gethostname()
    host_ip = socket.gethostbyname(host_name)
    st.write(f"Your device's IP address: {host_ip}")

    with st.container():
        st.markdown("## Shared Text")
        shared_text = st.text_area("", height=400, key="shared_text", value=load_text(), disabled=False)

        def autosave_text():
            while True:
                time.sleep(SAVE_INTERVAL)
                save_text(shared_text)

        autosave_thread = threading.Thread(target=autosave_text)
        autosave_thread.daemon = True
        autosave_thread.start()

    # Start the local HTTP server
    with socketserver.TCPServer(("", PORT), http.server.SimpleHTTPRequestHandler) as httpd:
        st.write(f"Serving at port {PORT}")
        httpd.serve_forever()

if __name__ == "__main__":
    main()
