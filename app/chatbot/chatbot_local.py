import json
import uuid
import requests

from app.chatbot.strategy.strategy_analysis import run_analysis_pipeline
# from strategy.strategy_analysis import run_analysis_pipeline

class NegotiationBot:
    def __init__(self, model_host="localhost", model_port=11434, model="mistral:latest"):
        self.session_id = None
        self.messages = []
        self.model = model
        self.model_url = f"http://{model_host}:{model_port}/api/chat"
        self.headers = {"Content-Type": "application/json"}
        self.memory = {}
        self.sessions = {}  # Local storage for sessions instead of API

    def create_session(self, max_price: float, min_price: float, target_price: float, product_id: str, flexibility: float = 0.1, negotiation_strategy: str = "standard"):
        """Create a new negotiation session locally"""
        session_id = str(uuid.uuid4())
        session_data = {
            "session_id": session_id,
            "parameters": {
                "max_price": max_price,
                "min_price": min_price,
                "target_price": target_price,
                "product_id": product_id,
                "flexibility": flexibility,
                "negotiation_strategy": negotiation_strategy
            },
            "messages": []
        }
        
        self.sessions[session_id] = session_data
        self.session_id = session_id
        return session_data
    
    def load_session(self, session_id: str):
        """Load an existing negotiation session from local storage"""
        if session_id in self.sessions:
            self.session_id = session_id
            self.messages = self.sessions[session_id]["messages"]
            return self.sessions[session_id]
        else:
            raise Exception(f"Session {session_id} not found")

    def update_parameters(self, **kwargs):
        """Update negotiation parameters locally"""
        if not self.session_id:
            raise Exception("No active session. Create or load a session first.")
        
        # Get current parameters
        parameters = self.sessions[self.session_id]["parameters"]
        
        for key, value in kwargs.items():
            if key in parameters:
                parameters[key] = value
        
        return {"message": "Parameters updated successfully"}
    
    def enrich_with_analysis(self, user_input):
        if user_input not in self.memory:
            self.memory[user_input] = run_analysis_pipeline(user_input)
            
        if len(self.memory) > 10:
            self.memory.pop(next(iter(self.memory)))
        return self.memory[user_input]

    def build_payload(self, prompt): 
        return {
            "model": self.model,
            "options": {"temperature": 0.0},
            "stream": True,
            "messages": [
                {"role": "system", "content": "You are a helpful negotiation assistant."},
                {"role": "user", "content": prompt}
            ]
        }
    
    def send_streaming_request(self, payload):
        try:
            response = requests.post(self.model_url, json=payload, headers=self.headers, stream=True)

            if response.status_code == 200:
                return response
            else:
                print(f"API Error: {response.status_code} - {response.text}")
                return None
        except requests.exceptions.RequestException as e:
            print(f"Request failed: {e}")
            return None

    def process_stream(self, response):
        full_reply = ""
        try:
            for line in response.iter_lines():
                if line:
                    try:
                        res = json.loads(line.decode('utf-8'))
                        content = res.get('message', {}).get('content', '')
                        full_reply += content

                    except json.JSONDecodeError as e:
                        print(f"\n[Error decoding JSON in stream: {e}]")
                        continue
                    
                    except Exception as e:
                        print(f"\n[Error processing stream chunk: {e}]")
                        continue
            print()
            return full_reply
        finally:
            response.close()  


    def send_message(self, user_input):
        if not self.session_id:
            raise Exception("No active session.")
        
        context = self.sessions[self.session_id]["parameters"]
        enriched_input = self.enrich_with_analysis(user_input)
        
        import re
        price_mentions = re.findall(r'\$?(\d+(?:\.\d+)?)', user_input)
        mentioned_price = float(price_mentions[0]) if price_mentions else None

        strategy_guidance = ""

        if mentioned_price is not None:
            max_price = context['max_price']
            target_price = context['target_price'] 
            min_price = context['min_price']
            strategy = context['negotiation_strategy']
            
            if strategy == "aggressive":
                if mentioned_price > target_price:
                    strategy_guidance = f"""
                    Since the user is offering {mentioned_price}, which is above our target of {target_price}, 
                    we should push for an even higher price. Counter with a price closer to our maximum of {max_price}.
                    """
                else:
                    strategy_guidance = f"""
                    Since the user is offering {mentioned_price}, which is below our target of {target_price}, 
                    we should strongly counter with a price at or above our target.
                    """
            if strategy == "standard":
                if mentioned_price > target_price:
                    strategy_guidance = f"""
                    Since the user is offering {mentioned_price}, which is above our target of {target_price}, 
                    we should push for an even higher price. Counter with a price closer to our maximum of {max_price}.
                    """
                else:
                    strategy_guidance = f"""
                    Since the user is offering {mentioned_price}, which is below our target of {target_price}, 
                    we should strongly counter with a price at or above our target.
                    """

        prompt = f"""Negotiation Parameters:
                        - Max Price: {context['max_price']}
                        - Target: {context['target_price']}
                        - Min Price: {context['min_price']}
                        - Flexibility: {context['flexibility']}
                        - Strategy: {context['negotiation_strategy']}

                    {strategy_guidance}
                    {enriched_input}

                    USER INPUT: {user_input}
                    
                    CRITICAL INSTRUCTION: You are in a direct negotiation. Respond with ONLY the exact words you would say to the customer. Do not include any explanations or reasoning. When they mention a specific price:
                    - If they offer MORE than our target price, try to increase it further (especially with aggressive strategy)
                    - If they offer LESS than our target price, counter closer to our target
                    
                    Your response should be a single direct statement about price."""

        payload = self.build_payload(prompt)
        response = self.send_streaming_request(payload)

        if response:
            full_reply = self.process_stream(response)

            import re
            quoted_text = re.findall(r'"([^"]*)"', full_reply)

            if quoted_text:
                reply = quoted_text[0]
            else:
                sentences = re.split(r'(?<=[.!?])\s+', full_reply)
                relevant_sentences = [s for s in sentences if any(word in s.lower() for word in ["price", "deal", "offer", "$"])]

                if relevant_sentences:
                    reply = min(relevant_sentences, key=len)
                else:
                    reply = full_reply
            self.save_message_locally("user", user_input)
            self.save_message_locally("assistant", reply)
            return reply
        else:
            fallback_reply = "I'm having trouble connecting to the model service."
            print(f"\nFallback response: {fallback_reply}")
            self.save_message_locally("user", user_input)
            self.save_message_locally("assistant", fallback_reply)
            return fallback_reply
    
    def save_message_locally(self, role, content):
        message = {"role": role, "content": content}
        self.sessions[self.session_id]["messages"].append(message)
        self.messages = self.sessions[self.session_id]["messages"]


        
    def chat(self):
        print("Start chatting with the AI (type 'exit' or 'quit' to stop):")
        while True:
            try:
                user_input = input("You: ").strip()
                if user_input.lower() in {"exit", "quit"}:
                    print("Exiting chat.")
                    break

                if not user_input:
                    print("Please provide a valid input.")
                    continue

                print(f"\n[User]: {user_input}")
                ai_reply = self.send_message(user_input)
                print(f"\n[AI]: {ai_reply}")

            except KeyboardInterrupt:
                print("\nChat interrupted. Exiting.")
                break
            except Exception as e:
                print(f"Unexpected error: {e}")
                continue


if __name__ == "__main__":

    bot = NegotiationBot()
    try:
        session = bot.create_session(
            max_price=1000,
            min_price=850,
            target_price=700,
            product_id="truck_loads",
            flexibility=0.15,
            negotiation_strategy="simple"
        )
        print(f"[Session Created] ID: {session['session_id']}")

    except Exception as e:
        print(f"[Error] Could not create session: {e}")
        
    try:
        bot.chat()

    except Exception as e:
        print(f"[Error] Failed during message exchange: {e}")