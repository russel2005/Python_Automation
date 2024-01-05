import configparser


def read_config():
    config = configparser.ConfigParser()
    config_path ='common/config.ini'

    if config.read(config_path):
        print(f"Config file {config_path} successfully read.")
        return config
    else:
        print(f"Error reading config file: {config_path}")
        return None
