import re
from datetime import datetime


def extract_number_from_sitename(data):
    numeric_value = re.findall(r'\d+', data)
    return numeric_value


def epoch_to_datetime(epoch_time):
    try:
        # Convert epoch time to a datetime object
        dt_object = datetime.utcfromtimestamp(epoch_time)

        # Format the datetime object as a string
        formatted_date = dt_object.strftime('%Y-%m-%d %H:%M:%S UTC')

        return formatted_date
    except Exception as e:
        print(f"Error converting epoch time to human-readable date: {e}")
        return None
