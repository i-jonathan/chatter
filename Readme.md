# Testing

This project doesn't include a frontend and so can be tested via API tools like curl or Postman.

Requires Docker and Kubernetes.

- Image is located at farinloyejonathan/chatter or can be built using
  `docker image build -t chatter .`
  Can be run with
  `docker run -p 8000:8000 chatter`
- Contains a script to run kubernetes deployment and service
  `./deploy.sh`

Server IP would be the local address of the machine. Typically `127.0.0.1`

### HTTP Endpoints

- This repo contains a Postman collection file for easy importing into postman

### Alternatively the endpoints are listed below

##### Create a user account

- URL: `{{server_url}}:8000/account/register/`
- Method: POST
- Body: `{
"email": "johndoe@example.come",
"password": "jackandjill!"
}`
- Returns: api_key

##### Retrieve Chat History

- URL: `{{server_url}}:8000/chat/{{room_id}}/`
  `room_id`: Name of room provided upon websocket connection
- Method: GET
- Header:
  Key: Authorization
  Value: `{{api_key}}`

##### Mark as Read

- URL: `{{server_url}}:8000/chat/read/{{room_id}}/`
  `room_id`: Name of room provided upon websocket connection
- Method: PATCH
- Header
  Key: Authorization
  Value: `{{api_key}}`

### Websocket Endpoint

- URL: `ws://{{server_url}}:8000/ws/room/{{room_id}}/?api_key={{api_key}}`
