import streamlit as st
import re
from typing import TypedDict, List
from langchain_core.messages import HumanMessage, AIMessage
from langchain_core.prompts import ChatPromptTemplate
from langchain_groq import ChatGroq

class PlannerState(TypedDict):
    messages: List[HumanMessage | AIMessage]
    city: str
    budget: str
    currency: str
    duration: int
    purpose: str
    preferences: str
    dietary_preferences: str
    specific_interests: str
    mobility_concerns: str
    accommodation_preferences: str
    additional_input: str
    itinerary: str

# Define the LLM
llm = ChatGroq(
    temperature=0,
    groq_api_key="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",  # API key unchanged
    model_name="llama-3.3-70b-versatile"
)

# Define the itinerary prompt
itinerary_prompt = ChatPromptTemplate.from_messages([
    ("system",
     "You are a helpful travel assistant. Using the provided information, generate:\n"
     "1. Top-rated attractions and activities at the destination.\n"
     "2. Suggestions aligned with user preferences (e.g., 'Hidden Gems').\n"
     "3. A well-structured itinerary with timing and grouping of activities for each day.\n\n"
     "Use the following inputs (some might be missing):\n"
     "City: {city}, Budget: {budget} {currency}, Duration: {duration} days, Purpose: {purpose}, "
     "Preferences: {preferences}, Dietary Preferences: {dietary_preferences}, Specific Interests: {specific_interests}, "
     "Mobility Concerns: {mobility_concerns}, Accommodation Preferences: {accommodation_preferences}, "
     "Additional Input: {additional_input}."
    ),
    ("human", "Create a detailed itinerary for my trip."),
])

# Helper Functions
def parse_budget(budget: str) -> str:
    """Convert budget from flexible phrases like 'moderate' into a range."""
    budget_lower = budget.lower()
    if "low" in budget_lower or "tight" in budget_lower:
        return "low"
    elif "moderate" in budget_lower:
        return "moderate"
    elif "high" in budget_lower or "luxury" in budget_lower:
        return "high"
    return "moderate"  # Default to moderate if unspecified

def process_optional_inputs(state: PlannerState) -> PlannerState:
    """Fill in default values for optional inputs."""
    state["budget"] = parse_budget(state["budget"]) if state["budget"] else "moderate"
    state["currency"] = state["currency"] if state["currency"] else "USD"
    state["duration"] = state["duration"] if state["duration"] > 0 else 3  # Default to 3 days
    state["purpose"] = state["purpose"] if state["purpose"] else "Leisure"
    state["preferences"] = state["preferences"] if state["preferences"] else "general sightseeing"
    state["dietary_preferences"] = state["dietary_preferences"] or "none"
    state["specific_interests"] = state["specific_interests"] or "none"
    state["mobility_concerns"] = state["mobility_concerns"] or "none"
    state["accommodation_preferences"] = state["accommodation_preferences"] or "standard"
    state["additional_input"] = state["additional_input"] or "none"
    return state

def create_itinerary(state: PlannerState) -> str:
    """Generate a detailed itinerary."""
    response = llm.invoke(
        itinerary_prompt.format_messages(
            city=state['city'],
            budget=state['budget'],
            currency=state['currency'],
            duration=state['duration'],
            purpose=state['purpose'],
            preferences=state['preferences'],
            dietary_preferences=state['dietary_preferences'],
            specific_interests=state['specific_interests'],
            mobility_concerns=state['mobility_concerns'],
            accommodation_preferences=state['accommodation_preferences'],
            additional_input=state['additional_input']
        )
    )
    state["itinerary"] = response.content
    state["messages"] += [AIMessage(content=response.content)]
    return response.content

# Streamlit Application
def main():
    st.title("AI-Powered Travel Planner")
    st.write("Fill in the details below to get a personalized trip itinerary. All inputs are optional.")

    # Initialize state
    if "state" not in st.session_state:
        st.session_state.state = {
            "messages": [],
            "city": "",
            "budget": "",
            "currency": "USD",
            "duration": 0,
            "purpose": "",
            "preferences": "",
            "dietary_preferences": "",
            "specific_interests": "",
            "mobility_concerns": "",
            "accommodation_preferences": "",
            "additional_input": "",
            "itinerary": "",
        }

    # User Inputs (Optional)
    city = st.text_input("Enter your destination city (optional)", placeholder="e.g., Paris")
    budget = st.text_input("Enter your budget (optional, e.g., low, moderate, high)", placeholder="e.g., moderate")
    currency = st.selectbox("Select your currency (optional)", ["USD", "EUR", "GBP", "INR", "JPY", "AUD", "CAD"], index=0)
    duration = st.number_input("Enter the trip duration (in days, optional)", min_value=0, step=1, value=0)
    purpose = st.selectbox("Select the purpose of your trip (optional)", ["", "Leisure", "Adventure", "Business", "Romantic", "Family"])
    preferences = st.text_input("Describe your preferences (optional)", placeholder="e.g., museums, famous places, local food, adventure")
    dietary_preferences = st.text_input("Do you have any dietary preferences? (optional)", placeholder="e.g., vegetarian, vegan, halal")
    specific_interests = st.text_area("What are your specific interests? (optional)", placeholder="e.g., art galleries, nature trails, shopping")
    mobility_concerns = st.text_input("Do you have any walking tolerance or mobility concerns? (optional)", placeholder="e.g., none, limited walking")
    accommodation_preferences = st.text_input("What type of accommodation do you prefer? (optional)", placeholder="e.g., luxury, budget, central location")
    additional_input = st.text_area("Optional: Provide additional details", placeholder="e.g., I want a mix of famous and offbeat places.")

    # Generate itinerary button
    if st.button("Generate Itinerary"):
        # Update state with user inputs
        st.session_state.state.update({
            "city": city,
            "budget": budget,
            "currency": currency,
            "duration": duration,
            "purpose": purpose,
            "preferences": preferences,
            "dietary_preferences": dietary_preferences,
            "specific_interests": specific_interests,
            "mobility_concerns": mobility_concerns,
            "accommodation_preferences": accommodation_preferences,
            "additional_input": additional_input,
        })

        # Process optional inputs
        st.session_state.state = process_optional_inputs(st.session_state.state)

        # Generate itinerary
        itinerary = create_itinerary(st.session_state.state)

        # Display the generated itinerary
        st.subheader("Your Personalized Itinerary")
        st.markdown(itinerary)

if __name__ == "__main__":
    main()
