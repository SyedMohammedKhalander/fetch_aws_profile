# AWS Profile Details Fetcher

This script fetches AWS profile details for a specified user and their CloudTrail events within the last 7 days. It categorizes events into created components and component accesses.

## Overview

This script interacts with the AWS Identity and Access Management (IAM) service and the AWS CloudTrail service to gather information about a specific user. It retrieves data about their profile, created components, and components they accessed. The script then stores this information in a JSON file.

## Installation

1. Clone the repository:

    ```
    git clone https://github.com/your-username/aws-profile-details-fetcher.git
    ```

2. Navigate to the project directory:

    ```
    cd aws-profile-details-fetcher
    ```

3. Create and activate a virtual environment:

    ```
    python3 -m venv venv
    source venv/bin/activate
    ```

4. Install the required dependencies:

    ```
    pip install -r requirements.txt
    ```

## Usage

1. Run the script:

    ```
    python main.py
    ```

2. The script will prompt you to provide your AWS credentials. This information is used to access the AWS services.

3. After successful authentication, the script will fetch and store profile details along with CloudTrail events in a JSON file named `user_data.json`.

4. You can find the stored user data in the `user_data.json` file.

## How It Works

- The script uses the `boto3` library to interact with AWS services.
- It starts by authenticating your AWS credentials.
- It retrieves the user's profile information, including create date, ARN, username, access key, and last login.
- The script then fetches CloudTrail events that match the specified criteria (last 7 days).
- Events are categorized into two groups: "created components" and "component accesses."
- Event data is cleaned and formatted for better presentation.
- Finally, the script stores all the gathered information in a structured JSON format in the `user_data.json` file.

## Disclaimer

This script is provided as-is and should be used responsibly. Make sure you have the necessary permissions before running the script. It's your responsibility to ensure proper AWS access and compliance with any applicable AWS policies.
