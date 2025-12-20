from smolagents import InferenceClientModel, CodeAgent,tool
import os

HF_API_KEY = os.getenv("HF_API_KEY")
@tool
def get_restaurant_recommendations(place:str)->list[str]:
    """
    Provides restaurant recommendations based on the place.
    
    Args:
        place (str): The location to find restaurants in.
        
    Returns:
        str: A list of recommended restaurants.
    """

    recommendations = {
        "New York": [
            "Joe's Pizza - Famous for its classic New York-style pizza.",
            "Le Bernardin - A high-end seafood restaurant with exquisite dishes.",
            "Katz's Delicatessen - Iconic spot for pastrami sandwiches."
        ],
        "San Francisco": [
            "Tartine Bakery - Renowned for its artisanal bread and pastries.",
            "Zuni Café - Known for its wood-fired dishes and cozy atmosphere.",
            "The Slanted Door - Modern Vietnamese cuisine with a view of the bay."
        ],
        "Chicago": [
            "Alinea - A three-Michelin-star restaurant offering innovative cuisine.",
            "Giordano's - Famous for its deep-dish pizza.",
            "Portillo's - A must-visit for Chicago-style hot dogs and Italian beef sandwiches."
        ],
        "Goa": [
            "Vinayak Family Restaurant - Known for authentic Goan seafood.",
            "Martin's Corner - A popular spot for local dishes and vibrant atmosphere.",
            "Fisherman's Wharf - Offers a great view along with delicious seafood."
        ]
    }
    
    if place in recommendations:
        return recommendations[place]
    else:
        return [f"Sorry, we don't have restaurant recommendations for {place} at the moment."]
    
def restaurant_guide_bot(query: str) -> str:
    agent = CodeAgent(tools=[get_restaurant_recommendations], model=InferenceClientModel(api_key=HF_API_KEY))

    query = (
        "you are a restaurant guide bot. A user will provide you with a location to find restaurant recommendations."
        "Provide restaurant recommendations based on the provided location."
        "if the get_restaurant_recommendations tool didnt give the specific recommendations, don't try to improvise and give your own suggestions."
        "answer in str format such that a agentic ai can understand."
        "the user query is: " + query
    )
    response = agent.run(query)
    return response

