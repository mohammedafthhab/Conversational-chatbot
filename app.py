from flask import Flask, render_template, request, jsonify, session
import random
import spacy
import sqlite3
import nltk
import requests
from bs4 import BeautifulSoup
from nltk.sentiment.vader import SentimentIntensityAnalyzer
from fuzzywuzzy import fuzz
import re
import os

app = Flask(__name__)
app.secret_key = os.urandom(24)  # For session management

# Setup - load these only once at startup
nltk.download('vader_lexicon', quiet=True)
try:
    nlp = spacy.load("en_core_web_sm")
except:
    # If spaCy model isn't installed, download it
    import subprocess
    subprocess.call(['python', '-m', 'spacy', 'download', 'en_core_web_sm'])
    nlp = spacy.load("en_core_web_sm")
    
vader_analyzer = SentimentIntensityAnalyzer()

# Initialize DB
def init_db():
    conn = sqlite3.connect('new_chat_history.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS conversation (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_input TEXT,
            bot_response TEXT,
            user_name TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

def save_to_db(user_input, bot_response, user_name):
    conn = sqlite3.connect('new_chat_history.db')
    cursor = conn.cursor()
    cursor.execute("INSERT INTO conversation (user_input, bot_response, user_name) VALUES (?, ?, ?)", 
                  (user_input, bot_response, user_name))
    conn.commit()
    conn.close()

def get_chat_history(limit=10):
    conn = sqlite3.connect('new_chat_history.db')
    cursor = conn.cursor()
    cursor.execute("SELECT user_input, bot_response FROM conversation ORDER BY id DESC LIMIT ?", (limit,))
    rows = cursor.fetchall()
    history = []
    for row in rows:
        history.append({"user": row[0], "bot": row[1]})
    conn.close()
    history.reverse()  # Show in chronological order
    return history

def get_filtered_history(keyword):
    conn = sqlite3.connect('new_chat_history.db')
    cursor = conn.cursor()
    cursor.execute("SELECT user_input, bot_response FROM conversation WHERE user_input LIKE ? OR bot_response LIKE ? ORDER BY id", 
                  ('%' + keyword + '%', '%' + keyword + '%'))
    rows = cursor.fetchall()
    history = []
    for row in rows:
        history.append({"user": row[0], "bot": row[1]})
    conn.close()
    return history

# Expand abbreviations
def preprocess_input(user_input):
    abbreviation_dict = {
        "u": "you", "iam": "i am", "im": "i am", "pls": "please", "btw": "by the way",
        "idk": "i don't know", "thx": "thanks"
    }
    words = user_input.lower().split()
    expanded_words = [abbreviation_dict.get(word, word) for word in words]
    expanded_input = " ".join(expanded_words).strip()
    return expanded_input

# Fuzzy intent matcher
def match_intent(user_input, patterns, threshold=75):
    for pattern in patterns:
        if fuzz.partial_ratio(user_input.lower(), pattern.lower()) >= threshold:
            return True
    return False

# Sentiment
def analyze_sentiment_vader(text):
    scores = vader_analyzer.polarity_scores(text)
    compound = scores['compound']
    if compound >= 0.3:
        return "positive"
    elif compound <= -0.3:
        return "negative"
    else:
        return "neutral"

def generate_emotion_response(user_input):
    sentiment = analyze_sentiment_vader(user_input)
    if sentiment == "positive":
        return "I'm glad you're feeling good! 😊"
    elif sentiment == "negative":
        return "I'm here for you. Let me know if you want to talk. ❤️"
    else:
        return "Got it. What's on your mind?"

# Name extraction
def extract_name(user_input):
    doc = nlp(user_input)
    for ent in doc.ents:
        if ent.label_ == "PERSON":
            return ent.text.strip()

    phrases = ["call me", "this is", "you are speaking to", "i am", "my name is", "you can call me", "i'm"]
    for phrase in phrases:
        if phrase in user_input.lower():
            parts = user_input.lower().split(phrase)
            if len(parts) > 1:
                possible_name = parts[1].strip().split()[0].capitalize()
                return possible_name
    return None

# Web scraping
def scrape_url(url):
    try:
        response = requests.get(url, timeout=5)
        soup = BeautifulSoup(response.text, 'html.parser')

        title = soup.title.string if soup.title else "No title found"
        content = ""
        for paragraph in soup.find_all(['p', 'h1', 'h2', 'h3', 'article']):
            content += paragraph.get_text() + "\n"

        image_urls = []
        for img_tag in soup.find_all('img', src=True):
            img_url = img_tag['src']
            if img_url.startswith('http'):
                image_urls.append(img_url)
            else:
                img_url_full = requests.compat.urljoin(url, img_url)
                image_urls.append(img_url_full)

        response_content = f"Page Title: {title}\n\nMain Content:\n{content[:800]}...\n\nImages:\n"
        response_content += "\n".join(image_urls[:3]) if image_urls else "No images found."
        return response_content
    except Exception as e:
        return f"Sorry, I couldn't retrieve the page. Error: {str(e)}"

# Main response handler
def generate_response(user_input, user_name=None):
    processed_input = preprocess_input(user_input)
    
    # Command to filter chat history
    if processed_input.startswith("show history with"):
        keyword = processed_input.replace("show history with", "").strip()
        history = get_filtered_history(keyword)
        if history:
            return f"Found {len(history)} messages with '{keyword}'", True, {"filtered_history": history}
        else:
            return f"No conversations found with '{keyword}'.", False, {}
            
    # Command to show chat history
    if processed_input == "show history":
        history = get_chat_history()
        return "Here's your recent chat history.", True, {"history": history}

    # Check for URL
    if re.match(r'http[s]?://', processed_input):
        return scrape_url(processed_input), False, {}

    # Emotion handling
    if match_intent(processed_input, ["feeling", "happy", "sad", "angry", "depressed", "good", "bad"]):
        return generate_emotion_response(processed_input), False, {}

    # Greeting
    if match_intent(processed_input, ["hi", "hello", "hey", "good morning", "good evening"]):
        return f"Hello, {user_name if user_name else 'there'}!", False, {}

    # How are you
    if match_intent(processed_input, ["how are you", "how r u", "how are u doing"]):
        return random.choice([
            "I'm doing great! Thanks for asking 😊",
            "All good here. How about you?",
            "I'm functioning perfectly, like a good little bot!"
        ]), False, {}

    # Jokes
    if match_intent(processed_input, ["tell me a joke", "make me laugh", "say a joke", "joke"]):
        jokes = [
            "Why did the computer go to therapy? Because it had too many bytes of emotional baggage!",
            "Parallel lines have so much in common… it's a shame they'll never meet.",
            "I would tell you a UDP joke, but you might not get it.",
            "Why did the scarecrow win an award? Because he was outstanding in his field!"
        ]
        return random.choice(jokes), False, {}

    # Name inquiry
    if match_intent(processed_input, ["what is my name", "who am i", "tell me my name"]):
        return f"Your name is {user_name}." if user_name else "I don't know your name yet. Please tell me.", False, {}

    # Name extraction
    name = extract_name(processed_input)
    if name:
        return f"Nice to meet you, {name}! 😊", True, {"new_name": name}

    # Default response
    return "Interesting! Tell me more.", False, {}

# Flask routes
@app.route('/')
def index():
    init_db()  # Make sure DB is initialized
    return render_template('index.html')

@app.route('/chat', methods=['POST'])
def chat():
    user_input = request.json.get('message', '')
    
    # Get user name from session if available
    user_name = session.get('user_name', None)
    
    # Generate response
    response, special_action, extra_data = generate_response(user_input, user_name)
    
    # Handle name extraction
    if special_action and 'new_name' in extra_data:
        session['user_name'] = extra_data['new_name']
        user_name = extra_data['new_name']
    
    # Save to database
    save_to_db(user_input, response, user_name)
    
    # Prepare response
    result = {
        'response': response,
        'user_name': user_name
    }
    
    # Add any extra data
    if special_action:
        for key, value in extra_data.items():
            result[key] = value
    
    return jsonify(result)

@app.route('/history')
def history():
    limit = request.args.get('limit', 10, type=int)
    history = get_chat_history(limit)
    return jsonify(history)

if __name__ == '__main__':
    init_db()
    app.run(debug=True)