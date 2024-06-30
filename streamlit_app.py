import streamlit as st
import os
import socket
import time
import json
import threading
import http.server
import socketserver
import fcntl
import contextlib

PORT = 8000
MAX_PORT_ATTEMPTS = 10
SAVE_INTERVAL = 3  # Save every 3 seconds

def get_shared_text_file_name():
    host_name = socket.gethostname()
    host_ip = socket.gethostbyname(host_name)
    return f"shared_text_{host_ip.replace('.', '_')}.json"

@contextlib.contextmanager
def file_lock(filename):
    with open(filename, 'w') as f:
        try:
            fcntl.flock(f, fcntl.LOCK_EX)
            yield
        finally:
            fcntl.flock(f, fcntl.LOCK_UN)

@st.cache(allow_output_mutation=True)
def get_shared_text():
    shared_text_file = get_shared_text_file_name()
    try:
        os.makedirs(os.path.dirname(shared_text_file), exist_ok=True)
    except OSError:
        pass
    if not os.path.exists(shared_text_file):
        open(shared_text_file, 'w').close()
        os.chmod(shared_text_file, 0o666)
    return load_text(shared_text_file)

def load_text(shared_text_file):
    if os.path.exists(shared_text_file):
        with open(shared_text_file, "r") as f:
            data = json.load(f)
            return data["text"]
    return ""

def save_text(text, shared_text_file):
    with file_lock(shared_text_file):
        with open(shared_text_file, "w") as f:
            json.dump({"text": text}, f)

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

    shared_text_file = get_shared_text_file_name()

    with st.container():
        st.markdown("## Shared Text")
        shared_text_value = st.text_area("", height=400, value=get_shared_text(), disabled=False, key="shared_text_area")

        lock = threading.Lock()
        last_saved_text = get_shared_text()

        def update_shared_text():
            while True:
                time.sleep(SAVE_INTERVAL)
                with file_lock(shared_text_file):
                    if shared_text_value != last_saved_text:
                        save_text(shared_text_value, shared_text_file)
                        last_saved_text = shared_text_value
                        st.experimental_rerun()

        update_thread = threading.Thread(target=update_shared_text)
        update_thread.daemon = True
        update_thread.start()

        if st.button("Update"):
            with file_lock(shared_text_file):
                save_text(shared_text_value, shared_text_file)
                last_saved_text = shared_text_value
                st.success("Shared text updated.")
            shared_text_value = get_shared_text()

    # Start the local HTTP server
    for port_attempt in range(PORT, PORT + MAX_PORT_ATTEMPTS * 2):
        try:
            with socketserver.TCPServer(("", port_attempt), http.server.SimpleHTTPRequestHandler) as httpd:
                httpd.allow_reuse_address = True
                st.write(f"Serving at port {port_attempt}")
                httpd.serve_forever()
                break
        except OSError as e:
            if e.errno == 98:  # Address already in use
                if port_attempt == PORT + MAX_PORT_ATTEMPTS - 1:
                    port_attempt = PORT
                    continue
                continue
            else:
                raise e

if __name__ == "__main__":
    main()
