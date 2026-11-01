import argparse
import json
import logging
import sys
import yaml

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def setup_argparse():
    """
    Sets up the argument parser for the command-line interface.
    Returns:
        argparse.ArgumentParser: The configured argument parser.
    """
    parser = argparse.ArgumentParser(description='Detects policy drift by comparing the values in a data file against the expected settings in a policy file. Both files are named by the operator; no system information is read directly.')

    parser.add_argument('policy_file', help='Path to the policy file (YAML or JSON) holding a mapping of setting names to expected values.')
    parser.add_argument('data_file', help='Path to the data file (YAML or JSON) holding a mapping of setting names to current values.')
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
            # The parser is chosen by filename suffix alone, case included. A YAML file named with an uppercase suffix, or a YAML document saved as .json, is handed to the wrong parser and reported as invalid content rather than as a naming mismatch.
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
    
def compare_settings(policy_data, system_data):
    """
    Compares current values against the expected settings in the policy.
    Args:
        policy_data (dict): Mapping of setting names to expected values.
        system_data (dict): Mapping of setting names to current values.
    Returns:
        list: One drift line per key whose current value differs from the
        expected value, is missing from the data, or is present in the
        data but not listed in the policy.
    """
    drift = []
    for key in sorted(policy_data):
        if key not in system_data:
            drift.append(f"{key}: missing from the data file (expected {policy_data[key]!r})")
        # Values compare with plain Python equality across two different parsers. YAML turns yes into True and JSON has no yes, while True and 1 compare equal here, so a policy written as yes and a data file carrying 1 pass as identical. Type drift between the two files is mostly invisible to me.
        elif system_data[key] != policy_data[key]:
            drift.append(f"{key}: current value {system_data[key]!r} differs from expected {policy_data[key]!r}")
    # Extra keys are appended after the whole policy pass instead of being merged into one sorted list, so the drift output is two alphabetical runs back to back. A reader looking for one alphabetical report will miss an extra key that sorts before every policy key.
    for key in sorted(system_data):
        if key not in policy_data:
            drift.append(f"{key}: present in the data file but not listed in the policy")
    return drift

def main():
    """
    Main function to execute the policy drift detection.
    """
    parser = setup_argparse()
    args = parser.parse_args()

    # Set logging level
    logging.getLogger().setLevel(args.log_level.upper())

    try:
        # Load policy and data. A policy file that cannot be parsed, or
        # that does not hold a non-empty mapping of expected settings,
        # is a problem with the policy file itself, never drift.
        try:
            policy_data = load_data(args.policy_file)
        except ValueError as e:
            logging.error(f"Policy file is invalid: {args.policy_file} - {e}")
            sys.exit(1)
        if not isinstance(policy_data, dict) or not policy_data:
            logging.error(f"Policy file is invalid: {args.policy_file} must hold a mapping of setting names to expected values.")
            sys.exit(1)

        system_data = load_data(args.data_file)
        # An empty mapping passes this test, where the policy side above rejects an empty mapping outright. That asymmetry is the honest one: an empty data file means every setting is missing, which is drift, while an empty policy would make any data file look compliant.
        if not isinstance(system_data, dict):
            logging.error(f"Data file is invalid: {args.data_file} must hold a mapping of setting names to current values.")
            sys.exit(1)

        # If either file uses keys of mixed types, which YAML happily produces, the sorted() calls inside compare_settings raise TypeError and the run ends in the generic handler below as an unexpected error, not as a complaint about the key shapes.
        drift = compare_settings(policy_data, system_data)

        if not drift:
            logging.info("System configuration is compliant with the security policy.")
        else:
            logging.warning("Policy drift detected!")
            for line in drift:
                logging.warning(f"Drift: {line}")
            sys.exit(1)

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