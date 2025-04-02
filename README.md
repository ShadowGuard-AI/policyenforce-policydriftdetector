# policyenforce-PolicyDriftDetector
A command-line tool that compares the current system configuration against a defined security policy (expressed in YAML or JSON) and reports deviations (drift). Uses libraries like `PyYAML` or `json` for parsing policies and `psutil` for system information. Can optionally create alerts if deviations are found. - Focused on Enforces security policies defined in YAML or JSON format. Validates configuration files, API responses, or other data against defined security constraints. Provides feedback on policy violations and can be integrated into CI/CD pipelines to prevent non-compliant deployments. Focuses on automated validation of security requirements.

## Install
`git clone https://github.com/ShadowStrikeHQ/policyenforce-policydriftdetector`

## Usage
`./policyenforce-policydriftdetector [params]`

## Parameters
- `-h`: Show help message and exit
- `--alert`: Create an alert if deviations are found.
- `--log_level`: Set the logging level.

## License
Copyright (c) ShadowStrikeHQ
