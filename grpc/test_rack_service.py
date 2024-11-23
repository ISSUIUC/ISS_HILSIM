import grpc
import sys
import os
from concurrent import futures

import socket

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), 'stubs')))

import grpc_servers_pb2 as grpc_servers_pb2_
import grpc_servers_pb2_grpc as grpc_servers_pb2_grpc_
from google.protobuf.empty_pb2 import Empty

def check_channel_validity(channel, stub_class, rpc_method, **rpc_kwargs):
    try:
        stub = stub_class(channel)
        getattr(stub, rpc_method)(**rpc_kwargs)
        return True
    except grpc.RpcError:
        return False

class TestRackServerService(grpc_servers_pb2_grpc_.TestRackServiceServicer):
    def __init__(self, port):
        self.hostname = socket.gethostbyname_ex(socket.gethostname())[2][0]
        self.port = int(port)
        # print("http://" + self.hostname + "::" + str(self.port))
        self.channel = grpc.insecure_channel('localhost:50051')
        self.client_stub = grpc_servers_pb2_grpc_.ManagerServiceStub(self.channel)

        print(grpc_servers_pb2_.WorkerInfo().DESCRIPTOR.fields[0].name)

        self.client_stub.Subscribe(grpc_servers_pb2_.WorkerInfo(id='1', ip_address="http://localhost:3000"))

        pass

    def SubscribeToServer(self, request, context):
        return Empty()

    def ExecuteJob(self, request, context):
        return Empty()
    
server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
grpc_servers_pb2_grpc_.add_TestRackServiceServicer_to_server(TestRackServerService(50052), server)
server.add_insecure_port("[::]:50052")
server.start()
server.wait_for_termination()