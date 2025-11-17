from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional, List
import os
import base64
from vaultwarden.clients.bitwarden import BitwardenAPIClient
from vaultwarden.models.bitwarden import get_organization
from vaultwarden.utils.crypto import decrypt, encrypt
import uuid

class VaultwardenService:
    
    def __init__(self):
        """
            Constructor for the VaultwardenService class.
            Initializes the name and breed of a bitwarden instance.
        """
        self.bitwarden = BitwardenAPIClient(url, email, password, client_id, client_secret, device_id)

# Set env variables
# ---------- Configuration ----------
#set environment or inline here os.environ['BITWARDEN_URL']=""
#set environment or inline here os.environ['BITWARDEN_EMAIL']=""
#set environment or inline here os.environ['BITWARDEN_PASSWORD']=""
#set environment or inline here os.environ['BITWARDEN_CLIENT_ID']=""
#set environment or inline here os.environ['BITWARDEN_CLIENT_SECRET']=""
#set environment or inline here os.environ['BITWARDEN_ORGANIZATION']=""
#set environment or inline here os.environ['BITWARDEN_DEVICE_ID']=""

# Get Bitwarden credentials from environment variables
url = os.environ.get("BITWARDEN_URL", None)
email = os.environ.get("BITWARDEN_EMAIL", None)
password = os.environ.get("BITWARDEN_PASSWORD", None)
client_id = os.environ.get("BITWARDEN_CLIENT_ID", None)
client_secret = os.environ.get("BITWARDEN_CLIENT_SECRET", None)
device_id = os.environ.get("BITWARDEN_DEVICE_ID", None)
organization = os.environ.get("BITWARDEN_ORGANIZATION", None)

vaultwardenservice = VaultwardenService()
app = FastAPI(title="Vaultwarden REST API Service", version="1.0")

# ---------- Models ----------

class EncryptRequest(BaseModel):
    plaintext: str

class DecryptRequest(BaseModel):
    ciphertext: str

class OrgRequest(BaseModel):
    org_id: str
    name: Optional[str] = None
    description: Optional[str] = None

class OrgRenameRequest(BaseModel):
    org_id: str
    name: str
    description: Optional[str] = None

class CollectionRequest(BaseModel):
    org_id: str
    name: Optional[str] = None
    description: Optional[str] = None

class EntityRequest(BaseModel):
    id: Optional[str] = None
    name: str
    org_id: Optional[str] = None
    username: Optional[str] = None
    password: Optional[str] = None
    notes: Optional[str] = None

class CollectionOrganizationRequest(BaseModel):
    org_id: str
    collection_id: str
    
class InviteRequest(BaseModel):
    org_id: str
    collection_id: str
    email: str
    
class OrganizationUserRequest(BaseModel):
    org_id: str
    email: str

class OrganizationCollectionUserRequest(BaseModel):
    org_id: str
    collection_id: str
    email: str

class NewOrgRequest(BaseModel):
    name: str
    email: str
    
class OrgCipherRequest(BaseModel):
    org_id: str
    cipher_id: str

class LoginCipherRequest(BaseModel):
    name: str
    username: str = None
    password: str = None
    uris: Optional[list[str]] = None 
    uri: Optional[str] = None
    type: int = 1, 
    folder_id: Optional[str] = None
    org_id: str
    collection_ids: Optional[list[str]] = None
    notes: Optional[str] = None
    favorite: Optional[bool] = False
    fields: Optional[list[dict]] = None 
    
class CardCipherRequest(BaseModel):
    name: str 
    brand: str = None 
    cardholderName: str = None 
    code: str = None 
    expMonth: str = None 
    expYear: str = None 
    number: str = None 
    uris: list[str] = None 
    uri: str = None 
    type: int = 3 
    folder_id: str = None 
    org_id: str = None 
    collection_ids: list[str] = None 
    notes: str = None 
    favorite: bool = False 
    fields: list[dict] = None    
    

# ---------- Encryption / Decryption ----------
@app.post("/encrypt")
def encrypt_value(req: EncryptRequest):
    try:
        org = get_organization(vaultwardenservice.bitwarden, organization)
        key = org.key()
        enc = encrypt(2, req.plaintext, key)
        return {"ciphertext": enc}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/decrypt")
def decrypt_value(req: DecryptRequest):
    try:
        org = get_organization(vaultwardenservice.bitwarden, organization)
        key = org.key()
        dec = decrypt(req.ciphertext, key).decode("utf-8")        
        return {"plaintext": dec}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ---------- Organisation APIs ----------
# view organization
@app.get("/org")
def get_org(req: OrgRequest):
    organization = get_organization(vaultwardenservice.bitwarden, req.org_id)
    #return {"id": organization.Id, "name": organization.Name}
    return organization
    
@app.get("/org/ciphers")
def list_entities(req: OrgRequest):
    organization = get_organization(vaultwardenservice.bitwarden, req.org_id)
    ciphers = organization.ciphers()
    return [
        {
            "id": c.Id,
            "name": c.Name,
            "entity details": c
        }
        for c in ciphers
    ]

@app.get("/org/collection/ciphers")
def list_entities(req:CollectionOrganizationRequest):
    organization = get_organization(vaultwardenservice.bitwarden, req.org_id)
    ciphers = organization.ciphers(uuid.UUID(req.collection_id))
    return [
        {
            "id": c.Id,
            "name": c.Name,
            "entity details": c
        }
        for c in ciphers
    ]

@app.get("/collection")
def list_collections(req: CollectionRequest):
    organization = get_organization(vaultwardenservice.bitwarden, req.org_id)
    org_colls = organization.collections()
    return org_colls

@app.post("/collection")
def add_collection(org_id: str, collection_name: str):
    organization = get_organization(vaultwardenservice.bitwarden, org_id)
    organizationcollection = organization.create_collection(collection_name)
    return {"added": ok, "id": organizationcollection.Id, "name":organizationcollection.Name}

@app.get("/collection/{collection_id}")
def get_collection(org_id: str, collection_id: str):
    organization = get_organization(vaultwardenservice.bitwarden, org_id)
    org_coll = organization.collection(collection_id)
    return org_coll

@app.get("/org/users")
def get_org_users(req: OrgRequest):
    organization = get_organization(vaultwardenservice.bitwarden, req.org_id)
    return organization.users()    

@app.delete("/collection")
def delete_collection(req: CollectionOrganizationRequest):
    organization = get_organization(vaultwardenservice.bitwarden, req.org_id)
    ok = organization.delete_collection(uuid.UUID(req.collection_id))
    return {"deleted": ok, "Id": req.collection_id}

@app.get("/org/user")
def search_user(req: OrganizationUserRequest):
    organization = get_organization(vaultwardenservice.bitwarden, req.org_id)
    return organization.user_search(req.email)    


@app.post("/organization/users/invite")
def invite(req: InviteRequest):
    organization = get_organization(vaultwardenservice.bitwarden, req.org_id)
    org_coll = organization.collection(req.collection_id)    
    invite = organization.invite(req.email)
    return {invite}
    
@app.put("/org/rename")
def rename_org(req: OrgRenameRequest):
    organization = get_organization(vaultwardenservice.bitwarden, req.org_id)
    if hasattr(organization, 'rename'):
        organization.rename(req.name)
        return {"id": req.org_id, "renamed to": req.name}
    else:
        print("organization has no attribute 'rename'")
        return {"id": req.org_id}

#---create org ----
@app.post("/org/create")
def add_org(org: NewOrgRequest):
    response = vaultwardenservice.bitwarden.create_organisation(org.name, org.email)
    return {response.is_success}
    
@app.delete("/org/user")
def delete_user(req: OrganizationUserRequest):
    organization = get_organization(vaultwardenservice.bitwarden, req.org_id)
    user = organization.user_search(req.email)    
    resp = user.delete()
    return {"deleted user": resp, "Id": req.email}   
    
@app.get("/org/collection/users")
def get_users_of_collection(req:CollectionOrganizationRequest):
    organization = get_organization(vaultwardenservice.bitwarden, req.org_id)
    org_colls_names = organization.collections(as_dict=True)
    users = org_colls_names.get(req.collection_id).users()
    return users

@app.post("/cipher/login/create")
def create_login_cipher(req: LoginCipherRequest):
    organization = get_organization(vaultwardenservice.bitwarden, req.org_id)
    cipher = organization.create_login_cipher(req.name, req.username, req.password, req.uris, req.uri, req.type, req.folder_id, req.org_id, req.collection_ids, req.notes, req.favorite, req.fields)
    return cipher
    
@app.delete("/cipher/delete")
def delete_cipher(req: OrgCipherRequest):
    organization = get_organization(vaultwardenservice.bitwarden, req.org_id)
    cipher = organization.delete_cipher(req.cipher_id)
    return {"deleted Id": req.cipher_id}
    
@app.post("/cipher/card/create")
def create_card_cipher(req: CardCipherRequest):
    organization = get_organization(vaultwardenservice.bitwarden, req.org_id)
    print("in card cipher")
    if req.brand == "VISA":
        req.brand = "Visa"
    if req.brand == "MASTERCARD" or req.brand == "MasterCard":
        req.brand = "Mastercard"
    if req.brand == "AMEX" or req.brand == "Americanexpress" or req.brand == "AmericanExpress" or req.brand == "AMERICANEXPRESS":
        req.brand = "Amex"
    if req.brand == "RUPAY" or req.brand == "rupay" or req.brand == "Rupay":
        req.brand = "RuPay"
    cipher = organization.create_card_cipher(req.name, req.brand, req.cardholderName, req.code, req.expMonth, req.expYear, req.number, req.uris, req.uri, req.type, req.folder_id, req.org_id, req.collection_ids, req.notes, req.favorite, req.fields)
    return cipher    

# ---------- Root ----------
@app.get("/")
def root():
    return {"status": "ok", "message": "Vaultwarden REST API running"}
