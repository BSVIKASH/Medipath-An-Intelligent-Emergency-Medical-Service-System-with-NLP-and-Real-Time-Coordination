from flask import Flask, request, render_template, jsonify, send_from_directory
from openai import OpenAI
import os

app = Flask(__name__)

# Initialize the OpenAI client
client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key="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",  # Replace with your actual API key
)

# Main route to render the index page
@app.route("/")
def index():
    return render_template("index.html")  # Serve the main page

# Chatbot interface route
@app.route("/chatbot.html")
def chatbot():
    return render_template("chatbot.html")  # Serve the chatbot page

# Live location page route
@app.route("/live_location.html")
def live_location():
    return render_template("live_location.html")  # Serve the live location page (if you have one)

# Route to handle user input and generate responses
@app.route("/get_response", methods=["POST"])
def get_response():
    # Get user input from the form
    user_input = request.form["user_input"]
    
    # Prepare the prompt for the Deepseek model
    prompt = f"The user has the following medical issue: {user_input}. Provide 10 concise and clear first aid points for this issue in a numbered list format. Use simple language and ensure the information is specific to India. For example, use '108' for ambulance and '100' for police. Highlight important words in **bold**."
    
    try:
        # Call the Deepseek API
        completion = client.chat.completions.create(
            extra_headers={
                "HTTP-Referer": "http://localhost:5000",  # Replace with your site URL
                "X-Title": "Medical First Aid Chatbot",  # Replace with your site name
            },
            model="deepseek/deepseek-r1-distill-llama-8b",
            messages=[
                {"role": "user", "content": prompt}
            ]
        )
        
        # Extract the response from the API
        response = completion.choices[0].message.content
        
        # Format the response to ensure it's concise and user-friendly
        formatted_response = format_response(response)
        
        # Return the response as JSON
        return jsonify({"response": formatted_response})
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"response": "I'm sorry, there was an error processing your request. Please try again."})

# Function to format the response
def format_response(response):
    # Split the response into lines and remove unnecessary details
    lines = response.split("\n")
    formatted_lines = []
    for line in lines:
        if line.strip() and not line.strip().startswith(("Note:", "Disclaimer:", "Warning:")):
            # Replace markdown bold syntax with HTML bold tags
            line = line.replace("**", "<strong>").replace("**", "</strong>")
            formatted_lines.append(line.strip())
    return "<br>".join(formatted_lines)

# Run the Flask app
if __name__ == "__main__":
    app.run(debug=True)