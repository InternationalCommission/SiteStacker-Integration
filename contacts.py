import requests
from datetime import datetime
from requests_oauthlib import OAuth2Session
from oauthlib.oauth2 import BackendApplicationClient
from config import SS_API_KEY, SS_API_SECRET, CC_CLIENT_ID, CC_CLIENT_SECRET, CC_ACCESS_TOKEN_URL, CC_AUTHORIZATION_URL, CC_SCOPES


# Helper function to generate SiteStacker API signature
def generate_signature(api_secret, method, content_type, date):
    string_to_sign = f"{method}\n{content_type}\n{date}"
    signature = hashlib.sha256(string_to_sign.encode('utf-8'), api_secret.encode('utf-8')).hexdigest()
    return signature


# Helper function to fetch contacts from SiteStacker
def fetch_ss_contacts():
    date = datetime.utcnow().strftime('%a, %d %b %Y %H:%M:%S GMT')
    signature = generate_signature(SS_API_SECRET, 'GET', '', date)
    headers = {
        'Authorization': f'HMAC {SS_API_KEY}:{signature}',
        'SS-Date': date
    }
    response = requests.get('https://ic-world.wmtekdev.com/api/persons', headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(f"Failed to fetch SiteStacker contacts: {response.text}")


# Helper function to fetch contacts from Constant Contact
def fetch_cc_contacts(access_token):
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Accept': 'application/json'
    }
    response = requests.get('https://api.cc.email/v3/contacts', headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(f"Failed to fetch Constant Contact contacts: {response.text}")


# Helper function to update contacts in SiteStacker
def update_ss_contact(contact_id, data):
    date = datetime.utcnow().strftime('%a, %d %b %Y %H:%M:%S GMT')
    signature = generate_signature(SS_API_SECRET, 'PUT', 'application/json', date)
    headers = {
        'Authorization': f'HMAC {SS_API_KEY}:{signature}',
        'SS-Date': date,
        'Content-Type': 'application/json'
    }
    response = requests.put(f'https://ic-world.wmtekdev.com/api/persons/{contact_id}', headers=headers, json=data)
    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(f"Failed to update SiteStacker contact: {response.text}")


# Helper function to update contacts in Constant Contact
def update_cc_contact(contact_id, data, access_token):
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json'
    }
    response = requests.patch(f'https://api.cc.email/v3/contacts/{contact_id}', headers=headers, json=data)
    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(f"Failed to update Constant Contact contact: {response.text}")
