import grpc
import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), "protobuf"))

import battle_description_pb2
import battle_description_pb2_grpc

def run():
    with grpc.insecure_channel("localhost:50051") as channel:
        stub = battle_description_pb2_grpc.DescriptionServiceStub(channel)
        response = stub.GenerateDescription(battle_description_pb2.DescriptionRequest(
            first_char_id="67d3240109e0f17fbfeddf2f",  # Замените на реальный ID
            second_char_id="67d3240192f29f3c32eddf2f"  # Замените на реальный ID
        ))
        print("Описание битвы:", response.battle_description)

if __name__ == "__main__":
    run()