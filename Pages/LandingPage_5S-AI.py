# Flask Backend with Embedded HTML and CSS

# This application creates a simple webpage for 5S-AI.com.
# 5S is a way to keep workplaces clean and organized, like tidying up your desk or room!
# This program uses Flask to handle the webpage, combining Python (backend) with HTML and CSS (frontend).

from flask import Flask, render_template_string

# Set up the Flask application
app = Flask(__name__)

# Define the main page of the website
@app.route("/")
def landing_page():
    # Features to show on the webpage
    features = [
        {"title": "AI-Powered Scoring", "description": "Eliminate bias with intelligent evaluations"},
        {"title": "Real-time Efficiency", "description": "75% faster assessment completion"},
        {"title": "Advanced Analytics", "description": "Track improvements with precision"},
        {"title": "Visual Intelligence", "description": "Smart workplace documentation"},
    ]

    # Steps to guide the user through the process
    steps = [
        {"step": "01", "title": "Capture", "description": "Upload or take photos of your workspace"},
        {"step": "02", "title": "Analyze", "description": "AI evaluates 5S compliance"},
        {"step": "03", "title": "Improve", "description": "Get actionable insights and recommendations"},
    ]

    # HTML code for the webpage, including inline CSS for styling
    landing_page_html = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>5S-AI Landing Page</title>
    <style>
        /* Style for the body */
        body {
            font-family: Arial, sans-serif;
            line-height: 1.6;
            color: #333;
        }

        /* Style for the header */
        header {
            background: #f4f4f4;
            padding: 1em 0;
            text-align: center;
        }

        /* Containers for features and steps */
        .features-container, .steps-container {
            display: flex;
            gap: 1em;
            justify-content: center;
            padding: 2em;
        }
    </style>
</head>
<body>
    <header>
        <h1>5S-AI.COM</h1>
        <nav>
            <a href="#features">Features</a>
            <a href="#about">About</a>
            <a href="#contact">Contact</a>
            <a href="#login" class="login-button">Log In</a>
        </nav>
    </header>
    
    <main>
        <!-- Introduction section -->
        <section id="intro">
            <h2>Transform Your Workplace Assessment</h2>
            <p>Elevate your 5S evaluations with AI-powered insights. Achieve precision, efficiency, and continuous improvement.</p>
        </section>

        <!-- Features section -->
        <section id="features">
            <h2>Why Choose Our Platform</h2>
            <div class="features-container">
                {% for feature in features %}
                    <div class="feature-card">
                        <h3>{{ feature.title }}</h3>
                        <p>{{ feature.description }}</p>
                    </div>
                {% endfor %}
            </div>
        </section>

        <!-- Steps section -->
        <section id="how-it-works">
            <h2>How It Works</h2>
            <div class="steps-container">
                {% for step in steps %}
                    <div class="step">
                        <h3>{{ step.step }}: {{ step.title }}</h3>
                        <p>{{ step.description }}</p>
                    </div>
                {% endfor %}
            </div>
        </section>
    </main>

    <!-- Footer section -->
    <footer>
        <p>&copy; 2024 5S-AI.COM. All rights reserved.</p>
    </footer>
</body>
</html>
"""

    # Render the webpage with the features and steps passed as data
    return render_template_string(landing_page_html, features=features, steps=steps)

# Run the Flask app in debug mode for easy testing
if __name__ == "__main__":
    app.run(debug=True)
