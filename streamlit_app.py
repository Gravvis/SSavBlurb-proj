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
MAX_PORT_ATTEMPTS = 7
SAVE_INTERVAL = 3  # Save every 3 seconds

def get_shared_text_file_name():
    host_name = socket.gethostname()
    host_ip = socket.gethostbyname(host_name)
    return f"shared_text_{host_ip.replace('.', '_')}.json"

def save_text(text):
    shared_text_file = get_shared_text_file_name()
    with open(shared_text_file, "w") as f:
        json.dump({"text": text}, f)

def load_text():
    shared_text_file = get_shared_text_file_name()
    if os.path.exists(shared_text_file):
        with open(shared_text_file, "r") as f:
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
    for port_attempt in range(PORT, PORT + MAX_PORT_ATTEMPTS):
        try:
            with socketserver.TCPServer(("", port_attempt), http.server.SimpleHTTPRequestHandler) as httpd:
                st.write(f"Serving at port {port_attempt}")
                httpd.serve_forever()
                break
        except OSError as e:
            if e.errno == 98:  # Address already in use
                if port_attempt == PORT + MAX_PORT_ATTEMPTS - 1:
                    st.error(f"Maximum number of port attempts ({MAX_PORT_ATTEMPTS}) reached. Unable to start the server.")
                    return
                continue
            else:
                raise e

if __name__ == "__main__":
    main()
