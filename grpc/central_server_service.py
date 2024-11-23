import sys
import os
import grpc
from concurrent import futures

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), 'stubs')))

import grpc_servers_pb2 as grpc_servers_pb2_
import grpc_servers_pb2_grpc as grpc_servers_pb2_grpc_
from google.protobuf.empty_pb2 import Empty

class CentralServerService(grpc_servers_pb2_grpc_.ManagerServiceServicer):
    def __init__(self):
        self.workers = []
        
    def Subscribe(self, request, context):
        print("SUBSCRIBE IS BEING CALLED")
        worker_info = {"id": request.id, "address": request.ip_address}

        print(worker_info)
        self.workers.append(worker_info)
        
        # print(f"Worker {request.id} subscribed with address {request.address}")
        
        return Empty()
    
    def SendJob(self, request, context):
        return Empty()
    
server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
grpc_servers_pb2_grpc_.add_ManagerServiceServicer_to_server(CentralServerService(), server)
print("GRPC SERVER IS ABOUT TO START")
server.add_insecure_port("[::]:50051")
server.start()
server.wait_for_termination()