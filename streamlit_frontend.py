import streamlit as st
import time
import requests
from PIL import Image
# Predefined lists for model and style names
img = Image.open('logo.png')
st.set_page_config(
    page_icon=img,
    layout="wide",
    initial_sidebar_state="expanded",
    page_title="STORYBOARD",
)

hide_streamlit_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            </style>
            """
st.markdown(hide_streamlit_style, unsafe_allow_html=True) 

st.markdown(
    r"""
    <style>
    .stDeployButton {
            visibility: hidden;
        }
    </style>
    """, unsafe_allow_html=True
)


if 'images_data' not in st.session_state:
    st.session_state.images_data = []

current_page_url = st.query_params()
access_key = current_page_url["access_key"][0]
# st.write(current_page_url["access_key"])


app_id = current_page_url["app_id"][0]
# st.write(current_page_url["app_id"])

# print(access_key[0])
# print(app_id[0])
token = f'Bearer {access_key}'

def refresh_product(taskId):
    url = f'https://marketplace-api-user.staging.devsaitech.com/api/v1/user/products/{app_id}/refresh/{taskId}'
    headers = {
        'Content-Type': 'application/json',
        'Authorization': token    
    }
    
    start_time = time.time()
    with st.spinner("Generating Storyboard"):
        while True:
            response = requests.get(url, headers=headers)
            data = response.json()
            # st.write(data)
            if data['data']['status'] != 'Pending':
                print("Success:", data)
                return data
                break
            
            elif time.time() - start_time > 120:  # Check if 50 seconds have passed
                print("Timeout reached without success.")
                return []
                break
            
            else:
                print("Request not yet successful. Retrying...")
                time.sleep(2)  # Wait for 2 seconds before retrying


models = ['Unstable', 'RealVision', 'SDXL']
styles = ['(No style)', 'Japanese Anime', 'Digital/Oil Painting', "Pixar/Disney Character", "Photographic", "Comic book", "Line art", "Black and White Film Noir", "Isometric Rooms"]

# Sidebar inputs
general_prompt = st.sidebar.text_area('General Prompt')
negative_prompt = st.sidebar.text_area('Negative Prompt')
style_name = st.sidebar.selectbox('Style Name', styles)

# Long text box for multiple prompts
prompt_text = st.sidebar.text_area('Enter Prompts (each on a new line)', value="Driving in car\nEating breakfast")

# Splitting the input text by newlines to build the prompt array
prompt_array = prompt_text.split('\n') if prompt_text else []
height = st.sidebar.number_input('Height', min_value=768)
width = st.sidebar.number_input('Width', min_value=768)
id_length = st.sidebar.number_input('ID Length', min_value=1)
model_name = st.sidebar.selectbox('Model Name', models)
guidance_scale = st.sidebar.slider('Guidance Scale', min_value=1, max_value=10, value=7)
seed = st.sidebar.slider('Seed', min_value=1, max_value=10000000)
num_steps = st.sidebar.number_input('Number of Steps', min_value=20, max_value=40)
# st.write(st.session_state.images_data)

def display_images():
    for index, image_url in enumerate(st.session_state.images_data):
        st.image(image_url, use_column_width=True)

# API call
if st.sidebar.button('Generate'):

    payload = {
    "method": "create_storyboard",
    "payload": {
        "height": height,
        "width": width,
        "model_name": model_name,
        "guidance_scale": guidance_scale,
        "seed": seed,
        "num_steps": num_steps,
        "general_prompt": general_prompt,
        "negative_prompt": negative_prompt,
        "prompt_array": prompt_array,
        "style_name": style_name,
        "id_length": id_length
        }
    }

    headers = {
        'Content-Type': 'application/json',
        'Authorization': token    
    }


    response = requests.post(f'https://marketplace-api-user.staging.devsaitech.com/api/v1/user/products/{app_id}/use', json=payload, headers=headers)

    # Check if the request was successful
    if response.status_code == 201:
        parsed_response_dict = response.json()
        # st.write(parsed_response_dict)
        taskId = parsed_response_dict.get('data', {}).get('taskId', "not found")
        # st.write(taskId)
        data = refresh_product(taskId)
        if not data["data"]["result"]["data"]:
            st.write("Could not generate images, please try again.")
        else:
            images_data = data["data"]["result"]["data"]
            # Update the session state with new images
            st.session_state.images_data = images_data
        
    else:
        st.write(response.json())
        st.error(f"Failed to generate image. Status code: {response.status_code}")

# Call display_images() outside the conditional to ensure images are shown on every run
display_images()
