
class Language():
    # Language configuration for the bot
    # Options: "en" (English only), "he" (Hebrew only), "bilingual" (both languages)
    BOT_LANGUAGE = "en"  # Change this to "he" for Hebrew or "bilingual" for both
    
    # You can also set this per user if needed
    USER_LANGUAGES = {
        # "user_id": "he",  # Example: specific user gets Hebrew
        # "another_user_id": "bilingual"  # Example: specific user gets both languages
    }