import streamlit as st
from PIL import Image
import os
import json
from dotenv import load_dotenv
import google.generativeai as genai

# Set page configuration
st.set_page_config(page_title="Health Management: Nutrition Calculator & Diet Planner")

# Load API Key
load_dotenv()
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# File to store user data
USER_DATA_FILE = "users.json"

# Initialize session state for login and registration
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'page' not in st.session_state:
    st.session_state.page = "login"
if 'registration_message' not in st.session_state:
    st.session_state.registration_message = ""
if 'password_reset_message' not in st.session_state:
    st.session_state.password_reset_message = ""

# Load user data from file
def load_user_data():
    if os.path.exists(USER_DATA_FILE):
        with open(USER_DATA_FILE, 'r') as file:
            return json.load(file)
    return {}

# Save user data to file
def save_user_data(users):
    with open(USER_DATA_FILE, 'w') as file:
        json.dump(users, file, indent=4)

# Initialize users in session state from file
if 'users' not in st.session_state:
    st.session_state.users = load_user_data()

# Function to load Google Gemini model and get response for diet planning
def get_response_diet(prompt, input):
    try:
        model = genai.GenerativeModel('gemini-1.5-pro')  
        response = model.generate_content([prompt, input])
        return response.text
    except Exception as e:
        return f"Error: {str(e)}"

# Function to load Google Gemini model and get response for nutrition analysis
def get_response_nutrition(image, prompt):
    try:
        model = genai.GenerativeModel('gemini-1.5-pro')  
        response = model.generate_content([image[0], prompt])
        return response.text
    except Exception as e:
        return f"Error: {str(e)}"

# Preprocess image data
def prep_image(uploaded_file):
    if uploaded_file is not None:
        bytes_data = uploaded_file.getvalue()
        image_parts = [
            {
                "mime_type": uploaded_file.type,
                "data": bytes_data
            }
        ]
        return image_parts
    else:
        raise FileNotFoundError("No file is uploaded!")

# Function to render the header
def render_header():
    st.markdown("""
        <style>
        .header-box {
            background-color: black;
            color: white;
            padding: 10px;
            text-align: center;
            font-size: 24px;
            width: 100%;
            position: fixed;
            top: 0;
            left: 0;
            right: 0;
            z-index: 1000;
        }
        </style>
        <div class="header-box">Nutrigen</div>
    """, unsafe_allow_html=True)

# Function to show the registration page
def show_registration_page():
    render_header()
    st.title("Register")
    new_username = st.text_input("New Username")
    new_password = st.text_input("New Password", type="password")
    confirm_password = st.text_input("Confirm Password", type="password")
    
    if st.button("Register"):
        if new_username and new_password and confirm_password:
            if new_username in st.session_state.users:
                st.error("Username already exists")
            elif new_password != confirm_password:
                st.error("Passwords do not match")
            else:
                st.session_state.users[new_username] = new_password
                save_user_data(st.session_state.users)
                st.session_state.registration_message = "User registered successfully!"
                st.session_state.page = "login"
        else:
            st.error("Please enter a valid username and password")

    if st.session_state.registration_message:
        st.success(st.session_state.registration_message)
        st.session_state.registration_message = ""

    # Navigation to login page
    st.markdown("##")
    st.button("Back to Login", on_click=lambda: st.session_state.update({"page": "login"}))

# Function to show the password reset page
def show_password_reset_page():
    render_header()
    st.title("Reset Password")
    username = st.text_input("Username")
    new_password = st.text_input("New Password", type="password")
    confirm_password = st.text_input("Confirm Password", type="password")
    
    if st.button("Reset Password"):
        if username in st.session_state.users:
            if new_password == confirm_password:
                st.session_state.users[username] = new_password
                save_user_data(st.session_state.users)
                st.session_state.password_reset_message = "Password changed successfully!"
                st.session_state.page = "login"
            else:
                st.error("Passwords do not match")
        else:
            st.error("Username does not exist")

    if st.session_state.password_reset_message:
        st.success(st.session_state.password_reset_message)
        st.session_state.password_reset_message = ""

    # Navigation to login page
    st.markdown("##")
    st.button("Back to Login", on_click=lambda: st.session_state.update({"page": "login"}))

# Function to show the login page
def show_login_page():
    render_header()
    st.title("Login")
    col1, col2 = st.columns([2, 1])  # Create columns for layout
    
    with col1:
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        if st.button("Login"):
            if username in st.session_state.users and st.session_state.users[username] == password:
                st.session_state.logged_in = True
                st.session_state.page = "main"
            else:
                st.error("Incorrect username or password")

    with col2:
        st.write("")  # Add some space
        st.button("Forgot Password", on_click=lambda: st.session_state.update({"page": "reset_password"}))
        st.button("New User? Register", on_click=lambda: st.session_state.update({"page": "register"}))

# Function to show the main app page
def show_main_page():
    render_header()
    
    # Logout button at the top right
    st.sidebar.button("Logout", on_click=lambda: st.session_state.update({"logged_in": False, "page": "login"}))
    
    st.image('logo.jpg', width=70)
    st.header("Health: Nutrition Calculator & Diet Planner")

    section_choice1 = st.radio("Choose Section:", ("Nutrition Calculator", "Diet Planner"))

    # If choice is nutrition calculator
    if section_choice1 == "Nutrition Calculator":
        upload_file = st.file_uploader("Choose an image...", type=["jpg", "jpeg", "png"])
        if upload_file is not None:
            image = Image.open(upload_file)
            st.image(image, caption="Uploaded Image", use_column_width=True)

        # Prompt Template
        input_prompt_nutrition = """
        You are an expert Nutritionist. As a skilled nutritionist, you're required to analyze the food items
        in the image and determine the total nutrition value. 
        Additionally, you need to furnish a breakdown of each food item along with its respective content.

        Food item, Serving size, Total Cal., Protein (g), Fat,
        Carb (g), Fiber (g), Vit B-12, Vit B-6,
        Iron, Zinc, Manganese.

        Use a table to show the above information.
        """
        
        if st.button("Calculate Nutrition value!"):
            image_data = prep_image(upload_file)
            response = get_response_nutrition(image_data, input_prompt_nutrition)
            st.subheader("Nutrition AI:")
            st.write(response)

    # If choice is diet planner
    if section_choice1 == "Diet Planner":
        # Prompt Template
        input_prompt_diet = """
        You are an expert Nutritionist. 
        If the input contains a list of items like fruits or vegetables, you have to provide a diet plan and suggest
        breakfast, lunch, and dinner based on the given items.
        If the input contains numbers, you need to suggest a diet plan for breakfast, lunch, and dinner within
        the given number of calories for the whole day.

        Return the response using markdown.
        """
        
        age_category = st.selectbox("Select your age group:", ["Child", "Teenager", "Adult", "Senior"])
        diseases = st.multiselect("Do you have any of the following diseases? (Select all that apply):",
                                  ["Diabetes", "Hypertension", "Heart Disease", "Asthma", "High Cholesterol", "None"])
        
        input_diet = st.text_area("Input the list of items that you have at home to get a diet plan! OR \
                                  Input how many calories you want to intake per day:")
        
        if st.button("Plan my Diet!"):
            prompt = f"""
            You are an expert Nutritionist. Considering the age group '{age_category}' and the following diseases: {', '.join(diseases)}, 
            prepare a diet plan based on the given input.

            Input:
            {input_diet}
            """
            response = get_response_diet(prompt, input_diet)
            st.subheader("Diet Planner AI:")
            st.write(response)

# Main function to control page flow
def main():
    if st.session_state.page == "login":
        show_login_page()
    elif st.session_state.page == "register":
        show_registration_page()
    elif st.session_state.page == "reset_password":
        show_password_reset_page()
    elif st.session_state.page == "main" and st.session_state.logged_in:
        show_main_page()

if __name__ == "__main__":
    main()
