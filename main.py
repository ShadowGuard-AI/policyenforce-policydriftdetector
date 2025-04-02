import argparse
import json
import logging
import sys
import yaml
from jsonschema import validate, ValidationError, SchemaError

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def setup_argparse():
    """
    Sets up the argument parser for the command-line interface.
    Returns:
        argparse.ArgumentParser: The configured argument parser.
    """
    parser = argparse.ArgumentParser(description='Detects policy drift by comparing system configuration against a defined security policy.')

    parser.add_argument('policy_file', help='Path to the security policy file (YAML or JSON).')
    parser.add_argument('data_file', help='Path to the data file (YAML or JSON) containing the current system configuration.')
    parser.add_argument('--alert', action='store_true', help='Create an alert if deviations are found.')
    parser.add_argument('--log_level', default='INFO', choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'], help='Set the logging level.')

    return parser


def load_data(file_path):
    """
    Loads data from a YAML or JSON file.
    Args:
        file_path (str): The path to the file.
    Returns:
        dict: The loaded data as a dictionary.  Returns None if file is not valid.
    Raises:
        FileNotFoundError: If the specified file does not exist.
        ValueError: If the file format is invalid.
    """
    try:
        with open(file_path, 'r') as file:
            if file_path.endswith('.yaml') or file_path.endswith('.yml'):
                data = yaml.safe_load(file)
            elif file_path.endswith('.json'):
                data = json.load(file)
            else:
                raise ValueError("Unsupported file format.  Must be YAML or JSON.")
        return data
    except FileNotFoundError:
        logging.error(f"File not found: {file_path}")
        raise
    except (yaml.YAMLError, json.JSONDecodeError) as e:
        logging.error(f"Error parsing file: {file_path} - {e}")
        raise ValueError(f"Invalid YAML or JSON format in {file_path}")
    except Exception as e:
        logging.error(f"An unexpected error occurred: {e}")
        raise
    
def validate_data(data, schema):
    """
    Validates data against a JSON schema.
    Args:
        data (dict): The data to validate.
        schema (dict): The JSON schema.
    Returns:
        bool: True if the data is valid, False otherwise.
    """
    try:
        validate(instance=data, schema=schema)
        return True
    except ValidationError as e:
        logging.error(f"Validation Error: {e}")
        return False
    except SchemaError as e:
        logging.error(f"Schema Error: {e}")
        return False
    except Exception as e:
        logging.error(f"An unexpected error occurred during validation: {e}")
        return False

def main():
    """
    Main function to execute the policy drift detection.
    """
    parser = setup_argparse()
    args = parser.parse_args()

    # Set logging level
    logging.getLogger().setLevel(args.log_level.upper())

    try:
        # Load policy and data
        policy_data = load_data(args.policy_file)
        system_data = load_data(args.data_file)

        # Validate
        if not policy_data:
            logging.error("Policy data could not be loaded.")
            sys.exit(1)
        if not system_data:
            logging.error("System data could not be loaded.")
            sys.exit(1)

        is_valid = validate_data(system_data, policy_data)

        if is_valid:
            logging.info("System configuration is compliant with the security policy.")
        else:
            logging.warning("Policy drift detected!")
            if args.alert:
                logging.warning("Creating alert...") # Placeholder for alert creation logic

    except FileNotFoundError as e:
        logging.error(f"File not found: {e.filename}")
        sys.exit(1)
    except ValueError as e:
        logging.error(e)
        sys.exit(1)
    except Exception as e:
        logging.error(f"An unexpected error occurred: {e}")
        sys.exit(1)


if __name__ == "__main__":
    # Example Usage (This part is omitted to meet the specified output requirements)
    main()