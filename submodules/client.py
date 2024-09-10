import grpc
import requests
from protos.proto.src.python.czorg.abc-service.v1 import abc_service_pb2 as abc_pb
from protos.proto.src.python.czorg.abc-service.v1 import abc_service_pb2_grpc as abc_grpc

def main():
    # === Secrets ===
    client_id = '<>'
    client_secret = '<>'
    cert_path = './org.ca.crt'

    sso_url = 'https://sso.czorg.com/adfs/oauth2/token'
    sso_resource = 'org.czorg.com'
    service_endpoint = "service.czorg.com"
    port = "443"

    # dynamically generate a bearer token
    bearer_token = generate_bearer_token(sso_url, client_id, sso_resource, client_secret)

    # read in certificate
    with open(cert_path, 'rb') as f:
        trusted_certs = f.read()

    # create credentials
    credentials = grpc.ssl_channel_credentials(root_certificates=trusted_certs)

    # open a connection to the endpoint, closed automatically based on scope
    with  grpc.secure_channel('{}:{}'.format(service_endpoint, port), credentials) as channel:
        metadata = (("authorization", "Bearer " + bearer_token),)
        stub = abc_grpc.ABCServiceStub(channel)

        request = abc_pb.GetAbcRequest(abc='abc-input')
        response = stub.GetAbc(request=request, metadata=metadata)
        print(f"Response: {response}")

# dynamically generate a bearer token
def generate_bearer_token(sso_url, client_id, sso_resource, client_secret):
    urlencode = {'client_id': client_id,
                 'client_secret': client_secret,
                 'resource': sso_resource,
                 'grant_type': 'client_credentials'}

    response = requests.post(sso_url, data=urlencode)

    if response.status_code == 200:
        return response.json()['access_token']
    else:
        msg = "GenerateBearerToken: Error " + str(
            response.status_code) + ": Cannot generate access token. Detail: " + response.text
        print(msg)
        return msg

if __name__ == '__main__':
    main()
