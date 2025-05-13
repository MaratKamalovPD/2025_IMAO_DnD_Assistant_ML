import grpc
import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), "protobuf"))

from actions_processor_llm_pb2 import Action, ActionList
from actions_processor_llm_pb2_grpc import ActionProcessorServiceStub


def run():
    with grpc.insecure_channel("localhost:50052") as channel:
        stub = ActionProcessorServiceStub(channel)

        # Пример списка действий, как в твоем JSON
        actions = [
            Action(
                name="Короткий меч",
                value="<p><em>Рукопашная атака оружием:</em> +4 к попаданию...</p>"
            ),
            Action(
                name="Ручной арбалет",
                value="<p><em>Дальнобойная атака:</em> +4 к попаданию...</p>"
            )
        ]

        request = ActionList(actions=actions)
        response = stub.ProcessActions(request)

        print("Ответ от сервера:")
        print(response)

if __name__ == "__main__":
    run()
