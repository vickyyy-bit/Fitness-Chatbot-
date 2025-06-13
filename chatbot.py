import google.generativeai as genai

# Configure Google Gemini API (Replace with your actual API key)
API_KEY = "AIzaSyAfytA-77cX75oQg2TjOtldo5ZJx2K6Re0"  # Replace with your actual API key
genai.configure(api_key=API_KEY)

# Load the AI model (now using gemini-1.5-flash)
model = genai.GenerativeModel("models/gemini-1.5-flash")

# Function to get chatbot response
def get_chatbot_response(user_message):
    try:
        response = model.generate_content(user_message)
        return response.text
    except Exception as e:
        return f"Error: {str(e)}"
