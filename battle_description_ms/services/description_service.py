import grpc
from utils import openrouter_utils, mongo_utils
import os
import sys

# Получаем абсолютный путь к корневой директории проекта
project_root = os.path.dirname(os.path.dirname(__file__))

# Добавляем путь к protobuf в sys.path
sys.path.append(os.path.join(project_root, "protobuf"))

import battle_description_pb2
import battle_description_pb2_grpc

class DescriptionService(battle_description_pb2_grpc.DescriptionServiceServicer):
    def GenerateDescription(self, request, context):
        print("aboba")
        first_char_id = request.first_char_id
        second_char_id = request.second_char_id

        first_character = mongo_utils.get_character_by_id(first_char_id)
        second_character = mongo_utils.get_character_by_id(second_char_id)

        if not first_character or not second_character:
            context.set_code(grpc.StatusCode.NOT_FOUND)
            context.set_details("Один или оба персонажа не найдены")
            return battle_description_pb2.DescriptionResponse()

        battle_description = openrouter_utils.get_dnd_battle_description(first_character, second_character)
        return battle_description_pb2.DescriptionResponse(battle_description=battle_description)