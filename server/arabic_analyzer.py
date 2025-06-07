from gemini_handler import analyze_word

def fetch_word_data(word):
    # Get analysis from Gemini
    analysis = analyze_word(word)
    
    if not analysis:
        return {"error": "Analysis failed"}
    
    return analysis