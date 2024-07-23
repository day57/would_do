import configparser
 
 
def read_config():
    # Create a ConfigParser object
    config = configparser.ConfigParser()
 
    # Read the configuration file
    config.read('config.ini')
 
    # Access values from the configuration file
    debug_mode = config.getboolean('General', 'debug')
    log_level = config.get('General', 'log_level')
    db_name = config.get('Database', 'db_name')
    db_host = config.get('Database', 'db_host')
    db_port = config.get('Database', 'db_port')
 
    # Return a dictionary with the retrieved values
    config_values = {
        'debug_mode': debug_mode,
        'log_level': log_level,
        'db_name': db_name,
        'db_host': db_host,
        'db_port': db_port
    }
 
    return config_values
 
 
if __name__ == "__main__":
    # Call the function to read the configuration file
    config_data = read_config()
 
    # Print the retrieved values
    print("Debug Mode:", config_data['debug_mode'])
    print("Log Level:", config_data['log_level'])
    print("Database Name:", config_data['db_name'])
    print("Database Host:", config_data['db_host'])
    print("Database Port:", config_data['db_port'])