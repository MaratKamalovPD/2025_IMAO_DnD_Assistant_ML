import grpc
from concurrent import futures
from services import description_service
import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), "protobuf"))

import battle_description_pb2_grpc

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    battle_description_pb2_grpc.add_DescriptionServiceServicer_to_server(
        description_service.DescriptionService(), server
    )
    server.add_insecure_port("[::]:50051")
    print("Сервер запущен на порту 50051...")
    server.start()
    server.wait_for_termination()

if __name__ == "__main__":
    serve()