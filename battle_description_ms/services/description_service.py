import grpc
import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'common'))
from common import openrouter_utils, mongo_utils


# Получаем абсолютный путь к корневой директории проекта
project_root = os.path.dirname(os.path.dirname(__file__))


# Добавляем путь к protobuf в sys.path
sys.path.append(os.path.join(project_root, "protobuf"))



import battle_description_pb2
import battle_description_pb2_grpc

class DescriptionService(battle_description_pb2_grpc.DescriptionServiceServicer):
    
    def __init__(self):
        super().__init__()  
        self.generator = openrouter_utils.DnDBattleGenerator()
    
    def GenerateDescription(self, request, context):
       
        first_char_id = request.first_char_id
        second_char_id = request.second_char_id

        first_character = mongo_utils.get_character_by_id(first_char_id)
        
        second_character = mongo_utils.get_character_by_id(second_char_id)

        if not first_character or not second_character:
            context.set_code(grpc.StatusCode.NOT_FOUND)
            context.set_details("Один или оба персонажа не найдены")
            return battle_description_pb2.DescriptionResponse()
        
        battle_description = self.generator.get_battle_description(first_character, second_character)
        return battle_description_pb2.DescriptionResponse(battle_description=battle_description)