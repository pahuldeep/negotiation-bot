import requests
import json

from app.chatbot.strategy.strategy_analysis import run_analysis_pipeline


class NegotiationBot:
    def __init__(self, api_url, model_host="192.168.1.54", model_port=11434, model="mistral:latest"):
        self.api_url = api_url
        self.session_id = None
        self.messages = []
        self.model = model
        self.model_url = f"http://{model_host}:{model_port}/api/chat"
        self.headers = {"Content-Type": "application/json"}
        self.memory = {}

    def create_session(self, max_price: float, min_price: float, target_price: float, product_id: str, flexibility: float = 0.1, negotiation_strategy: str = "standard"):
        """Create a new negotiation session"""
        payload = {
            "max_price": max_price,
            "min_price": min_price,
            "target_price": target_price,
            "product_id": product_id,
            "flexibility": flexibility,
            "negotiation_strategy": negotiation_strategy
        }
        response = requests.post(f"{self.api_url}/negotiations", json=payload)
        
        if response.status_code == 200:
            session_data = response.json()
            self.session_id = session_data["session_id"]
            return session_data
        else:
            raise Exception(f"Failed to create session: {response.text}")
    
    def load_session(self, session_id: str):
        """Load an existing negotiation session"""
        response = requests.get(f"{self.api_url}/negotiations/{session_id}")
        if response.status_code == 200:
            session_data = response.json()
            self.session_id = session_id
            self.messages = session_data["messages"]
            return session_data
        else:
            raise Exception(f"Failed to load session: {response.text}")

    def update_parameters(self, **kwargs):
        """Update negotiation parameters"""
        if not self.session_id:
            raise Exception("No active session. Create or load a session first.")
        

        session = self.load_session(self.session_id)
        parameters = session["parameters"]
        
        for key, value in kwargs.items():
            if key in parameters:
                parameters[key] = value
        
        response = requests.put(
            f"{self.api_url}/negotiations/{self.session_id}/parameters",
            json=parameters
        )
        
        if response.status_code != 200:
            raise Exception(f"Failed to update parameters: {response.text}")
        
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

    # def send_message(self, user_input):
    #     if not self.session_id:
    #         raise Exception("No active session.")
        
    #     context = self.load_session(self.session_id)["parameters"]
    #     enriched_input = self.enrich_with_analysis(user_input)

    #     prompt = f"""Negotiation Parameters:
    #                     - Max Price: {context['max_price']}
    #                     - Target: {context['target_price']}
    #                     - Min Price: {context['min_price']}
    #                     - Flexibility: {context['flexibility']}
    #                     - Strategy: {context['negotiation_strategy']}

    #                 {enriched_input}
    #                 USER INPUT: {user_input} 
    #                 CRITICAL INSTRUCTION: You are in a direct negotiation. 
    #                 Respond with ONLY the exact words you would say to the customer. 
    #                 Do not include any explanations, preambles, or notes. 
    #                 Start immediately with your negotiation response without any prefix like "Possible reply:" or similar. 
    #                 Keep your response concise and directly addressing the price negotiation.
    #                 """

    #     payload = self.build_payload(prompt)
    #     response = self.send_streaming_request(payload)
    #     reply = self.process_stream(response)


    #     self.save_message_to_api("user", user_input)
    #     self.save_message_to_api("assistant", reply)
    #     return reply


    def send_message(self, user_input):
        if not self.session_id:
            raise Exception("No active session.")
        
        context = self.sessions[self.session_id]["parameters"]
        enriched_input = self.enrich_with_analysis(user_input)
        
        # Extract numeric values from user input for better price analysis
        import re
        price_mentions = re.findall(r'\$?(\d+(?:\.\d+)?)', user_input)
        mentioned_price = float(price_mentions[0]) if price_mentions else None
        
        # Add guidance based on the mentioned price and our strategy
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
            
            # Post-process to extract just the core negotiation response
            import re
            
            # Try to find quoted text first
            quoted_text = re.findall(r'"([^"]*)"', full_reply)
            if quoted_text:
                reply = quoted_text[0]
            else:
                # If no quotes, try to get the most relevant sentence about price
                sentences = re.split(r'(?<=[.!?])\s+', full_reply)
                # Use the shortest sentence that mentions price, deal, or offer
                relevant_sentences = [s for s in sentences if any(word in s.lower() for word in ["price", "deal", "offer", "$"])]
                if relevant_sentences:
                    reply = min(relevant_sentences, key=len)
                else:
                    reply = full_reply
            
            self.save_message_to_api("user", user_input)
            self.save_message_to_api("assistant", reply)
            return reply
        else:
            fallback_reply = "I'm having trouble connecting to the model service."
            print(f"\nFallback response: {fallback_reply}")
            self.save_message_to_api("user", user_input)
            self.save_message_to_api("assistant", fallback_reply)
            return fallback_reply


    def save_message_to_api(self, role, content):
        message = {"role": role, "content": content}
        requests.post(f"{self.api_url}/negotiations/{self.session_id}/messages", json=message)


if __name__ == "__main__":

    api_url = "http://0.0.0.0:8000"  # Replace with your actual API URL
    bot = NegotiationBot(api_url=api_url)

    # Step 1: Create a negotiation session
    try:
        session = bot.create_session(
            max_price=1000,
            min_price=700,
            target_price=850,
            product_id="abc123",
            flexibility=0.15,
            negotiation_strategy="standard"
        )
        print(f"[Session Created] ID: {session['session_id']}")

    except Exception as e:
        print(f"[Error] Could not create session: {e}")
        

    # Step 2: Simulate a user message
    try:
        user_input = "Can we close this deal around 800?"
        print(f"\n[User]: {user_input}")
        ai_reply = bot.send_message(user_input)
        print(f"\n[AI]: {ai_reply}")

    except Exception as e:
        print(f"[Error] Failed during message exchange: {e}")


