# **M365 Policy Settings Exporter (m365\_full\_policy\_settings\_export.py)**

## **📄 Overview**

This Python script is designed to extract a complete, granular baseline of all observed security policies and their settings from a specified **Microsoft 365 (M365)** Monitored Service within the AppOmni Posture Explorer API.

This tool is essential for **security auditing, compliance reviews**, and creating a reference catalog of all active M365 configurations, providing significantly more detail than what is available in the high-level policy lists.

## **✨ Key Features**

* **Granular Data Extraction:** Fetches every single observed setting (e.g., Auto Forward Enabled, Require device PIN) associated with each policy.  
* **Structured Output:** Groups all settings by their parent Policy Type and Policy Name for easy review and filtering.  
* **Customer-Friendly Headers:** Uses column names that directly match the AppOmni Posture Explorer UI (e.g., "**Policy Type**," "**Setting**," "**Value**").  
* **Robust Pagination:** Automatically handles pagination for both the list of policies and the individual policy settings, ensuring all data is collected.

## **🛠️ Prerequisites**

1. **Python 3.x:** Installed on your system.  
2. **requests Library:** You will need to install the Python requests library.  
   `pip install requests`

3. **AppOmni API Access:**  
   * **Monitored Service Permissions:** The M365 monitored service in AppOmni **must** have all necessary permissions granted, especially those related to role management and configuration settings (e.g., RoleManagement.Read.All), or the script will fail with a 404 Not Found error.  
   * **AppOmni Session Token:** A valid, active **Session Token** from your AppOmni tenant. This token is required for authentication and typically expires after a short period.

## **🚀 Usage**

### **1\. Configure the Script**

Open m365\_full\_policy\_settings\_export.py and modify the values in the \====== EDIT THESE VALUES \====== section:

| Variable | Description | Example |
| :---- | :---- | :---- |
| `appomni\_instance` | Your AppOmni tenant prefix (e.g., the 'bdemo' part of bdemo.appomni.com). | 'bdemo' |
| `session\_token` | Your active AppOmni Session Token. | 'xxxxxxxxxxxxxxxxx' |
| `ms\_service` | The service type. For this script, it is always 'o365'. | 'o365' |
| `ms\_id` | The unique Monitored Service ID for your specific M365 instance (found in the AppOmni UI URL). | 'xxxxxxxxxxxxxxxxx' |

### **2\. Run the Script**

Execute the script from your terminal:

`python3 m365\_full\_policy\_settings\_export.py`

### **3\. Review the Output**

The script will generate a CSV file in the same directory with a timestamped name:

`\[appomni\_instance\]\_M365\_Policy\_Settings\_Full\_Report\_\[timestamp\].csv`

## **📊 Output Schema (CSV Columns)**

The output file contains all granular settings, logically grouped by their parent policy:

| Column Name | Source Field | Description |
| :---- | :---- | :---- |
| **Policy Type** | `policy\_category\_label` | The high-level category of the policy (e.g., M365 Exchange Remote Domain). |
| **Name** | `policy\_name` | The customer-defined name of the policy (e.g., \*.yale.edu). |
| **Policy ID** | `policy\_id` | The unique AppOmni identifier for the policy object. |
| **Setting** | `setting\_name` | The human-readable name of the specific configuration setting (e.g., Auto Forward Enabled). |
| **Value** | `current\_value` | The observed value of that setting in the M365 environment (e.g., False, TRUE, \<Missing\>). |
| **Criticality** | `criticality` | The AppOmni criticality level (e.g., high, medium, informational). |
| **Category** | `setting\_category\_label` | The security category the setting belongs to (e.g., Other Security Settings). |

**Technical/Debug Columns (Included at the end for reference):**

* API Name  
* Policy Category (API)  
* Criticality Score  
* Service Category
