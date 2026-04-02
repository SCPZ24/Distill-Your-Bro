from backend.models.model import ModelManager

model_manager = ModelManager.get_instance()

model = model_manager.get_model()

def activate_soul(bro_name: str, chat_message: str):
    prompt = f"{bro_name}的灵魂是：\n{chat_message}"
    response = model.generate(prompt)
    return response