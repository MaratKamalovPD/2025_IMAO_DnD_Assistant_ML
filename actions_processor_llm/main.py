# actions_processor_ms/main.py

import os
import sys
import grpc
from concurrent import futures
import logging
from actions_processor_llm.services import action_processor_service

sys.path.append(os.path.join(os.path.dirname(__file__), "protobuf"))


import actions_processor_llm_pb2_grpc as pb2_grpc


def serve():
    logging.basicConfig(level=logging.INFO)
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))

    pb2_grpc.add_ActionProcessorServiceServicer_to_server(
        action_processor_service.ActionProcessorService(),
        server
    )

    server.add_insecure_port("[::]:50052")
    logging.info("ActionProcessorService запущен на порту 50052...")
    server.start()
    server.wait_for_termination()

if __name__ == "__main__":
    serve()
