# vaultwarden-api-client
FastAPI based client for building and hosting APIs with Python

## Start container
uvicorn vaultwarden_service:app --reload --port 8080

## curl
### Get org
curl -X GET http://localhost:8080/org -H "Content-Type: application/json" -d '{"org_id": “532f2c11-5001-6adcc-a42-94522326b33"}'

similarly you can curl
### Collection - Add
### Collection - Delete
### Collection - All List
### Collection - User List
### Decrypt
### Encrypt
### Entity (Cipher login) - Add
### Entity (Cipher card) - Add
### Entity (Cipher) - Delete
### Entity (Cipher) - Org level List
### Entity (Cipher) - Collection level List
### Organisation - Specific Retrieve
### Organisation - Users List
### Organisation - Specific User Search
### Organisation - User Invite
### Organisation - User Delete
### Organisation - Rename
### Organisation - Add
