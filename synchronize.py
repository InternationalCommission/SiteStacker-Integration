import json
import os
from constants import *
from config import CC_REDIRECT_URI
from ss_utils import *


# Helper function to map SiteStacker contact to Constant Contact contact
def ss_to_cc_contact(ss_contact):
    cc_contact = {
        'email_addresses': [
            {'email_address': ss_contact['email'], 'status': 'ACTIVE'}
        ],
        'first_name': ss_contact['first_name'],
        'last_name': ss_contact['last_name']
    }
    return cc_contact


# Helper function to map Constant Contact contact to SiteStacker contact
def cc_to_ss_contact(cc_contact):
    ss_contact = {
        'email': cc_contact['email_addresses'][0]['email_address'],
        'first_name': cc_contact['first_name'],
        'last_name': cc_contact['last_name']
    }
    return ss_contact


def synchronize():
    # Fetch SiteStacker contacts
    ss_contacts = fetch_ss_contacts()

    # Fetch Constant Contact access token using oAuth2 Device Flow
    client = BackendApplicationClient(client_id=CC_CLIENT_ID)
    oauth = OAuth2Session(client=client)
    authorization_url, state = oauth.authorization_url(CC_AUTHORIZATION_URL, scope=CC_SCOPES)
    print(f"Please visit the following URL to authorize the application: {authorization_url}")
    device_code = input("Enter the device code: ")
    token = oauth.fetch_token(CC_ACCESS_TOKEN_URL, authorization_response=f"{CC_REDIRECT_URI}?code={device_code}", client_secret=CC_CLIENT_SECRET)

    # Fetch Constant Contact contacts
    cc_contacts = fetch_cc_contacts(token['access_token'])

    # Sync SiteStacker contacts to Constant Contact
    for ss_contact in ss_contacts:
        # Check if contact already exists in Constant Contact
        cc_contact = next((c for c in cc_contacts if c['email_addresses'][0]['email_address'] == ss_contact['email']), None)
        if cc_contact:
            # Contact exists, update it in Constant Contact
            cc_data = ss_to_cc_contact(ss_contact)
            cc_contact_id = cc_contact['id']
            update_cc_contact(cc_contact_id, cc_data, token['access_token'])
        else:
            # Contact does not exist, create it in Constant Contact
            cc_data = ss_to_cc_contact(ss_contact)
            create_cc_contact(cc_data, token['access_token'])

    # Sync Constant Contact contacts to SiteStacker
    for cc_contact in cc_contacts:
        # Check if contact already exists in SiteStacker
        ss_contact = next((c for c in ss_contacts if c['email'] == cc_contact['email_addresses'][0]['email_address']), None)
        if not ss_contact:
            # Contact does not exist, create it in SiteStacker
            ss_data = cc_to_ss_contact(cc_contact)
            create_ss_contact(ss_data)
