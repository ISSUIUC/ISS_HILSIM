import sys
import os
import grpc
from concurrent import futures

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), 'stubs')))

import central_server_pb2 as central_server_pb2_
import central_server_pb2_grpc as central_server_pb2_grpc_
from google.protobuf.empty_pb2 import Empty

class CentralServerService(central_server_pb2_grpc_.ManagerServiceServicer):
    def __init__(self):
        self.workers = []
        
    def Subscribe(self, request, context):
        worker_info = {"id": request.id, "address": request.address}
        self.worker_list.append(worker_info)
        
        print(f"Worker {request.id} subscribed with address {request.address}")
        
        return Empty()
    
    def SendJob(self, request, context):
        return Empty()
    
server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
central_server_pb2_grpc_.add_ManagerServiceServicer_to_server(CentralServerService(), server)
server.add_insecure_port("[::]:50051")
server.start()
server.wait_for_termination()