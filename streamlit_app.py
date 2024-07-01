import streamlit as st
import socket
import os

def get_local_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(('10.255.255.255', 1))
        IP = s.getsockname()[0]
    except Exception:
        IP = '127.0.0.1'
    finally:
        s.close()
    return IP

def get_shared_text_file_path(local_ip):
    shared_text_file = os.path.join("/tmp", f"ssavblurb_{local_ip.replace('.', '_')}.txt")
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

    # Get the local IP address
    local_ip = get_local_ip()

    # Check if the user is on the same local network
    if local_ip.startswith("10.") or local_ip.startswith("192.168."):
        # Get the path to the shared text file
        try:
            shared_text_file = get_shared_text_file_path(local_ip)
            st.success(f"Shared text file created at: {shared_text_file}")
        except Exception as e:
            st.error("Error getting the shared text file path: " + str(e))
            if not os.access("/tmp", os.W_OK):
                st.warning("Please grant write permissions to the /tmp directory to use this app.")
            return

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
    else:
        st.warning("This app is only accessible to devices on the same local Wi-Fi network.")

if __name__ == "__main__":
    main()
