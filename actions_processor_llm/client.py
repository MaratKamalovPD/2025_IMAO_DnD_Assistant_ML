import grpc
import os
import sys
from google.protobuf.json_format import MessageToDict

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
                value="<p><em>Рукопашная атака оружием:</em> <dice-roller label=\"Атака\" formula=\"к20 + 4\">+4</dice-roller> к попаданию, досягаемость 5 фт., одна цель. <em>Попадание:</em>&nbsp;5&nbsp;(<dice-roller label=\"Урон\" formula=\"1к6 + 2\"/>) колющего урона.</p>"
            ),
            Action(
                name="Ручной арбалет",
                value="<p><em>Дальнобойная атака оружием:</em> <dice-roller label=\"Атака\" formula=\"к20 + 4\">+4</dice-roller> к попаданию, дистанция 30/120 фт., одна цель. <em>Попадание:</em>&nbsp;5&nbsp;(<dice-roller label=\"Урон\" formula=\"1к6 + 2\"/>) колющего урона. Белдора носит с собой 10 болтов для арбалета.</p>"
            )
        ]

        request = ActionList(actions=actions)
        response = stub.ProcessActions(request)

        result_dict = MessageToDict(response, preserving_proto_field_name=True)
        print("Ответ от сервера:")
        print(result_dict["parsed_actions"])

if __name__ == "__main__":
    run()
