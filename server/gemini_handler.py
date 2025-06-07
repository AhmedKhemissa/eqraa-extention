import google.generativeai as genai
import os
import re
from dotenv import load_dotenv

load_dotenv()

# Arabic word detection regex - allows spaces
ARABIC_REGEX = re.compile(r'^[\u0600-\u06FF\s]+$')

# Remove normalize_arabic_word() function

def is_valid_arabic_word(word):
    """Checks if the input is a valid Arabic word or phrase using Gemini."""
    prompt = f"""
    هل "{word}" كلمة أو عبارة عربية صحيحة وذات معنى؟
    أجب بـ "نعم" أو "لا" فقط.
    """

    try:
        genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
        model = genai.GenerativeModel("gemini-2.0-flash")
        response = model.generate_content(prompt)
        answer = response.text.strip().lower()
        # Check if the answer contains "نعم" (yes)
        return "نعم" in answer or "yes" in answer
    except Exception as e:
        print(f"Validation error: {e}")
        # If there's an error, assume it might be valid and let processing continue
        return True

def get_gemini_completion(word):
    """Queries Gemini for structured word analysis."""
    prompt = f"""
    أعطني تحليلًا دقيقًا ومنسقًا للكلمة "{word}" بصيغة واضحة، حيث كل معلومة تكون في سطر مستقل وفقًا للتنسيق التالي:

    كلمة: {word}
    مستوى CEFR: (A1, A2, B1, B2, C1, C2 فقط)
    المجال: (حدد مجالًا واحدًا فقط مثل: قانون، طب، هندسة...)
    نوع الكلمة: (اسم، فعل، صفة، حال...)
    الجذر: (اكتب الجذر فقط، بدون شرح)
    التعريف: (جملة واحدة فقط تشرح المعنى بوضوح)
    المرادفات: (قائمة مفصولة بفواصل)
    الأضداد: (قائمة مفصولة بفواصل، أو اكتب "غير متوفر" إذا لم يكن هناك)
    مثال استخدام: (جملة قصيرة توضح استخدام الكلمة)
    السياق: (وضح كيف تُستخدم الكلمة في الحياة اليومية... )

    **مهم**: لا تضف أي شرح زائد خارج هذا التنسيق.
    """

    try:
        genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
        model = genai.GenerativeModel("gemini-2.0-flash")
        response = model.generate_content(prompt)
        return response.text.strip() if response.text else "غير متوفر"
    except Exception as e:
        print(f"Gemini completion error: {e}")
        return "غير متوفر"

def parse_response(text, original_word):
    """Parse the Gemini response into a structured dictionary."""
    result = {
        "Word": original_word,
        "CEFR Level": "غير متوفر",
        "Field": "غير متوفر",
        "Part of Speech": "غير متوفر",
        "Lemma": "غير متوفر",
        "Definition": "غير متوفر",
        "Synonyms": "غير متوفر",
        "Antonyms": "غير متوفر",
        "Phrase Example": "غير متوفر",
        "Context": "غير متوفر"
    }
    
    # Field mapping from Arabic to dictionary keys
    field_map = {
        "كلمة": "Word",
        "مستوى CEFR": "CEFR Level",
        "المجال": "Field",
        "نوع الكلمة": "Part of Speech",
        "الجذر": "Lemma",
        "التعريف": "Definition",
        "المرادفات": "Synonyms",
        "الأضداد": "Antonyms",
        "مثال استخدام": "Phrase Example",
        "السياق": "Context"
    }
    
    # Parse the text line by line
    for line in text.split('\n'):
        line = line.strip()
        if not line:
            continue
            
        # Extract field and value
        parts = line.split(':', 1)
        if len(parts) < 2:
            continue
            
        field, value = parts[0].strip(), parts[1].strip()
        
        # Map field to dictionary key
        if field in field_map:
            result[field_map[field]] = value
    
    return result

def analyze_word(word):
    """Main function to analyze an Arabic word."""
    # First check if input is valid Arabic
    if not ARABIC_REGEX.match(word):
        return {
            "error": True,
            "message": "⚠️ يُسمح فقط بالنصوص العربية. حاول مرة أخرى!"
        }
    
    # Check if it's a valid Arabic word
    if not is_valid_arabic_word(word):
        return {
            "error": True,
            "message": """
            ⚠️ خطأ: الكلمة المدخلة ليست كلمة عربية صحيحة أو ذات معنى.
            الرجاء إدخال كلمة أو عبارة عربية صحيحة.
            """
        }
    
    # Use word directly without normalization
    cleaned_word = word.strip()
    
    # Get the word analysis from Gemini
    gemini_response = get_gemini_completion(cleaned_word)
    
    # Parse the response
    word_data = parse_response(gemini_response, cleaned_word)
    
    # Return formatted result
    return {
        "error": False,
        "data": word_data,
        "formatted_output": f"""
        === نتيجة التحليل ===
        كلمة: {word_data.get('Word', 'غير متوفر')}
        مستوى CEFR: {word_data.get('CEFR Level', 'غير متوفر')}
        المجال: {word_data.get('Field', 'غير متوفر')}
        نوع الكلمة: {word_data.get('Part of Speech', 'غير متوفر')}
        الجذر: {word_data.get('Lemma', 'غير متوفر')}
        التعريف: {word_data.get('Definition', 'غير متوفر')}
        المرادفات: {word_data.get('Synonyms', 'غير متوفر')}
        الأضداد: {word_data.get('Antonyms', 'غير متوفر')}
        مثال استخدام: {word_data.get('Phrase Example', 'غير متوفر')}
        السياق: {word_data.get('Context', 'غير متوفر')}
        =====================
        """
    }

# For testing
if __name__ == "__main__":
    test_word = input("🔹 أدخل الكلمة: ").strip()
    result = analyze_word(test_word)
    if result.get("error"):
        print(result["message"])
    else:
        print(result["formatted_output"])