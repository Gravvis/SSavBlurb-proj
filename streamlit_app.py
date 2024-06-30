import streamlit as st
import os
import socket
import time
from datetime import datetime, timedelta
import json
import http.server
import socketserver
import shutil

PORT = 8000
MAX_FILE_SIZE = 50 * 1024 * 1024  # 50 MB
FILE_EXPIRATION_DAYS = 3

class CustomHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/text':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            text = load_text()
            self.wfile.write(json.dumps({'text': text}).encode())
        elif self.path.startswith('/files/'):
            file_path = os.path.join(os.getcwd(), 'uploads', self.path.split('/files/')[1])
            if os.path.isfile(file_path):
                self.send_response(200)
                self.send_header('Content-type', 'application/octet-stream')
                self.end_headers()
                with open(file_path, 'rb') as f:
                    self.wfile.write(f.read())
            else:
                self.send_response(404)
                self.end_headers()
        else:
            return super().do_GET()

    def do_POST(self):
        if self.path == '/save':
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data)
            save_text(data['text'])
            self.send_response(200)
            self.end_headers()
        elif self.path == '/upload':
            content_length = int(self.headers['Content-Length'])
            if content_length > MAX_FILE_SIZE:
                self.send_response(413)
                self.end_headers()
                return
            post_data = self.rfile.read(content_length)
            file_name = self.headers['X-Filename']
            file_path = os.path.join(os.getcwd(), 'uploads', file_name)
            with open(file_path, 'wb') as f:
                f.write(post_data)
            self.send_response(200)
            self.end_headers()
        else:
            return super().do_POST()

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

def get_uploaded_files():
    uploads_dir = os.path.join(os.getcwd(), 'uploads')
    if os.path.exists(uploads_dir):
        return [f for f in os.listdir(uploads_dir)]
    return []

def cleanup_expired_files():
    uploads_dir = os.path.join(os.getcwd(), 'uploads')
    if os.path.exists(uploads_dir):
        for filename in os.listdir(uploads_dir):
            file_path = os.path.join(uploads_dir, filename)
            file_age = time.time() - os.path.getmtime(file_path)
            if file_age > FILE_EXPIRATION_DAYS * 24 * 60 * 60:
                os.remove(file_path)

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
    st.write("A simple tool to share text and files across devices on the same Wi-Fi network.")

    with st.container():
        text = st.text_area("Enter your text here...", height=400, key="text_input")

    if st.button("Save Text"):
        save_text(text)
        st.success("Text saved successfully!")

    host_name = socket.gethostname()
    host_ip = socket.gethostbyname(host_name)
    st.write(f"Your device's IP address: {host_ip}")

    with st.container():
        st.markdown("## Shared Text")
        shared_text = st.text_area("", height=400, key="shared_text", disabled=False)
        if shared_text != load_text():
            shared_text = load_text()
            st.session_state["shared_text"] = shared_text

    if st.button("Update Shared Text"):
        save_text(shared_text)
        st.success("Shared text updated successfully!")

    with st.container():
        st.markdown("## Shared Files")
        uploaded_files = get_uploaded_files()
        if uploaded_files:
            col1, col2 = st.columns(2)
            for file_name in uploaded_files:
                with col1:
                    if st.button(f"Download {file_name}", key=file_name):
                        file_path = os.path.join(os.getcwd(), 'uploads', file_name)
                        st.download_button(
                            label=f"Download {file_name}",
                            data=open(file_path, 'rb'),
                            file_name=file_name,
                            mime='application/octet-stream',
                        )
                col2.write(file_name)
        else:
            st.write("No files have been uploaded yet.")

        with st.form("file_upload_form"):
            uploaded_file = st.file_input("Upload a file (max 50 MB)", type=None, accept_multiple_files=False)
            submit = st.form_submit_button("Upload")

        if submit and uploaded_file is not None:
            file_path = os.path.join(os.getcwd(), 'uploads', uploaded_file.name)
            with open(file_path, 'wb') as f:
                f.write(uploaded_file.getbuffer())
            st.success(f"File '{uploaded_file.name}' uploaded successfully!")

    # Start the local HTTP server
    with socketserver.TCPServer(("", PORT), CustomHTTPRequestHandler) as httpd:
        cleanup_expired_files()
        st.write(f"Serving at port {PORT}")
        httpd.serve_forever()

if __name__ == "__main__":
    main()
