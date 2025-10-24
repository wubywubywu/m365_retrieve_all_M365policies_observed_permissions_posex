import requests
import csv
import time
from datetime import datetime
import sys

# Created by Rosie the TAM Assistant to fulfill customer request for all
# observed permissions/settings grouped by policy.
# 2025 AppOmni Inc.

# ====== EDIT THESE VALUES ======
# Your AppOmni tenant domain prefix (e.g., 'fanniemae' from fanniemae.appomni.com)
appomni_instance = 'fanniemae'
# Your active AppOmni session token. Must be FRESH!
# !!! ACTION REQUIRED: UPDATE THIS TOKEN WITH A FRESH ONE !!!
session_token = 'd9ngw9fhsfhzmudlllzgtgd2qrv279k7'
# The type of monitored service
ms_service = 'o365'
# The specific Monitored Service ID for your M365 instance
ms_id = '36779'
# ====== DO NOT EDIT BELOW THIS LINE ======

BASE_URL = f'https://{appomni_instance}.appomni.com'
HEADERS = {
    'Authorization': f'Session {session_token}',
    'Content-Type': 'application/json'
}


# --- Core Pagination Function ---
def fetch_paginated_data(url, limit=1000):
    """
    Fetches all data, handling pagination until the 'next' URL is null.
    Returns the list of all collected results.
    """
    all_data = []
    current_url = url
    page_count = 0

    # Check if URL already has query parameters (for initial call)
    delimiter = '&' if '?' in current_url else '?'

    # Initialize with limit and offset=0 if they aren't already present
    if 'limit=' not in current_url and 'offset=' not in current_url:
        current_url = f"{current_url}{delimiter}limit={limit}&offset=0"

    while current_url:
        page_count += 1

        # Add rate limit pause before fetch
        if page_count > 1:
            time.sleep(1)

            # We keep this print to show progress
        print(f"  Fetching page {page_count} from: {current_url}")
        sys.stdout.flush()

        try:
            response = requests.get(current_url, headers=HEADERS)
            if response.status_code != 200:
                print(f"  ERROR: API call failed. Status code: {response.status_code}")
                print(f"  DEBUG: Response Text (Check for 401/403): {response.text}")
                sys.stdout.flush()
                return None

            data = response.json()

            # Extract results and next page URL
            results = data.get('results', [])
            all_data.extend(results)
            current_url = data.get('next')

            # If 'next' is not a full URL but a path, correct it to be a full URL
            if current_url and not current_url.startswith('http'):
                current_url = BASE_URL + current_url

        except Exception as e:
            print(f"  ERROR: An exception occurred during fetch: {e}")
            return None

    return all_data


# --- Step 1: Fetch all High-Level Policies ---
def get_all_policies():
    """Fetches the list of all high-level policies (ID, Category, Name) using the robust pagination function."""
    policy_list_base_url = f"{BASE_URL}/api/v1/{ms_service}/svcexp/{ms_id}/policy/"
    print("STEP 1: Starting fetch for high-level policy list...")

    policies = fetch_paginated_data(policy_list_base_url)

    if policies is None:
        print("ERROR: Could not retrieve any high-level policies.")
        return []

    print(f"  Successfully fetched {len(policies)} high-level policies.")
    return policies


# --- Step 2 & 3: Fetch Details, Flatten, and Group ---
def fetch_and_process_policy_settings(policies):
    """
    Iterates through policies, fetches all associated settings, and prepares
    the final list for CSV export, grouping the data.
    """
    final_settings_list = []

    print("\nSTEP 2: Starting fetch for granular policy settings (Observed Permissions)...")

    # --- FIX START: Filtering and Dynamic Keying (No change needed here, as the keys are correct) ---
    policies_to_process = []

    # Inspect all items and filter only for items that look like actual policies
    for idx, p in enumerate(policies):
        # We look for a unique identifier and a category name to ensure it's a policy object
        policy_id = p.get('id') or p.get('policy_id')
        policy_category = p.get('policy_category')

        if policy_id and policy_category:
            policies_to_process.append(p)

    if not policies_to_process:
        print("NOTICE: Filtered list is empty. No individual policies to fetch details for.")
        print(
            "CRITICAL DEBUG: The high-level API response did not contain the necessary 'id'/'policy_id' keys to link to the detailed API.")
        return []

    print(f"DEBUG: Filtered down to {len(policies_to_process)} actual policies for detailed fetch.")
    sys.stdout.flush()
    # --- FIX END ---

    for i, policy in enumerate(policies_to_process):
        # Get the keys needed for the API call and CSV
        policy_id = policy.get('id') or policy.get('policy_id')
        policy_category = policy.get('policy_category')
        policy_name = policy.get('name', 'UNKNOWN_NAME')

        print(f"Processing Policy {i + 1}/{len(policies_to_process)}: {policy_name} ({policy_id})")
        sys.stdout.flush()

        # The working path is /policy/policy_settings/ and requires both category and ID.
        base_query = f"/api/v1/{ms_service}/svcexp/{ms_id}/policy/policy_settings/?ordering=-criticality,setting&policy_category={policy_category}&policy_id={policy_id}"
        full_url = BASE_URL + base_query

        # Fetch all pages of settings for this single policy
        settings = fetch_paginated_data(full_url)

        if settings is None:
            # Error details already printed inside fetch_paginated_data
            print(f"  WARNING: Skipping {policy_name} due to fetch error.")
            continue

        if not settings:
            print(f"  NOTICE: Skipping {policy_name}. Zero settings retrieved.")
            continue

        print(f"  Retrieved {len(settings)} individual settings. Starting flatten.")
        sys.stdout.flush()

        # Flatten and group the results for the CSV
        for setting in settings:
            final_settings_list.append({
                # Grouping Keys (Mapping to API keys for consistency)
                'policy_category_api_name': policy_category,
                'policy_category_label': policy.get('policy_category_label', 'N/A'),
                'policy_name': policy_name,
                'policy_id': policy_id,
                'api_name': setting.get('api_name', 'N/A'),  # Keep API name for reference

                # Granular Setting Details
                'setting_name': setting.get('setting', 'N/A'),
                'current_value': setting.get('current_value', 'N/A'),
                'criticality': setting.get('criticality', 'N/A'),
                'criticality_score': setting.get('criticality_score', 0),
                'service_category': setting.get('service_category', 'N/A'),
                'setting_category_label': setting.get('category_label', 'N/A'),
            })

    return final_settings_list


def save_to_csv(data, filename):
    """Saves a list of dictionaries to a CSV file using customer-friendly headers."""
    if not data:
        print("\nNo detailed settings data was generated, so no file will be saved.")
        return

    # Define a map from the internal data keys to the final, customer-facing column names
    column_mapping = {
        'policy_category_label': 'Policy Type',
        'policy_name': 'Name',
        'policy_id': 'Policy ID',
        'setting_name': 'Setting',
        'current_value': 'Value',
        'criticality': 'Criticality',
        'setting_category_label': 'Category',

        # Include technical columns at the end for reference (not visible in the screenshot, but useful)
        'api_name': 'API Name',
        'policy_category_api_name': 'Policy Category (API)',
        'criticality_score': 'Criticality Score',
        'service_category': 'Service Category',
    }

    # The actual keys in the data dictionary
    data_keys = list(column_mapping.keys())

    # The friendly headers for the CSV file
    csv_headers = list(column_mapping.values())

    with open(filename, 'w', newline='', encoding='utf-8') as output_file:
        # Use fieldnames from the internal data keys, but specify the header row separately
        dict_writer = csv.DictWriter(output_file, fieldnames=data_keys)

        # Write the customer-friendly headers
        dict_writer.writerow(dict(zip(data_keys, csv_headers)))

        # Write the data rows
        dict_writer.writerows(data)

    print(f"\nSUCCESS: Successfully saved {len(data)} detailed setting rows to {filename}")
    print("The output is grouped by policy and contains all observed settings as requested.")


# Rest of the original __main__ block
if __name__ == "__main__":

    # 1. Get the list of policies (Policy ID and Category are mandatory for the next step)
    policies_list = get_all_policies()

    if policies_list:
        # 2. Fetch all granular settings and combine them
        detailed_settings_data = fetch_and_process_policy_settings(policies_list)

        # 3. Save the final grouped data to a CSV
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_filename = f"{appomni_instance}_M365_Policy_Settings_Full_Report_{timestamp}.csv"
        save_to_csv(detailed_settings_data, output_filename)