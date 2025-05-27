from tools.negotiation_tools import detect_emotion

def run_analysis_pipeline(user_input):
    analysis = {
        "sentiment": f"{detect_emotion(user_input)}",
        "intent": "price_negotiation",                              # add this model (not trained yet) "f{negotiation_context(user_input)}"   
        "key_entities": ["price", "deal"],
        "analysis": f"User is discussing price points around {user_input}"
        }
    return analysis 

    
# if __name__ == "__main__":
#     print(run_analysis_pipeline("I can offer $10,000 for the truck load, but only if you include a 6-month warranty."))
