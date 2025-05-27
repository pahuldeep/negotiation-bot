
class PromptExtractor:


    def extracted_context(self, user_input):
        return f"""You are an AI system specialized in extracting structured negotiation data from natural language text.
        Your task is to read the input carefully, identify the type of negotiation context, and return a well-structured JSON object with correctly populated fields based on the content.

        Input: "{user_input}"

        Output format:
        {{
            "negotiation_context": {{
                "@type": "Negotiation_Context",
                "parameters": {{
                    "roles_involved": [],              // All roles participating (distributor, receiver, team members, etc.)
                    "interests_and_values": {{}},      // Key values, offers, requests, interests, etc.
                    "strategies_or_tactics": [],       // Tactics, approaches, reasons for avoidance, etc.
                    "intended_outcomes": []            // Goals, proposed solutions, mutual gains, etc.
                }}
            }}
        }}

        Respond only with the JSON object.
        """


    def extracted_type(self, user_input):
        return f"""You are an AI system specialized in extracting structured negotiation context from natural language input.
        Read the following input carefully and return a complete JSON object. Identify and populate relevant context types with appropriate parameters.

        Input: "{user_input}"

        Output format:
        {{
            "name": "NegotiationContext",
            "context": {{
                "@start": true,
                "user_input": "{user_input}"
            }},
            "extracted_contexts": {{
                "Distributive": {{
                    "parameters": {{ /* extracted values */ }}
                }},
                "Collaborative": {{
                    "parameters": {{ /* extracted values */ }}
                }},
                "Avoidance": {{
                    "parameters": {{ /* extracted values */ }}
                }},
                "Accommodation": {{
                    "parameters": {{ /* extracted values */ }}
                }},
                "Tactical_Influence": {{
                    "parameters": {{ /* extracted values */ }}
                }},
                "Multiparty_Team": {{
                    "parameters": {{ /* extracted values */ }}
                }}
            }}
        }}

        Respond only with the JSON object.
        """


    def extracted_type_extended(self, user_input):
        return f""" You are a negotiation context extractor. 
        Analyze the following statement and fill in the structured JSON template with appropriate values.
        
        Statement: "{user_input}"
        Respond only with a complete JSON object in the following format:
        {{
            "name": "NegotiationContext",
            "context": {{
                "@start": true,
                "user_input": "{user_input}"
            }},
            "distributive": {{
                "@type": "Distributive_Negotiation_Context",
                "parameters": {{
                    "distributor_role": "",
                    "receiver_role": "",
                    "offer_value": "",
                    "request_value": ""
                }}
            }},
            "collaborative": {{
                "@type": "Integrative_Collaborative_Context",
                "parameters": {{
                    "mutual_gains": "",
                    "common_interests": "",
                    "collaboration_strategy": "",
                    "stakeholder_roles": ""
                }}
            }},
            "avoidance_accommodation": {{
                "@type": "Avoidance_Accommodation_Context",
                "parameters": {{
                    "avoider_role": "",
                    "accommodator_role": "",
                    "reason_for_avoidance": "",
                    "proposed_solution": ""
                }}
            }},
            "tactical_influence_based": {{
                "@type": "Tactical_Influence_Based_Context",
                "parameters": {{
                    "influencer_role": "",
                    "target_person_role": "",
                    "tactic_used": "",
                    "desired_outcome": ""
                }}
            }},
            "multiparty_team": {{
                "@type": "Multiparty_Team_Context",
                "parameters": {{
                    "team_members": "",
                    "roles_assigned": "",
                    "conflicting_interests": "",
                    "coordination_mechanisms": ""
                }}
            }}
        }}"""