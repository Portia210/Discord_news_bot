import pandas as pd
from datetime import datetime



def format_economic_calendar(df: pd.DataFrame) -> pd.DataFrame:
    def rename_columns(df):
        # Fix: Use inplace=True and return the modified DataFrame
        df.rename(columns={
            "time": "שעה",
            "volatility": "תנודתיות צפויה",
            "description": "תיאור",
            "actual": "בפועל",
            "forecast": "תחזית",
            "previous": "הקודם"
        }, inplace=True)
        return df


    # on volatility column, change the value to "חלשה" if it's "weak"
    def change_volatility(x):
        if "צפויה תנודתיות" in x:
            x = x.replace("צפויה תנודתיות", "").strip()
            return x
        return x


    # Fix: Use .loc[] to modify the original DataFrame
    # columns order - use .loc[] to avoid the warning
    df = df.loc[:, ["time", "volatility", "description", "previous", "forecast", "actual"]]

    # Fix: Use .loc[] to modify the volatility column in the original DataFrame
    df.loc[:, "volatility"] = df.loc[:, "volatility"].apply(change_volatility)
    
    # Fix: Call rename_columns and return the modified DataFrame
    df = rename_columns(df)
    return df


class CSVTextFormatter:
    def __init__(self):
        # Emoji mapping for common column names
        self.emoji_map = {
            'זמן': '🕐',
            'אירוע': '📋',
            'תנודתיות צפויה': '⚡',
            'תיאור': '📝',
            'תחזית': '🔮',
            'הקודם': '🔄',
            'בפועל': '✅',
            'תאריך': '📅',
            'שעה': '⏰',
        }
    
    def format_csv_to_markdown(self, df: pd.DataFrame) -> str:
        """
        Convert CSV to nicely formatted markdown text with emojis
        
        Args:
            df: DataFrame to format
        """
        try:
            # Generate formatted markdown
            formatted_text = self._format_markdown(df)

            return formatted_text
            
        except Exception as e:
            error_msg = f"❌ Error formatting CSV: {e}"
            print(error_msg)
            return error_msg
    
    def _get_emoji(self, column_name: str) -> str:
        """Get appropriate emoji for column name"""
        return self.emoji_map.get(column_name, '📋')
    
    def _format_markdown(self, df: pd.DataFrame) -> str:
        """Format as clean markdown with emojis and better readability"""
        text = ""
        
        # Process each row
        for idx, row in df.iterrows():
            # Add each column with emoji and clean formatting
            for col in df.columns:
                value = str(row[col]) if pd.notna(row[col]) else "N/A"
                # Clean up the value - remove extra quotes if present
                value = value.strip('"\'')
                
                # Get emoji for this column
                emoji = self._get_emoji(col)
                
                # Format with emoji and clean text (no bold)
                text += f"{emoji}   {col}: {value}  \n"
            
            # Add spacing between records
            text += "\n\n"
        
        return text


def economic_calendar_to_text(df: pd.DataFrame) -> str:
    formatter = CSVTextFormatter()
    formatted = format_economic_calendar(df)
    text = formatter.format_csv_to_markdown(formatted)
    return text
