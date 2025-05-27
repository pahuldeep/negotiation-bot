import requests
import json

from app.chatbot.prompt.prompt_extractor import PromptExtractor

# ==================================================
# NEGOTAITION CONTEXT
# ==================================================
class NegotiationContext:
    def __init__(self, model="mistral", ollama_url="http://localhost:11434/api/generate"):
        self.model = model
        self.ollama_url = ollama_url
        self.prompt_extractor = PromptExtractor()
        
    def extract(self, user_input):

        prompt = self.prompt_extractor.extracted_type_extended(user_input)
        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": False
        }
        try:
            response = requests.post(self.ollama_url, json=payload)
            if response.status_code == 200:
                return json.loads(response.json()["response"])
            else:
                raise ConnectionError(f"Ollama API error: {response.status_code} {response.text}")
            
        except (requests.exceptions.RequestException, json.JSONDecodeError):
            print(" Switching to mock mode due to Ollama failure.")
            return {
                "name": "NegotiationContext",
                "context": { "@start": True, "user_input": user_input },
                "type": "Unknown"
            }
        
    
    # def generate_context_summary(self, extracted_context):
    #     filled_details = []
        
    #     prefix_key = "extracted_context"
    #     type_key = "@type"
    #     params_key = "parameters"
    #     no_params_msg = "No filled parameters were found in the extracted negotiation contexts."
    #     type_template = "In the ({}) "
    #     list_template = '"{}" contains {} value(s): {}'
    #     str_template = '"{}" is set to "{}"'

    #     for key, context in extracted_context.items():
    #         if key.startswith(prefix_key) and isinstance(context, dict):
    #             context_type = context.get(type_key, "Unknown Type")
    #             parameters = context.get(params_key, {})

    #             filled_params = []
    #             for param, value in parameters.items():
    #                 if isinstance(value, list) and value:
    #                     filled_params.append(list_template.format(param, len(value), value))
    #                 elif isinstance(value, str) and value.strip():
    #                     filled_params.append(str_template.format(param, value))

    #             if filled_params:
    #                 paragraph = type_template.format(context_type) + "; ".join(filled_params) + "."
    #                 filled_details.append(paragraph)

    #     return " ".join(filled_details) if filled_details else no_params_msg


# if __name__ == "__main__":

#     extractor = NegotiationContext(model="mistral")
    
#     negotiation_text = "I can offer $10,000 for the truck load, but only if you include a 6-month warranty."

#     print("\n--- Extracting Negotiation Context ---")
#     extracted_context = extractor.extract(negotiation_text)  
#     print(json.dumps(extracted_context, indent=4))

        # context_result = extractor.generate_context_summary(extracted_context) 
    # print(context_result)
