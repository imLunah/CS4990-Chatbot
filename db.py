import boto3


class ChatDB:
    def __init__(self):
        dynamodb = boto3.resource("dynamodb", region_name="us-west-1")
        self.table = dynamodb.Table("chatbot")

    def is_user_exist(self, user_id: str):
        response = self.table.get_item(Key={"user_id": user_id})
        return "Item" in response
    
    def get_user_hashed_password(self, user_id: str):
        if not self.is_user_exist(user_id):
            raise Exception("User does not exist")
        
        response = self.table.get_item(Key={"user_id": user_id})
        return response["Item"]["hashed_password"]

    def is_login_valid(self, user_id: str, hashed_password: str):
        response = self.table.get_item(Key={"user_id": user_id})
        if "Item" not in response:
            return False
        return response["Item"]["hashed_password"] == hashed_password

    def create_user(self, user_id: str, hashed_password: str):
        # check if user_id already exists
        if self.is_user_exist(user_id):
            raise Exception("User already exists")

        self.table.put_item(
            Item={
                "user_id": user_id,
                "hashed_password": hashed_password,
                "conversations": [],
            }
        )

    def update_password(self, user_id: str, hashed_password: str):
        # check if user_id already exists
        if not self.is_user_exist(user_id):
            raise Exception("User does not exist")

        self.table.update_item(
            Key={"user_id": user_id},
            UpdateExpression="set hashed_password=:p",
            ExpressionAttributeValues={":p": hashed_password},
        )

    def save_chat(
        self, user_id: str, chat_history: list[dict], conversation_id: int = 0
    ):
        if not self.is_user_exist(user_id):
            raise Exception("User does not exist")

        response = self.table.get_item(Key={"user_id": user_id})
        conversations = response["Item"]["conversations"]

        # new conversation
        if conversation_id == 0:
            max_conversation_id = max(
                (c["conversation_id"] for c in conversations), default=0
            )
            conversations.append(
                {
                    "title": chat_history[0]['parts'][0] if len(chat_history) > 0 else "New Conversation",
                    "conversation_id": max_conversation_id + 1,
                    "content": chat_history,
                }
            )
        else:
            not_found = True
            for i, conversation in enumerate(conversations):
                if int(conversation["conversation_id"]) == conversation_id:
                    conversations[i]["content"] = chat_history
                    conversations[i]["title"] = chat_history[0]['parts'][0]
                    not_found = False
                    break

            if not_found:
                raise Exception("Conversation does not exist")

        self.table.update_item(
            Key={"user_id": user_id},
            UpdateExpression="set conversations=:c",
            ExpressionAttributeValues={":c": conversations},
        )

    def delete_conversation(self, user_id: str, conversation_id: str):
        if not self.is_user_exist(user_id):
            raise Exception("User does not exist")

        response = self.table.get_item(Key={"user_id": user_id})
        conversations = response["Item"]["conversations"]

        for i, conversation in enumerate(conversations):
            if conversation["conversation_id"] == conversation_id:
                del conversations[i]
                break

        self.table.update_item(
            Key={"user_id": user_id},
            UpdateExpression="set conversations=:c",
            ExpressionAttributeValues={":c": conversations},
        )

    def get_conversation(self, user_id: str, conversation_id: int) -> list[dict]:
        if not self.is_user_exist(user_id):
            raise Exception("User does not exist")

        response = self.table.get_item(Key={"user_id": user_id})
        conversations = response["Item"]["conversations"]

        for conversation in conversations:
            if conversation["conversation_id"] == conversation_id:
                return conversation["content"]
            
        raise Exception("Conversation does not exist")
    
    def get_all_conversation_titles(self, user_id: str) -> list[dict]:
        if not self.is_user_exist(user_id):
            raise Exception("User does not exist")

        response = self.table.get_item(Key={"user_id": user_id})
        conversations = response["Item"]["conversations"]

        return [
            {"conversation_id": c["conversation_id"], "title": c["title"]}
            for c in conversations
        ]
