import replicate
import streamlit as st
from PIL import Image
import io
import base64
import re
import time
from hydralit import HydraApp, HydraHeadApp
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

animal_emojis = {
    "dog": "🐕",
    "bird": "🐦",
    "cat": "🐈",
    "elephant": "🐘",
    "fish": "🐟",
    "fox": "🦊",
    "horse": "🐎",
    "lion": "🦁",
    "monkey": "🐒",
    "mouse": "🐁",
    "owl": "🦉",
    "panda": "🐼",
    "rabbit": "🐇",
    "snake": "🐍",
    "tiger": "🐅",
    "unicorn": "🦄",
    "dragon": "🐉",
    "swan": "🦢",
    # Add more as needed
}


def process_analysis_text(text):
    pattern = re.compile(r"(\w+): (\d+)%")
    matches = pattern.findall(text)
    extracted_results = [(match[0], int(match[1])) for match in matches]
    return extracted_results


def upload_image():
    uploaded_file = st.file_uploader("Upload Your Cloud Photo", type=["jpg", "jpeg", "png"])
    if uploaded_file is not None:
        image = Image.open(uploaded_file)
        st.image(image, caption="Uploaded Cloud Photo", width=200)
    return uploaded_file


def local_image_to_data_url(file_obj):
    img_byte_arr = io.BytesIO(file_obj.read())
    encoded_string = base64.b64encode(img_byte_arr.getvalue()).decode("utf-8")
    mime_type = Image.open(img_byte_arr).format.lower()
    return f"data:image/{mime_type};base64,{encoded_string}"


def submit_analysis(uploaded_image):
    try:
        image_url = local_image_to_data_url(uploaded_image)
        input_data = {
            "image": image_url,
            "prompt": "What are the top 5 animals this cloud looks like, with confidence scores (in the form of percentage)?",
        }
        output = replicate.run(
            "yorickvp/llava-13b:b5f6212d032508382d61ff00469ddda3e32fd8a0e75dc39d8a4191bb742157fb",
            input=input_data,
        )
        st.write("Result: ", output)
        analysis_text = output.get("text", "")
        extracted_results = process_analysis_text(analysis_text)
        if not extracted_results:
            extracted_results = [("Unknown", 0)] * 5
        st.session_state["extracted_results"] = extracted_results
        st.session_state["analysis_complete"] = True
        st.experimental_rerun()
    except Exception as e:
        st.error(f"An error occurred: {e}")
        st.write("Unable to generate the riddle. Please check your Replicate credentials.")
        

class CloudRiddleApp(HydraHeadApp):
    def run(self):
        # Load custom CSS for mobile navbar positioning
        with open("style.css") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

        if "page" not in st.session_state:
            st.session_state["page"] = "Landing Page"
            st.toast("A new cloud is available ☁️")
            time.sleep(4)

        if st.session_state["page"] == "Landing Page":
            if st.button("👀 Check my new cloud ☁️"):
                st.session_state["page"] = "Image Upload"
                st.experimental_rerun()

        elif st.session_state["page"] == "Image Upload":
            uploaded_image = upload_image()
            if uploaded_image is not None:
                if st.button("Confirm and Reveal the Riddle"):
                    st.session_state["uploaded_image"] = uploaded_image
                    st.session_state["page"] = "Riddle Reveal"
                    st.experimental_rerun()

        elif st.session_state["page"] == "Riddle Reveal":
            if "uploaded_image" not in st.session_state or st.session_state["uploaded_image"] is None:
                st.warning("Please upload an image first on the 'Image Upload' page.")
                st.session_state["page"] = "Image Upload"
                st.experimental_rerun()
            else:
                uploaded_image = st.session_state["uploaded_image"]
                st.image(uploaded_image, caption="Uploaded Cloud Photo", width=200)

                if "user_response" not in st.session_state:
                    st.session_state["user_response"] = ""
                st.session_state["user_response"] = st.text_input(
                    "What objects do you think the cloud looks like?",
                    value=st.session_state["user_response"]
                )
                if st.button("Submit and Reveal the Riddle"):
                    submit_analysis(uploaded_image)

                if "analysis_complete" in st.session_state and st.session_state["analysis_complete"]:
                    extracted_results = st.session_state["extracted_results"]
                    st.subheader("Top 5 Similarities:")
                    for index, (item, similarity) in enumerate(extracted_results, start=1):
                        emoji = animal_emojis.get(item.lower(), "")
                        st.write(f"{index}. {emoji} {item}: {similarity}%")

                    if st.button("Check Next Cloud ☁️"):
                        st.session_state["page"] = "Image Upload"
                        st.session_state.pop("uploaded_image", None)
                        st.session_state.pop("extracted_results", None)
                        st.session_state.pop("user_response", None)
                        st.session_state.pop("analysis_complete", None)
                        st.experimental_rerun()


class TimeLapseApp(HydraHeadApp):
    def run(self):
        # Load custom CSS for mobile navbar positioning
        with open("style.css") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

        st.title("Time-Lapse Page")
        st.write("This page will be implemented in the future.")


if __name__ == "__main__":
    app = HydraApp(
        title="Cloud Riddle and Time-Lapse",
        favicon="🌤️",
        use_navbar=True,
        navbar_sticky=False,
    )

    app.add_app("Cloud Riddle", icon="☁️", app=CloudRiddleApp())
    app.add_app("Time-Lapse", icon="⏳", app=TimeLapseApp())

    app.run()
