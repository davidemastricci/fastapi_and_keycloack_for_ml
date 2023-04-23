from fastapi import FastAPI, HTTPException, status
from transformers import pipeline
from keycloak import KeycloakOpenID
from pydantic import BaseModel

app = FastAPI()


#load the model, here I'm using HuggingFace model but it could be pkl file or whatever trained model you want.
# this model doeas text classification on arbitrary set of labels using zero-shot classification tecniques
model = pipeline(model="facebook/bart-large-mnli") 


class Input(BaseModel):
    token: str
    text: str
    labels: list

@app.post('/predict')
def predict(input: Input):
    prediction = {}
    token = input.token
    if secure(token):
        text = input.text
        labels = input.labels
        # Make prediction using the model
        prediction = model(text, labels)
    else:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="unauthorized token",
            headers={"WWW-Authenticate": "Basic"},
        )

    # Return the prediction as JSON
    return {'prediction': prediction, 'status_code': status.HTTP_200_OK}


# Configure client
keycloak_openid = KeycloakOpenID(server_url="http://localhost:8080/auth/",
                                 client_id="protected_modelt",
                                 realm_name="securemodel",
                                 client_secret_key="8K9nx7rM8rMgf7WUpCur9ZyXxdLuN7S0")

def secure(token):
    KEYCLOAK_PUBLIC_KEY = "-----BEGIN PUBLIC KEY-----\n" + keycloak_openid.public_key() + "\n-----END PUBLIC KEY-----"
    options = {"verify_signature": True, "verify_aud": False, "verify_exp": False}
    try:
        keycloak_openid.decode_token(token, key=KEYCLOAK_PUBLIC_KEY, options=options)
    except Exception:
        print("unauthorized token")
        return False
    else:
        print("authorized token")
        return True

