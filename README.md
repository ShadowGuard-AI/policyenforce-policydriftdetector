# policyenforce-PolicyDriftDetector
A command-line tool that compares the values in a data file against the expected settings in a defined security policy (both expressed in YAML or JSON) and reports deviations (drift). The policy file is a plain mapping of setting names to expected values; it is not a JSON Schema, and plain setting values are compared directly. Both input files are named by the operator; the tool reads no system information itself and uses no psutil. Each setting whose current value differs, each policy setting missing from the data file, and each data setting not listed in the policy is reported as drift. - Focused on Enforces security policies defined in YAML or JSON format. Provides feedback on policy violations. In a CI/CD pipeline the exit code is the gate: the run exits 1 when drift is detected and 0 when the data matches the policy, so a pipeline step using this tool fails on drift. No alert is sent anywhere; the earlier --alert flag was removed because there is no alert destination.

## Install
`git clone https://github.com/ShadowGuard-AI/policyenforce-policydriftdetector`

## Usage
`python3 main.py policy_file data_file [--log_level LEVEL]`

Example: `python3 main.py policy.json current.json`

A policy file that cannot be parsed, or that does not hold a mapping of expected settings, ends the run with exit code 1 and a message naming the policy file as the problem; that is never reported as drift. An empty object data file ({}) is a valid data file holding no settings: every policy setting is reported missing, which is drift, and the run exits 1.

## Parameters
- `policy_file`: Path to the policy file (YAML or JSON) holding expected settings. Required positional argument.
- `data_file`: Path to the data file (YAML or JSON) holding current values. Required positional argument.
- `-h`: Show help message and exit
- `--log_level`: Set the logging level. Default: INFO. Choices: DEBUG, INFO, WARNING, ERROR, CRITICAL.

## License
MIT License. See LICENSE.
