import csv
import os
from datetime import datetime
import pandas as pd

def get_timestamp():
    """
    Get the current timestamp as a string.
    """
    return datetime.now().strftime("%m-%d-%Y")

def read_devices_name(csv_path='input/devices.csv'):
    device_names = []
    try:
        with open(csv_path, newline='') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                device_names.append(row['device_name'])
    except Exception as e:
        print(f"Error reading device names from CSV: {e}")
    return device_names


def update_device_status_problem(device_status_dict, device_problem_dict, csv_folder='input', csv_prefix='device_status_update'):
    """
    Write device status information to a CSV file.

    Parameters:
        - device_status_dict (dict): Dictionary containing device_name and status.
        - device_problem_dict (dict): Dictionary containing device_name and problem_status.
        - csv_folder (str): Folder where the CSV file will be stored. Default is 'input'.
        - csv_prefix (str): Prefix for the CSV file name. Default is 'device_status_update'.
    """
    csv_filename = os.path.join(csv_folder, f"{csv_prefix}{get_timestamp()}.csv")
    
    try:
        # Combine device_status_dict and device_problem_dict into a single dictionary
        combined_dict = {
            'device_name': list(device_status_dict.keys()),
            'status': list(device_status_dict.values()),
            'problem': [device_problem_dict.get(device_name, '') for device_name in device_status_dict.keys()]
        }

        # Convert the combined dictionary to a pandas DataFrame
        df = pd.DataFrame(combined_dict)

        # Write the DataFrame to a CSV file
        df.to_csv(csv_filename, index=False)
    except Exception as e:
        print(f"Error updating device status in CSV: {e}")

def update_device_status(device_status_dict, csv_folder='input', csv_prefix='device_status_update'):
    """
    Write device status information to a CSV file.

    Parameters:
        - device_status_dict (dict): Dictionary containing device_name and status.
        - filename (str): Name of the CSV file. Default is 'device_status.csv'.
    """

    csv_filename = os.path.join(csv_folder, f"{csv_prefix}{get_timestamp()}.csv")
    try:
        # Convert the dictionary to a pandas DataFrame
        df = pd.DataFrame(list(device_status_dict.items()), columns=['device_name', 'status', 'problem'])

        # Write the DataFrame to a CSV file
        df.to_csv(csv_filename, index=False)
    except Exception as e:
        print(f"Error updating device status in CSV: {e}")



def update_devie_group(device_name_to_group ,csv_folder='input',csv_file='devices_status_12-04-2023_10_09.csv'):
    try:
        # Create a unique CSV file for each run
        csv_filename = os.path.join(csv_folder, csv_file)

        df = pd.read_csv(csv_filename)
        # Update the 'same_group' column based on the device_name mapping
        df['groupid'] = df['device_name'].map(device_name_to_group)
        # Save the updated DataFrame back to the CSV file
        df.to_csv(csv_filename, index=False)

    except Exception as e:
        print(f"Error updating device group in CSV: {e}")

# def update_device_status(csv_path, device_name, new_status):
#     try:
#         updated_rows = []
#         with open(csv_path, 'r') as csvfile:
#             reader = csv.DictReader(csvfile)
#             for row in reader:
#                 if row['device_name'] == device_name:
#                     row['status'] = new_status
#                 updated_rows.append(row)

#         with open(csv_path, 'w', newline='') as csvfile:
#             fieldnames = ['device_name', 'status']
#             writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
#             writer.writeheader()
#             writer.writerows(updated_rows)

#     except Exception as e:
#         print(f"Error updating CSV file: {e}")
