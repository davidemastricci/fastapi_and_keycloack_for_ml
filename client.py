import requests
import json

def get_token():
    # Keycloak token endpoint URL
    token_url = 'http://localhost:8080/auth/realms/securemodel/protocol/openid-connect/token'

    # client ID and secret for your Keycloak client
    client_id = 'caller'
    client_secret = 'ExPkb1fwGrCUr9Fcod5KK61sq5XN9yWv'

    # Set the grant type to 'client_credentials' for service role (machine to machine communication)
    # This works if client authtication flow is "Service account roles"
    grant_type = 'client_credentials'

    # Make a POST request to the token endpoint with the appropriate parameters
    response = requests.post(token_url, data={
        'client_id': client_id,
        'client_secret': client_secret,
        'grant_type': grant_type
    })


    if response.status_code == 200:
        
        # Extract the access token from the response
        access_token = response.json()['access_token']
        return access_token
    else:
        print(f'Failed to obtain access token, error: {response.status_code}')
        return None

    

model_url = 'http://localhost:8000/predict'
headers = {'Content-type': 'application/json'}
text = "I have a problem with my iphone that needs to be resolved asap!!"
labels = ["urgent", "not urgent", "phone", "tablet", "computer"]

#TODO: call the protected_model with and without the access token

def authorized_request():
    # Make a POST request the prediction
    response = requests.post(model_url, headers=headers, data=json.dumps({
        'token': get_token(),
        'text': text,
        'labels': labels
    }))
    analyze_response(response)


def unauthorized_request():
    fake_token = 'blablabla'
    response = requests.post(model_url, headers=headers, data=json.dumps({
    'token': fake_token,
    'text': text,
    'labels': labels
    }))
    analyze_response(response)



def analyze_response(response):
    if response.status_code == 200:
    
        # Extract the access token from the response
        prediction = response.json()['prediction']
        print('Prediction', prediction)
    else:
        print(f'Failed to obtain prediction, error: {response.status_code}')
        print(response.json())

if __name__ == '__main__':
    print("Attempting unauthorized request")
    unauthorized_request()
    print("Attempting authorized request")
    authorized_request()