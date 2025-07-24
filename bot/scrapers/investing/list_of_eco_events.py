import pandas as pd
import os
from IPython.display import display
from utils import write_json_file, read_json_file, measure_time
from ai_tools import AIInterpreter

def get_descriptions_list():
    list_of_files = os.listdir("data/investing_scraper")

    descriptions_dict = set()
    for file in list_of_files:
        df = pd.read_csv(f"data/investing_scraper/{file}")
        if "description" not in df.columns:
            continue
        # descirpiton series only if "volatility" is not "חופשי"
        wanted_volatility = ["צפויה תנודתיות גבוהה", "צפויה תנודתיות בינונית"]
        description_series = df[df["volatility"].isin(wanted_volatility)]["description"]
        # remove all data in () in description_series
        description_series = description_series.str.replace(r'\(.*?\)', '', regex=True).str.strip()
        descriptions_list = description_series.tolist()
        for description in descriptions_list:
            descriptions_dict.add(description)

    write_json_file("events_descriptions.json", list(descriptions_dict))

@measure_time
def get_descriptions_text():
    descriptions_dict = read_json_file("events_descriptions.json")
    chunk_size = 10
    ai_interpreter = AIInterpreter()
    count = 0
    for i in range(0, len(descriptions_dict), chunk_size):
        count += 1
        if count < 1:
            break
        prompt = """
        הסבר את המשמעות הכלכלית של כל אירוע מבין האירועים הבאים, שפה פשוטה, הסבר כיצד המשמעות של האירוע יכולה להשתנות בהתאם למצב הכלכלי בשוק. 

        החזר תשובה ב-JSON FORMAT בלבד, ללא טקסט נוסף. השתמש במבנה הבא:
        {
            "events": [
                {
                    "event_name": "שם האירוע",
                    "event_description": "הסבר מפורט על האירוע והשפעתו הכלכלית"
                }
            ]
        }

        חשוב: החזר JSON בלבד, ללא טקסט נוסף לפני או אחרי.
        """ + "\n" + "\n".join(descriptions_dict[i:i+chunk_size])
        response = ai_interpreter.get_json_response(prompt)
        write_json_file(f"json.json", response)

