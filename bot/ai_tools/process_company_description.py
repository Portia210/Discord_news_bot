from ai_tools.chat_gpt import AIInterpreter


def get_hebrew_description(symbol: str, raw_description: str):
    ai_interpreter = AIInterpreter()
    prompt = f"""
    You are a financial analyst and journalist.
    You will be given a description of a company.
    You need to expand what the summary describes. 
    Go in depth what exactly the company do according to the last information that you have (not just in general), what exactly is it do, who are other compatitor that it has and what is the main product or service it provides.
    *respond in hebrew*
    *respond with no intro, headers or subheaders*
    *use real new line to break the text into paragraphs*
    """ + f"\nsybmol name {symbol}" + f"\nraw description: {raw_description}"

    response = ai_interpreter.get_interpretation(prompt)
    return response
