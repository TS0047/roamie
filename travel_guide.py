from smolagents import InferenceClientModel, CodeAgent,tool
import os

HF_API_KEY = os.getenv("HF_API_KEY")
@tool
def get_travel_recommendations(destination: str, interests: str) -> str:
    """
    Provides travel recommendations based on the destination and interests.
    
    Args:
        destination (str): The travel destination.
        interests (str): The traveler's interests (e.g., history, food, adventure).
        
    Returns:
        str: A list of recommended activities and places to visit.
    """

    recommendations = {
        "Paris": {
            "history": "Visit the Louvre Museum and Notre-Dame Cathedral.",
            "food": "Try local delicacies at Le Marais district.",
            "adventure": "Take a hot air balloon ride over the city."
        },
        "Tokyo": {
            "history": "Explore the historic Asakusa district and Senso-ji Temple.",
            "food": "Enjoy sushi at Tsukiji Fish Market.",
            "adventure": "Experience the bustling Shibuya Crossing."
        },
        "Goa": {
            "history": "Explore the colonial architecture in Old Goa.",
            "food": "Try local seafood dishes at a beachside restaurant.",
            "adventure": "Go paragliding over the scenic coastline.",
        }
    }
    
    if destination in recommendations:
        recs = recommendations[destination].get(interests.lower(), "No specific recommendations available.")
        return f"Recommendations for {destination} based on your interest in {interests}: {recs}"
    else:
        return f"Sorry, we don't have recommendations for {destination} at the moment."
    
def travel_guide_bot(query: str) -> str:
    agent = CodeAgent(tools=[get_travel_recommendations], model=InferenceClientModel(api_key=HF_API_KEY))

    query = (
                "you are a travel guide bot. A user will provide you with a travel query and their interests."
                "Provide travel recommendations based on the provided information."
                "if the get_travel_recommendations tool didnt give the specific recommendations, don't try to improvise and give your own suggestions."
                "answer in str format such that a agentic ai can understand."
                "the user query is: " + query
            )
    
    response = agent.run(query)
    return response
