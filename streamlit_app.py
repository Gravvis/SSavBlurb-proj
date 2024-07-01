import streamlit as st
import socket
import os

def get_local_hostname():
    try:
        return socket.gethostname()
    except Exception:
        return "localhost"

def get_shared_text_file_path(hostname):
    shared_text_file = os.path.join("/tmp", f"ssavblurb_{hostname.replace('.', '_')}.txt")
    return shared_text_file

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

    # Get the local hostname
    local_hostname = get_local_hostname()

    # Get the path to the shared text file
    shared_text_file = get_shared_text_file_path(local_hostname)

    # Load the shared text
    try:
        if os.path.exists(shared_text_file):
            with open(shared_text_file, "r") as f:
                shared_text = f.read()
        else:
            shared_text = ""
    except Exception as e:
        st.error("Error loading the shared text: " + str(e))
        return

    # Display the shared text in the text area
    text = st.text_area("Enter your text here", value=shared_text, height=200, key="shared_text")

    # Save the text to the shared file
    if st.button("Save"):
        try:
            with open(shared_text_file, "w") as f:
                f.write(text)
            st.success("Text saved!")
        except Exception as e:
            st.error("Error saving the text: " + str(e))
            if not os.access(shared_text_file, os.W_OK):
                st.warning("Please grant write permissions to the shared text file to save changes.")

    st.write(f"Access this app from any device on the same Wi-Fi network.")

if __name__ == "__main__":
    main()
