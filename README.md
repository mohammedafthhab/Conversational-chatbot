# AI Chat Assistant

A modern Flask-based chatbot with sentiment analysis, name recognition, and web scraping capabilities.

AI Chat Assistant Screenshot
![alt text](image.png)

## Features

- 🤖 Natural language processing with spaCy
- 😊 Sentiment analysis using NLTK's VADER
- 🔍 Name extraction and recognition
- 🌐 Web page scraping and content analysis
- 💾 Chat history storage with SQLite
- 📱 Responsive, modern Bootstrap interface

## Tech Stack

- **Backend**: Flask, Python 3.9+
- **NLP**: spaCy, NLTK
- **Frontend**: HTML5, CSS3, JavaScript, Bootstrap 5
- **Database**: SQLite
- **Additional Libraries**: BeautifulSoup4, FuzzyWuzzy

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/j22k/chatbot.git
   cd ai-chat-assistant
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   
   # On Windows
   venv\Scripts\activate
   
   # On macOS/Linux
   source venv/bin/activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Download required NLP models:
   ```bash
   python -m spacy download en_core_web_sm
   python -c "import nltk; nltk.download('vader_lexicon')"
   ```

## Usage

1. Start the Flask application:
   ```bash
   python app.py
   ```

2. Open your browser and navigate to:
   ```
   http://127.0.0.1:5000/
   ```

3. Start chatting with the AI assistant!

## Key Functionalities

- **Sentiment Analysis**: The bot can detect emotional tone in messages
- **Name Recognition**: Tell the bot your name, and it will remember you
- **Web Scraping**: Paste a URL, and the bot will summarize the content
- **Chat History**: View your conversation history at any time
- **Command System**: Try commands like "show history" or "tell me a joke"

## Development

### Project Structure

```
chatbot_app/
│
├── static/           # Static files
├── templates/        # HTML templates
│   └── index.html    # Main UI template
├── app.py            # Main Flask application
└── requirements.txt  # Dependencies
```

### Adding New Features

To add new bot capabilities:

1. Define a new pattern-matching function in `app.py`
2. Add your logic to the `generate_response()` function
3. Update the UI if needed in `templates/index.html`

## License

[MIT License](LICENSE)

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## Contact

Your Name - [junaidkaliyadan@gmail.com](mailto:junaidkaliyadan@gmail.com)

Project Link: [https://github.com/j22k/chatbot.git](https://github.com/j22k/chatbot.git)