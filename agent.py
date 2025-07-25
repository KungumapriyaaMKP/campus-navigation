import os
import re
import json
# Import necessary classes and modules from the installed libraries
from lyzr import VoiceBot # <-- CHANGED ChatBot to VoiceBot
import elevenlabs
from deepgram import DeepgramClient

# --- Configuration ---
# IMPORTANT: Replace these placeholder API Keys with your actual keys.
# You can find these on your respective Lyzr, Deepgram, and ElevenLabs dashboards.
LYZR_API_KEY =   # Your Lyzr API Key
DEEPGRAM_API_KEY =   # Your Deepgram API Key
ELEVENLABS_API_KEY = #elevenlabs key


# Set ElevenLabs API key as an environment variable, which the 'generate' function uses.
# The elevenlabs library automatically picks this up for authentication.
os.environ["ELEVEN_LABS_API_KEY"] = ELEVENLABS_API_KEY

# --- Campus Map Data (Your Knowledge Base for Pathfinding) ---
# This dictionary represents your campus as a graph, where keys are locations
# and values are lists of directly connected locations.
# Ensure these keys are consistent with what your normalize_location_name function expects.
campus_map = {
  "F1_MainGate": ["F1_MainBlock", "F1_Parking", "F1_SECECircle"],
  "F1_MainBlock": ["F1_MainGate", "F1_IGNITE_Entrance", "F1_ITCentre_Entrance", "F1_Library_Entrance", "F1_CentralAtrium", "F1_Stairs_to_F2", "F1_Elevator_to_F2"],
  "F1_IGNITE_Entrance": ["F1_MainBlock", "F2_IGNITE"],
  "F1_ITCentre_Entrance": ["F1_MainBlock", "F2_ITCentre"],
  "F1_Library_Entrance": ["F1_MainBlock", "F3_Library"],
  "F1_Auditorium_FirstFloor": ["F1_Reception", "F3_Auditorium_SecondFloor", "F1_GDHall"],
  "F1_Reception": ["F1_MainBlock", "F1_Auditorium_FirstFloor", "F1_Cafeteria"],
  "F1_Cafeteria": ["F1_Reception"],
  "F1_Parking": ["F1_MainGate", "F1_MedicalCentre"],
  "F1_MedicalCentre": ["F1_Parking"],
  "F1_NCC_NSS_Block": ["F1_SECECircle"],
  "F1_Temple": ["F1_SECECircle"],
  "F1_SECECircle": ["F1_MainGate", "F1_NCC_NSS_Block", "F1_Temple", "F1_OpenAirTheatre"],
  "F1_OpenAirTheatre": ["F1_SECECircle", "F1_CentralAtrium"],
  "F1_CentralAtrium": ["F1_MainBlock", "F1_OpenAirTheatre", "F1_AmenityCentre"],
  "F1_AmenityCentre": ["F1_CentralAtrium", "F2_AmenityFirstFloor", "F1_BoysParlour", "F1_GirlsParlour"],
  "F1_BoysParlour": ["F1_AmenityCentre"],
  "F1_GirlsParlour": ["F1_AmenityCentre"],
  "F1_GDHall": ["F1_Auditorium_FirstFloor", "F3_GuestDining", "F3_InterviewRoom"],

  "F2_IGNITE": ["F1_IGNITE_Entrance", "F2_CoworkingSpaces", "F2_Makerspace"],
  "F2_CoworkingSpaces": ["F2_IGNITE"],
  "F2_Makerspace": ["F2_IGNITE", "F2_RapidPrototype"],
  "F2_ITCentre": ["F1_ITCentre_Entrance", "F2_ITAuditorium", "F2_SmartClassRoom", "F2_CODEStudio", "F2_DataScience", "F2_Informatica", "F2_Stairs_to_F3", "F2_Elevator_to_F3"],
  "F2_ITAuditorium": ["F2_ITCentre"],
  "F2_SmartClassRoom": ["F2_ITCentre"],
  "F2_RapidPrototype": ["F2_Makerspace", "F2_Robotics"],
  "F2_Robotics": ["F2_RapidPrototype", "F2_AI_DS_Block"],
  "F2_AI_DS_Block": ["F2_Robotics", "F2_CCEDept", "F2_AI_MachineLearning"],
  "F2_CCEDept": ["F2_AI_DS_Block"],
  "F2_MechanicalBlock": ["F2_ThermalCuttingLab", "F2_EEELab"],
  "F2_ThermalCuttingLab": ["F2_MechanicalBlock"],
  "F2_EEELab": ["F2_MechanicalBlock"],
  "F2_CODEStudio": ["F2_ITCentre", "F2_FullStackJava"],
  "F2_DataScience": ["F2_ITCentre"],
  "F2_Informatica": ["F2_ITCentre"],
  "F2_AI_MachineLearning": ["F2_AI_DS_Block"],
  "F2_FullStackJava": ["F2_CODEStudio"],
  "F2_AdvancedIOT": ["F2_IOTLab"],
  "F2_CloudLab": ["F2_IOTLab"],
  "F2_IOTLab": ["F2_AdvancedIOT", "F2_CloudLab"],
  "F2_AmenityFirstFloor": ["F1_AmenityCentre"],

  "F3_Library": ["F1_Library_Entrance", "F3_Dean_Office"],
  "F3_Auditorium_SecondFloor": ["F1_Auditorium_FirstFloor"],
  "F3_GuestDining": ["F1_GDHall"],
  "F3_InterviewRoom": ["F1_GDHall", "F3_GuestSuites"],
  "F3_GuestSuites": ["F3_InterviewRoom"],
  "F3_Dean_Office": ["F3_Library"],

  "F1_Stairs_to_F2": ["F1_MainBlock", "F2_Stairs_to_F1"],
  "F2_Stairs_to_F1": ["F1_Stairs_to_F2", "F2_ITCentre"],
  "F2_Stairs_to_F3": ["F2_ITCentre", "F3_Stairs_to_F2"],
  "F3_Stairs_to_F2": ["F2_Stairs_to_F3", "F3_Library"],

  "F1_Elevator_to_F2": ["F1_MainBlock", "F2_Elevator_to_F1"],
  "F2_Elevator_to_F1": ["F1_Elevator_to_F2", "F2_ITCentre"],
  "F2_Elevator_to_F3": ["F2_ITCentre", "F3_Elevator_to_F2"],
  "F3_Elevator_to_F2": ["F2_Elevator_to_F3", "F3_Library"],

  "F1_BoysHostel": ["F1_OutdoorGames", "F1_IndoorGames"],
  "F1_GirlsHostel": ["F1_OutdoorGames", "F1_IndoorGames"],
  "F1_OutdoorGames": ["F1_BoysHostel", "F1_GirlsHostel", "F1_FitnessCentre"],
  "F1_IndoorGames": ["F1_BoysHostel", "F1_GirlsHostel", "F1_FitnessCentre"],
  "F1_FitnessCentre": ["F1_OutdoorGames", "F1_IndoorGames", "F1_MusicStudio"],
  "F1_MusicStudio": ["F1_FitnessCentre"]
}

# --- Pathfinding and Formatting Functions ---

def bfs_path(start, end, graph):
    """
    Performs a Breadth-First Search to find the shortest path between two nodes in a graph.
    Args:
        start (str): The starting node.
        end (str): The destination node.
        graph (dict): The graph represented as an adjacency list.
    Returns:
        list: The path as a list of nodes, or None if no path is found.
    """
    if start not in graph or end not in graph:
        return None

    queue = [[start]]
    visited = {start}

    while queue:
        path = queue.pop(0)
        last_node = path[-1]

        if last_node == end:
            return path

        for neighbor in graph.get(last_node, []):
            if neighbor not in visited:
                visited.add(neighbor)
                queue.append(path + [neighbor])
    return None

def get_floor(location):
    """
    Extracts the floor number from a location key (e.g., 'F1_MainBlock' -> 1).
    Args:
        location (str): The location key.
    Returns:
        int: The floor number, or None if not found.
    """
    match = re.match(r"F(\d+)_", location)
    return int(match.group(1)) if match else None

def format_directions(path):
    """
    Formats a list of path nodes into human-readable, step-by-step directions.
    Args:
        path (list): The list of nodes representing the path.
    Returns:
        str: Formatted directions.
    """
    if not path or len(path) < 2:
        return "No clear path found or you are already there."

    directions = []
    for i in range(len(path) - 1):
        current = path[i]
        next_loc = path[i + 1]

        current_floor = get_floor(current)
        next_floor = get_floor(next_loc)

        # Clean up names for display (e.g., 'F1_MainBlock' -> 'Main Block')
        current_display_name = current.replace(f"F{current_floor}_", '').replace('_', ' ') if current_floor else current.replace('_', ' ')
        next_display_name = next_loc.replace(f"F{next_floor}_", '').replace('_', ' ') if next_floor else next_loc.replace('_', ' ')

        instruction_prefix = f"From Floor {current_floor} {current_display_name}" if current_floor else f"From {current_display_name}"

        if current_floor is not None and next_floor is not None and current_floor != next_floor:
            # Handle floor changes explicitly (stairs or elevator)
            if "Stairs_to_F" in next_loc:
                instruction = f"{instruction_prefix}, take the stairs to Floor {next_floor}."
            elif "Elevator_to_F" in next_loc:
                instruction = f"{instruction_prefix}, take the elevator to Floor {next_floor}."
            else:
                # Fallback for unexpected floor changes without explicit stairs/elevators nodes
                instruction = f"{instruction_prefix}, proceed towards Floor {next_floor} {next_display_name}."
        else:
            # Movement within the same floor or general progression
            instruction = f"{instruction_prefix}, proceed towards {next_display_name}."
        directions.append(instruction)

    # Add the final arrival statement
    final_destination_floor = get_floor(path[-1])
    final_destination_name = path[-1].replace(f"F{final_destination_floor}_", '').replace('_', ' ') if final_destination_floor else path[-1].replace('_', ' ')
    directions.append(f"You have arrived at Floor {final_destination_floor} {final_destination_name}.")
    return "\n".join(directions)

def normalize_location_name(name):
    """
    Normalizes user input location names to match the keys in campus_map.
    This function is crucial for mapping natural language input to your map keys.
    Args:
        name (str): The user-provided location name (e.g., "Floor 1 Main Gate").
    Returns:
        str: The corresponding key from campus_map (e.g., "F1_MainGate"), or None if no match.
    """
    # Convert to lowercase and replace non-alphanumeric characters with underscores
    # and remove leading/trailing/multiple underscores
    cleaned_name = re.sub(r'[^a-z0-9]+', '_', name.lower()).strip('_')

    # Try to handle "floor X" prefix in user input (e.g., "floor 1 main gate" -> "f1_main_gate")
    match_floor_prefix = re.match(r"f(\d+)_(.*)", cleaned_name)
    if match_floor_prefix:
        floor_num = match_floor_prefix.group(1)
        base_name = match_floor_prefix.group(2)
        # Construct the expected key format (e.g., F1_Main_Gate)
        # Using .title().replace('_', '') for cases like "main gate" -> "MainGate"
        potential_key_with_floor = f"F{floor_num}_{base_name.replace(' ', '_').title().replace('_', '')}"
        # Try to find an exact match for the constructed key
        if potential_key_with_floor in campus_map:
            return potential_key_with_floor
        # Also try with original base name if title casing is not consistent (e.g. F1_main_gate)
        potential_key_with_floor_alt = f"F{floor_num}_{base_name.replace(' ', '_')}"
        if potential_key_with_floor_alt in campus_map:
            return potential_key_with_floor_alt


    # If no explicit floor prefix, or if the above didn't match, try other matching strategies
    best_match = None
    max_score = 0 # To track how good a match is

    for key in campus_map:
        key_lower = key.lower()
        # Remove floor prefix from map key for comparison (e.g., "f1_main_gate" -> "main_gate")
        key_no_floor_prefix = re.sub(r"^f\d+_", "", key_lower)

        # 1. Exact match of cleaned user input with the map key (without floor prefix)
        if cleaned_name == key_no_floor_prefix:
            # If user says "main gate" and map has "F1_MainGate", this is a strong candidate.
            # This might pick the first one found if multiple floors have the same named area.
            return key

        # 2. Substring match (more flexible, but can be less precise)
        if cleaned_name in key_lower:
            # Calculate a score based on length of match relative to key length
            score = len(cleaned_name) / len(key_lower)
            if score > max_score:
                max_score = score
                best_match = key

    if best_match:
        return best_match

    # 3. Final attempt: direct match if user input is already in FX_ format (e.g., "F1_MAINGATE")
    if cleaned_name.upper() in campus_map:
        return cleaned_name.upper()

    return None # No match found

# --- Lyzr Agent Setup ---

# Initialize the Lyzr Agent with its role, goal, and instructions.
# The LyzrAgent here primarily acts as the orchestrator and conversational layer.
# Removing role, goal, instructions as they are not accepted in this version of ChatBot
# Try initializing VoiceBot with api_key
campus_agent = VoiceBot(api_key=LYZR_API_KEY)

# --- Main Interaction Loop ---
def run_campus_navigator():
    print("Hello! I am your campus navigation assistant. Please tell me your current location and your destination.")
    print("For example: 'How do I get from Floor 1 Main Block to Floor 3 Library?'")
    print("Type 'exit', 'quit', or 'bye' to end the conversation.")

    # Initialize Deepgram client for Speech-to-Text
    # The DeepgramClient expects the API key during initialization.
    deepgram_client = DeepgramClient(DEEPGRAM_API_KEY)

    while True:
        try:
            # --- Speech Input (Deepgram - Text Input for simplicity in this script) ---
            # In a full voice application, this part would involve capturing live audio
            # and sending it to Deepgram's streaming API for transcription.
            # For this script, we'll use text input to simulate the transcribed speech.
            user_input = input("You: ")
            if user_input.lower() in ['exit', 'quit', 'bye']:
                print("Goodbye!")
                break

            # --- DEBUGGING PRINTS: See what the script extracts and normalizes ---
            print(f"DEBUG: User Input: '{user_input}'")

            # Use regex to extract potential locations from user input.
            # This is a simple extraction. For more complex queries, a full LLM parsing
            # (e.g., via Lyzr's agent.process_message) would be more robust.
            match = re.search(r"(?:from\s+)?(.+?)\s+(?:to|towards)\s+(.+)", user_input, re.IGNORECASE)

            raw_current_location = None
            raw_destination = None

            if match:
                raw_current_location = match.group(1).strip()
                raw_destination = match.group(2).strip()
                print(f"DEBUG: Extracted Raw Current Location: '{raw_current_location}'")
                print(f"DEBUG: Extracted Raw Destination: '{raw_destination}'")
            else:
                print("Agent: Please state your query in the format 'From [start] to [end]' or '[start] to [end]'.")
                continue # Ask for input again if format is unclear

            # Normalize locations using our custom function to match campus_map keys
            current_location_key = normalize_location_name(raw_current_location)
            destination_key = normalize_location_name(raw_destination)

            print(f"DEBUG: Normalized Current Location Key: '{current_location_key}'")
            print(f"DEBUG: Normalized Destination Key: '{destination_key}'")

            response_text = ""
            if not current_location_key:
                response_text = f"Sorry, I don't recognize '{raw_current_location}'. Please provide a valid starting point from the campus map."
            elif not destination_key:
                response_text = f"Sorry, I don't recognize '{raw_destination}'. Please provide a valid destination from the campus map."
            else:
                # --- Pathfinding Logic ---
                path = bfs_path(current_location_key, destination_key, campus_map)
                print(f"DEBUG: Path found by BFS: {path}") # See the actual path list

                if path:
                    response_text = format_directions(path)
                else:
                    response_text = f"I couldn't find a path from '{raw_current_location}' to '{raw_destination}'. Please check the names or try a different route."

            print(f"Agent: {response_text}")

            # --- Speech Output (ElevenLabs) ---
            if response_text:
                try:
                    audio = elevenlabs.generate(
                        text=response_text,
                        voice=elevenlabs.Voice(
                            voice_id='EXAVITQu4vr4xnSDxMaL', # Default Adam voice ID. You can change this.
                                                              # Find other voice IDs on ElevenLabs website.
                            settings=elevenlabs.VoiceSettings(stability=0.75, similarity_boost=0.75, style=0.0, use_speaker_boost=True)
                        )
                    )
                    # In Colab, play() might not work directly for all users.
                    # You might need to download the audio or use Colab's Audio widget.
                    # For local script, play() should work.
                    elevenlabs.play(audio)
                except Exception as elevenlabs_e:
                    print(f"ERROR: ElevenLabs voice generation failed: {elevenlabs_e}")
                    print("Please ensure your ElevenLabs API key is correct and you have sufficient credits.")

        except Exception as e:
            print(f"An unexpected error occurred: {e}")
            print("Please try again or refine your query.")

# This ensures the run_campus_navigator() function is called when the script is executed.
if __name__ == '__main__':
    run_campus_navigator()


## ---------------------------------------------------------------------------------------------------------------------------------

import os
import re
import json
# Import necessary classes and modules from the installed libraries
# This is the standard import path for LyzrAgent.
# from lyzr import LyzrAgent # Commented out as per previous decision to bypass LyzrAgent
from deepgram import DeepgramClient
from elevenlabs import Voice, VoiceSettings, play # Removed 'generate' from direct import
from elevenlabs.client import ElevenLabs # ElevenLabs client for API key management

# --- Configuration ---
# IMPORTANT: Your actual API Keys are now filled in based on your previous steps.
LYZR_API_KEY = "sk-default-UVwrao9HeTWXAk5gb3d0cf1VWSZ304Bv"  # Your Lyzr API Key
DEEPGRAM_API_KEY = "7f45437a1cdd0a8d860d1e04f78a3639f77d1"  # Your Deepgram API Key
ELEVENLABS_API_KEY = "sk_8f5482590cd5c2861397ea7932b19ebe23c106f87a241385" # Corrected ElevenLabs API Key

# Set ElevenLabs API key as an environment variable, which the 'generate' function uses.
os.environ["ELEVEN_LABS_API_KEY"] = ELEVENLABS_API_KEY

# Initialize ElevenLabs client with the API key
elevenlabs_client = ElevenLabs(api_key=ELEVENLABS_API_KEY)


# --- Campus Map Data (Your Knowledge Base for Pathfinding) ---
campus_map = {
  "F1_MainGate": ["F1_MainBlock", "F1_Parking", "F1_SECECircle"],
  "F1_MainBlock": ["F1_MainGate", "F1_IGNITE_Entrance", "F1_ITCentre_Entrance", "F1_Library_Entrance", "F1_CentralAtrium", "F1_Stairs_to_F2", "F1_Elevator_to_F2"],
  "F1_IGNITE_Entrance": ["F1_MainBlock", "F2_IGNITE"],
  "F1_ITCentre_Entrance": ["F1_MainBlock", "F2_ITCentre"],
  "F1_Library_Entrance": ["F1_MainBlock", "F3_Library"],
  "F1_Auditorium_FirstFloor": ["F1_Reception", "F3_Auditorium_SecondFloor", "F1_GDHall"],
  "F1_Reception": ["F1_MainBlock", "F1_Auditorium_FirstFloor", "F1_Cafeteria"],
  "F1_Cafeteria": ["F1_Reception"],
  "F1_Parking": ["F1_MainGate", "F1_MedicalCentre"],
  "F1_MedicalCentre": ["F1_Parking"],
  "F1_NCC_NSS_Block": ["F1_SECECircle"],
  "F1_Temple": ["F1_SECECircle"],
  "F1_SECECircle": ["F1_MainGate", "F1_NCC_NSS_Block", "F1_Temple", "F1_OpenAirTheatre"],
  "F1_OpenAirTheatre": ["F1_SECECircle", "F1_CentralAtrium"],
  "F1_CentralAtrium": ["F1_MainBlock", "F1_OpenAirTheatre", "F1_AmenityCentre"],
  "F1_AmenityCentre": ["F1_CentralAtrium", "F2_AmenityFirstFloor", "F1_BoysParlour", "F1_GirlsParlour"],
  "F1_BoysParlour": ["F1_AmenityCentre"],
  "F1_GirlsParlour": ["F1_AmenityCentre"],
  "F1_GDHall": ["F1_Auditorium_FirstFloor", "F3_GuestDining", "F3_InterviewRoom"],

  "F2_IGNITE": ["F1_IGNITE_Entrance", "F2_CoworkingSpaces", "F2_Makerspace"],
  "F2_CoworkingSpaces": ["F2_IGNITE"],
  "F2_Makerspace": ["F2_IGNITE", "F2_RapidPrototype"],
  "F2_ITCentre": ["F1_ITCentre_Entrance", "F2_ITAuditorium", "F2_SmartClassRoom", "F2_CODEStudio", "F2_DataScience", "F2_Informatica", "F2_Stairs_to_F3", "F2_Elevator_to_F3"],
  "F2_ITAuditorium": ["F2_ITCentre"],
  "F2_SmartClassRoom": ["F2_ITCentre"],
  "F2_RapidPrototype": ["F2_Makerspace", "F2_Robotics"],
  "F2_Robotics": ["F2_RapidPrototype", "F2_AI_DS_Block"],
  "F2_AI_DS_Block": ["F2_Robotics", "F2_CCEDept", "F2_AI_MachineLearning"],
  "F2_CCEDept": ["F2_AI_DS_Block"],
  "F2_MechanicalBlock": ["F2_ThermalCuttingLab", "F2_EEELab"],
  "F2_ThermalCuttingLab": ["F2_MechanicalBlock"],
  "F2_EEELab": ["F2_MechanicalBlock"],
  "F2_CODEStudio": ["F2_ITCentre", "F2_FullStackJava"],
  "F2_DataScience": ["F2_ITCentre"],
  "F2_Informatica": ["F2_ITCentre"],
  "F2_AI_MachineLearning": ["F2_AI_DS_Block"],
  "F2_FullStackJava": ["F2_CODEStudio"],
  "F2_AdvancedIOT": ["F2_IOTLab"],
  "F2_CloudLab": ["F2_IOTLab"],
  "F2_IOTLab": ["F2_AdvancedIOT", "F2_CloudLab"],
  "F2_AmenityFirstFloor": ["F1_AmenityCentre"],

  "F3_Library": ["F1_Library_Entrance", "F3_Dean_Office"],
  "F3_Auditorium_SecondFloor": ["F1_Auditorium_FirstFloor"],
  "F3_GuestDining": ["F1_GDHall"],
  "F3_InterviewRoom": ["F1_GDHall", "F3_GuestSuites"],
  "F3_GuestSuites": ["F3_InterviewRoom"],
  "F3_Dean_Office": ["F3_Library"],

  "F1_Stairs_to_F2": ["F1_MainBlock", "F2_Stairs_to_F1"],
  "F2_Stairs_to_F1": ["F1_Stairs_to_F2", "F2_ITCentre"],
  "F2_Stairs_to_F3": ["F2_ITCentre", "F3_Stairs_to_F2"],
  "F3_Stairs_to_F2": ["F2_Stairs_to_F3", "F3_Library"],

  "F1_Elevator_to_F2": ["F1_MainBlock", "F2_Elevator_to_F1"],
  "F2_Elevator_to_F1": ["F1_Elevator_to_F2", "F2_ITCentre"],
  "F2_Elevator_to_F3": ["F2_ITCentre", "F3_Elevator_to_F2"],
  "F3_Elevator_to_F2": ["F2_Elevator_to_F3", "F3_Library"],

  "F1_BoysHostel": ["F1_OutdoorGames", "F1_IndoorGames"],
  "F1_GirlsHostel": ["F1_OutdoorGames", "F1_IndoorGames"],
  "F1_OutdoorGames": ["F1_BoysHostel", "F1_GirlsHostel", "F1_FitnessCentre"],
  "F1_IndoorGames": ["F1_BoysHostel", "F1_GirlsHostel", "F1_FitnessCentre"],
  "F1_FitnessCentre": ["F1_OutdoorGames", "F1_IndoorGames", "F1_MusicStudio"],
  "F1_MusicStudio": ["F1_FitnessCentre"]
}

# --- New Feature: Location Information ---
# Dictionary to store descriptive information about locations
# Each location now contains a dictionary with 'description', 'type', and 'accessibility'
location_info = {
    "F1_MainGate": {
        "description": "The main entrance to Sri Eshwar College of Engineering, serving as the primary access point to the campus.",
        "type": "entrance",
        "accessibility": "Wheelchair accessible, ramp available."
    },
    "F1_MainBlock": {
        "description": "The central administrative and academic block on the first floor, housing various departments and offices.",
        "type": "academic building",
        "accessibility": "Elevator access to all floors, wheelchair accessible."
    },
    "F1_IGNITE_Entrance": {
        "description": "The entrance to the IGNITE incubation center, fostering innovation and entrepreneurship.",
        "type": "innovation center",
        "accessibility": "Wheelchair accessible."
    },
    "F1_ITCentre_Entrance": {
        "description": "The entrance to the Information Technology Centre, equipped with computer labs and IT facilities.",
        "type": "department entrance",
        "accessibility": "Wheelchair accessible."
    },
    "F1_Library_Entrance": {
        "description": "The entrance to the main library, a hub for academic resources and study.",
        "type": "library entrance",
        "accessibility": "Wheelchair accessible."
    },
    "F1_Auditorium_FirstFloor": {
        "description": "The first floor of the main auditorium, used for large gatherings, events, and presentations.",
        "type": "auditorium",
        "accessibility": "Wheelchair accessible seating, ramp access."
    },
    "F1_Reception": {
        "description": "The main reception area, where visitors are greeted and directed.",
        "type": "administrative",
        "accessibility": "Wheelchair accessible."
    },
    "F1_Cafeteria": {
        "description": "The campus cafeteria, offering a variety of food and beverages for students and staff.",
        "type": "dining",
        "accessibility": "Wheelchair accessible, spacious seating."
    },
    "F2_IGNITE": {
        "description": "The IGNITE incubation center on the second floor, providing resources and mentorship for startups.",
        "type": "innovation center",
        "accessibility": "Accessible via elevator from F1, wheelchair accessible."
    },
    "F2_ITCentre": {
        "description": "The Information Technology Centre on the second floor, a key facility for computer science and IT students.",
        "type": "department",
        "accessibility": "Accessible via elevator from F1, wheelchair accessible labs."
    },
    "F3_Library": {
        "description": "The main library on the third floor, providing extensive collections and study spaces.",
        "type": "library",
        "accessibility": "Accessible via elevator from F1/F2, wheelchair accessible."
    },
    "F3_Dean_Office": {
        "description": "The office of the Dean on the third floor, handling academic and administrative affairs.",
        "type": "administrative",
        "accessibility": "Accessible via elevator from F1/F2, wheelchair accessible."
    },
    "F1_Parking": {
        "description": "The designated parking area for vehicles, accessible from the Main Gate.",
        "type": "parking",
        "accessibility": "Designated accessible parking spaces available."
    },
    "F1_MedicalCentre": {
        "description": "The campus medical center, providing first aid and basic healthcare services.",
        "type": "medical",
        "accessibility": "Wheelchair accessible entrance."
    },
    "F1_NCC_NSS_Block": {
        "description": "The block housing the National Cadet Corps (NCC) and National Service Scheme (NSS) offices.",
        "type": "administrative",
        "accessibility": "Ground floor access, generally accessible."
    },
    "F1_Temple": {
        "description": "The campus temple, a place for spiritual activities and quiet reflection.",
        "type": "religious",
        "accessibility": "Ramp access available."
    },
    "F1_SECECircle": {
        "description": "A central roundabout on the first floor, connecting various blocks and areas.",
        "type": "landmark",
        "accessibility": "Open area, generally accessible."
    },
    "F1_OpenAirTheatre": {
        "description": "An outdoor theatre space used for cultural events and student performances.",
        "type": "event space",
        "accessibility": "Ground level access, some seating areas may have steps."
    },
    "F1_CentralAtrium": {
        "description": "A large open area in the center of the main block, often used for informal gatherings.",
        "type": "common area",
        "accessibility": "Wheelchair accessible."
    },
    "F1_AmenityCentre": {
        "description": "A multi-purpose amenity center offering various facilities for students.",
        "type": "amenity",
        "accessibility": "Wheelchair accessible, elevator access to upper floors."
    },
    "F1_BoysParlour": {
        "description": "A common area for male students within the amenity center.",
        "type": "amenity",
        "accessibility": "Wheelchair accessible."
    },
    "F1_GirlsParlour": {
        "description": "A common area for female students within the amenity center.",
        "type": "amenity",
        "accessibility": "Wheelchair accessible."
    },
    "F1_GDHall": {
        "description": "The Ground Dining Hall, typically used for large-scale dining events.",
        "type": "dining",
        "accessibility": "Wheelchair accessible."
    },
    "F2_CoworkingSpaces": {
        "description": "Shared workspaces within the IGNITE center, designed for collaborative projects.",
        "type": "workspace",
        "accessibility": "Accessible via elevator, spacious."
    },
    "F2_Makerspace": {
        "description": "A facility within IGNITE for hands-on creation and prototyping.",
        "type": "lab",
        "accessibility": "Accessible via elevator, some equipment may require assistance."
    },
    "F2_RapidPrototype": {
        "description": "A lab dedicated to rapid prototyping, often associated with the Makerspace.",
        "type": "lab",
        "accessibility": "Accessible via elevator."
    },
    "F2_Robotics": {
        "description": "The robotics lab, where students work on robotic projects and research.",
        "type": "lab",
        "accessibility": "Accessible via elevator."
    },
    "F2_AI_DS_Block": {
        "description": "The block dedicated to Artificial Intelligence and Data Science departments.",
        "type": "department block",
        "accessibility": "Accessible via elevator."
    },
    "F2_CCEDept": {
        "description": "The Computer Science and Engineering department office.",
        "type": "department",
        "accessibility": "Accessible via elevator."
    },
    "F2_MechanicalBlock": {
        "description": "The block housing various mechanical engineering labs.",
        "type": "department block",
        "accessibility": "Accessible via elevator."
    },
    "F2_ThermalCuttingLab": {
        "description": "A lab within the Mechanical Block for thermal cutting experiments.",
        "type": "lab",
        "accessibility": "Accessible via elevator, specific lab equipment may vary."
    },
    "F2_EEELab": {
        "description": "The Electrical and Electronics Engineering lab.",
        "type": "lab",
        "accessibility": "Accessible via elevator."
    },
    "F2_CODEStudio": {
        "description": "A specialized studio for coding and software development.",
        "type": "lab",
        "accessibility": "Accessible via elevator."
    },
    "F2_DataScience": {
        "description": "A lab or classroom focused on Data Science studies.",
        "type": "lab",
        "accessibility": "Accessible via elevator."
    },
    "F2_Informatica": {
        "description": "A lab or classroom for Informatica-related studies.",
        "type": "lab",
        "accessibility": "Accessible via elevator."
    },
    "F2_AI_MachineLearning": {
        "description": "A lab or classroom focused on AI and Machine Learning.",
        "type": "lab",
        "accessibility": "Accessible via elevator."
    },
    "F2_AdvancedIOT": {
        "description": "A lab for advanced Internet of Things (IoT) research and projects.",
        "type": "lab",
        "accessibility": "Accessible via elevator."
    },
    "F2_CloudLab": {
        "description": "A lab dedicated to cloud computing studies and experiments.",
        "type": "lab",
        "accessibility": "Accessible via elevator."
    },
    "F2_IOTLab": {
        "description": "The Internet of Things (IoT) lab.",
        "type": "lab",
        "accessibility": "Accessible via elevator."
    },
    "F2_AmenityFirstFloor": {
        "description": "The first floor of the amenity center.",
        "type": "amenity",
        "accessibility": "Accessible via elevator."
    },
    "F3_Auditorium_SecondFloor": {
        "description": "The second floor of the main auditorium, providing additional seating or facilities.",
        "type": "auditorium",
        "accessibility": "Accessible via elevator, wheelchair seating available."
    },
    "F3_GuestDining": {
        "description": "A dining area specifically for guests.",
        "type": "dining",
        "accessibility": "Accessible via elevator."
    },
    "F3_InterviewRoom": {
        "description": "Rooms designated for interviews.",
        "type": "office",
        "accessibility": "Accessible via elevator."
    },
    "F3_GuestSuites": {
        "description": "Accommodation suites for guests.",
        "type": "accommodation",
        "accessibility": "Accessible via elevator."
    },
    "F1_BoysHostel": {
        "description": "The hostel for male students.",
        "type": "residence",
        "accessibility": "Main entrance is accessible, specific room accessibility may vary."
    },
    "F1_GirlsHostel": {
        "description": "The hostel for female students.",
        "type": "residence",
        "accessibility": "Main entrance is accessible, specific room accessibility may vary."
    },
    "F1_OutdoorGames": {
        "description": "Area for outdoor sports and recreational activities.",
        "type": "recreation",
        "accessibility": "Ground level access, specific facilities may vary."
    },
    "F1_IndoorGames": {
        "description": "Area for indoor sports and recreational activities.",
        "type": "recreation",
        "accessibility": "Ground level access, wheelchair accessible."
    },
    "F1_FitnessCentre": {
        "description": "The campus fitness center or gym.",
        "type": "recreation",
        "accessibility": "Wheelchair accessible entrance, some equipment may be adapted."
    },
    "F1_MusicStudio": {
        "description": "A studio for music practice and production.",
        "type": "recreation",
        "accessibility": "Wheelchair accessible."
    },
    "F1_Stairs_to_F2": {
        "description": "Stairs connecting Floor 1 to Floor 2.",
        "type": "navigation",
        "accessibility": "Not wheelchair accessible. Use nearby elevator for access."
    },
    "F2_Stairs_to_F1": {
        "description": "Stairs connecting Floor 2 to Floor 1.",
        "type": "navigation",
        "accessibility": "Not wheelchair accessible. Use nearby elevator for access."
    },
    "F2_Stairs_to_F3": {
        "description": "Stairs connecting Floor 2 to Floor 3.",
        "type": "navigation",
        "accessibility": "Not wheelchair accessible. Use nearby elevator for access."
    },
    "F3_Stairs_to_F2": {
        "description": "Stairs connecting Floor 3 to Floor 2.",
        "type": "navigation",
        "accessibility": "Not wheelchair accessible. Use nearby elevator for access."
    },
    "F1_Elevator_to_F2": {
        "description": "Elevator connecting Floor 1 to Floor 2.",
        "type": "navigation",
        "accessibility": "Wheelchair accessible elevator."
    },
    "F2_Elevator_to_F1": {
        "description": "Elevator connecting Floor 2 to Floor 1.",
        "type": "navigation",
        "accessibility": "Wheelchair accessible elevator."
    },
    "F2_Elevator_to_F3": {
        "description": "Elevator connecting Floor 2 to Floor 3.",
        "type": "navigation",
        "accessibility": "Wheelchair accessible elevator."
    },
    "F3_Elevator_to_F2": {
        "description": "Elevator connecting Floor 3 to Floor 2.",
        "type": "navigation",
        "accessibility": "Wheelchair accessible elevator."
    }
}


# --- Pathfinding and Formatting Functions ---

def bfs_path(start, end, graph):
    """
    Performs a Breadth-First Search to find the shortest path between two nodes in a graph.
    Args:
        start (str): The starting node.
        end (str): The destination node.
        graph (dict): The graph represented as an adjacency list.
    Returns:
        list: The path as a list of nodes, or None if no path is found.
    """
    if start not in graph or end not in graph:
        return None

    queue = [[start]]
    visited = {start}

    while queue:
        path = queue.pop(0)
        last_node = path[-1]

        if last_node == end:
            return path

        for neighbor in graph.get(last_node, []):
            if neighbor not in visited:
                visited.add(neighbor)
                queue.append(path + [neighbor])
    return None

def get_floor(location):
    """
    Extracts the floor number from a location key (e.g., 'F1_MainBlock' -> 1).
    Args:
        location (str): The location key.
    Returns:
        int: The floor number, or None if not found.
    """
    match = re.match(r"F(\d+)_", location)
    return int(match.group(1)) if match else None

def format_directions(path):
    """
    Formats a list of path nodes into human-readable, step-by-step directions.
    Args:
        path (list): The list of nodes representing the path.
    Returns:
        str: Formatted directions.
    """
    if not path or len(path) < 2:
        return "No clear path found or you are already there."

    directions = []
    for i in range(len(path) - 1):
        current = path[i]
        next_loc = path[i + 1]

        current_floor = get_floor(current)
        next_floor = get_floor(next_loc)

        # Clean up names for display (e.g., 'F1_MainBlock' -> 'Main Block')
        current_display_name = current.replace(f"F{current_floor}_", '').replace('_', ' ') if current_floor else current.replace('_', ' ')
        next_display_name = next_loc.replace(f"F{next_floor}_", '').replace('_', ' ') if next_floor else next_loc.replace('_', ' ')

        instruction_prefix = f"From Floor {current_floor} {current_display_name}" if current_floor else f"From {current_display_name}"

        if current_floor is not None and next_floor is not None and current_floor != next_floor:
            # Handle floor changes explicitly (stairs or elevator)
            if "Stairs_to_F" in next_loc:
                instruction = f"{instruction_prefix}, take the stairs to Floor {next_floor}."
            elif "Elevator_to_F" in next_loc:
                instruction = f"{instruction_prefix}, take the elevator to Floor {next_floor}."
            else:
                # Fallback for unexpected floor changes without explicit stairs/elevator nodes
                instruction = f"{instruction_prefix}, proceed towards Floor {next_floor} {next_display_name}."
        else:
            # Movement within the same floor or general progression
            instruction = f"{instruction_prefix}, proceed towards {next_display_name}."
        directions.append(instruction)

    # Add the final arrival statement
    final_destination_floor = get_floor(path[-1])
    final_destination_name = path[-1].replace(f"F{final_destination_floor}_", '').replace('_', ' ') if final_destination_floor else path[-1].replace('_', ' ')
    directions.append(f"You have arrived at Floor {final_destination_floor} {final_destination_name}.")
    return "\n".join(directions)

def normalize_location_name(name):
    """
    Normalizes user input location names to match the keys in campus_map.
    This function is crucial for mapping natural language input to your map keys.
    Args:
        name (str): The user-provided location name (e.g., "Floor 1 Main Gate").
    Returns:
        str: The corresponding key from campus_map (e.g., "F1_MainGate"), or None if no match.
    """
    # Convert to lowercase and replace non-alphanumeric characters with underscores
    # and remove leading/trailing/multiple underscores
    cleaned_name = re.sub(r'[^a-z0-9]+', '_', name.lower()).strip('_')

    # Specific common phrases to remove/replace for better matching
    cleaned_name = cleaned_name.replace("floor_", "f").replace("im_in_", "").replace("i_am_in_", "").replace("go_to_", "").strip('_')

    # Create a comprehensive set of normalized map keys for robust lookup
    normalized_map_keys_lookup = {}
    for key in campus_map:
        # Add the exact key (e.g., "F1_MainGate")
        normalized_map_keys_lookup[key.lower()] = key
        
        # Add key without floor prefix (e.g., "maingate")
        key_no_floor_prefix = re.sub(r"^f\d+_", "", key.lower())
        normalized_map_keys_lookup[key_no_floor_prefix] = key

        # Add key with underscores (e.g., "f1_main_gate")
        key_with_underscores = key.lower().replace(' ', '_')
        normalized_map_keys_lookup[key_with_underscores] = key

        # Add key without floor prefix and with underscores (e.g., "main_gate")
        key_no_floor_prefix_with_underscores = re.sub(r"^f\d+_", "", key.lower()).replace(' ', '_')
        normalized_map_keys_lookup[key_no_floor_prefix_with_underscores] = key

        # Add common variations like "IT Centre" -> "itcentre"
        display_name = key.replace(f"F{get_floor(key)}_", '').replace('_', ' ').lower() if get_floor(key) else key.replace('_', ' ').lower()
        normalized_map_keys_lookup[display_name.replace(' ', '')] = key # "itcentre" -> "F2_ITCentre"
        normalized_map_keys_lookup[display_name.replace(' ', '_')] = key # "it_centre" -> "F2_ITCentre"
        normalized_map_keys_lookup[display_name] = key # "it centre" -> "F2_ITCentre"


    # First, try to find a direct match with the cleaned user input
    if cleaned_name in normalized_map_keys_lookup:
        return normalized_map_keys_lookup[cleaned_name]
    
    # If not a direct match, try matching parts of the cleaned name
    # This helps with inputs like "main gate" when the key is "MainGate"
    for part in cleaned_name.split('_'):
        if part and part in normalized_map_keys_lookup:
            return normalized_map_keys_lookup[part]
        
    # Fallback to substring matching (less precise but can catch variations)
    best_match = None
    max_score = 0
    for map_key_original, map_key_normalized in normalized_map_keys_lookup.items():
        if cleaned_name in map_key_original:
            score = len(cleaned_name) / len(map_key_original)
            if score > max_score:
                max_score = score
                best_match = map_key_normalized
    
    if best_match:
        return best_match

    return None # No match found

# --- Lyzr Agent Setup ---

# Initialize the Lyzr Agent.
# campus_agent = VoiceBot() # This line is commented out as VoiceBot is not used in this script

# --- Main Interaction Loop ---
def run_campus_navigator():
    print("Hello! I am your campus navigation assistant. Please tell me your current location and your destination.")
    print("For example: 'How do I get from Floor 1 Main Block to Floor 3 Library?'")
    print("You can also ask: 'Tell me about Main Gate' or 'What is the IT Centre?'")
    print("NEW FEATURE: Ask about accessibility! Try: 'Is the Library accessible?' or 'Show me accessible labs.'") # New instruction for accessibility
    print("Type 'exit', 'quit', or 'bye' to end the conversation.")

    # Initialize Deepgram client for Speech-to-Text
    deepgram_client = DeepgramClient(DEEPGRAM_API_KEY)

    while True:
        try:
            # --- Speech Input (Deepgram - Text Input for simplicity in this script) ---
            # In a full voice application, this part would involve capturing live audio
            # and sending it to Deepgram's streaming API for transcription.
            # For this script, we'll use text input to simulate the transcribed speech.
            user_input = input("You: ")
            if user_input.lower() in ['exit', 'quit', 'bye']:
                print("Goodbye!")
                break

            # --- DEBUGGING PRINTS: See what the script extracts and normalizes ---
            print(f"DEBUG: User Input: '{user_input}'")

            # --- Intent Detection: Directions vs. Information vs. Accessibility ---
            raw_current_location = None
            raw_destination = None
            location_info_query = None # To store location if user asks for general info
            accessibility_query_location = None # To store location if user asks for accessibility

            # Check for direction query pattern
            match_direction = re.search(
                r"(?:(?:from|i'm\s+in|i\s+am\s+in)\s+)?(.+?)\s+(?:to|towards|go\s+to)\s+(.+)",
                user_input,
                re.IGNORECASE
            )
            
            # Check for accessibility query pattern (e.g., "Is X accessible?", "Show me accessible Y")
            match_accessibility = re.search(
                r"(?:is\s+(.+?)\s+accessible\??|show\s+me\s+accessible\s+(.+)|what\s+is\s+the\s+accessibility\s+of\s+(.+))",
                user_input,
                re.IGNORECASE
            )

            # Check for general information query pattern (e.g., "Tell me about X", "What is X")
            match_info = re.search(
                r"(?:tell\s+me\s+about|what\s+is|info\s+on)\s+(.+)",
                user_input,
                re.IGNORECASE
            )

            response_text = ""

            if match_direction:
                raw_current_location = match_direction.group(1).strip()
                raw_destination = match_direction.group(2).strip()
                print(f"DEBUG: Detected Direction Query.")
                print(f"DEBUG: Extracted Raw Current Location: '{raw_current_location}'")
                print(f"DEBUG: Extracted Raw Destination: '{raw_destination}'")
                
                # Normalize locations for directions
                current_location_key = normalize_location_name(raw_current_location)
                destination_key = normalize_location_name(raw_destination)

                print(f"DEBUG: Normalized Current Location Key: '{current_location_key}'")
                print(f"DEBUG: Normalized Destination Key: '{destination_key}'")

                if not current_location_key:
                    response_text = f"Sorry, I don't recognize '{raw_current_location}'. Please provide a valid starting point from the campus map."
                elif not destination_key:
                    response_text = f"Sorry, I don't recognize '{raw_destination}'. Please provide a valid destination from the campus map."
                else:
                    # --- Pathfinding Logic ---
                    path = bfs_path(current_location_key, destination_key, campus_map)
                    print(f"DEBUG: Path found by BFS: {path}") # See the actual path list

                    if path:
                        response_text = format_directions(path)
                    else:
                        response_text = f"I couldn't find a path from '{raw_current_location}' to '{raw_destination}'. Please check the names or try a different route or ensure they are connected."

            elif match_accessibility:
                # Extract the location or type from the accessibility query
                if match_accessibility.group(1): # "Is X accessible?"
                    accessibility_query_location = match_accessibility.group(1).strip()
                elif match_accessibility.group(2): # "Show me accessible Y" (Y is a type like "labs")
                    accessibility_query_location = match_accessibility.group(2).strip()
                elif match_accessibility.group(3): # "What is the accessibility of X?"
                    accessibility_query_location = match_accessibility.group(3).strip()

                print(f"DEBUG: Detected Accessibility Query for: '{accessibility_query_location}'")
                
                normalized_query = normalize_location_name(accessibility_query_location)
                print(f"DEBUG: Normalized Accessibility Query: '{normalized_query}'")

                found_accessible_locations = []
                # Check if the query is for a specific location's accessibility
                if normalized_query and normalized_query in location_info and "accessibility" in location_info[normalized_query]:
                    display_name = normalized_query.replace(f"F{get_floor(normalized_query)}_", '').replace('_', ' ') if get_floor(normalized_query) else normalized_query.replace('_', ' ')
                    response_text = f"The accessibility information for {display_name} is: {location_info[normalized_query]['accessibility']}"
                else:
                    # If not a specific location, check for types (e.g., "accessible labs")
                    query_type = normalized_query # Use normalized_query as potential type
                    for loc_key, details in location_info.items():
                        if "type" in details and query_type in details["type"].lower() and "accessibility" in details:
                            # Only add if it's explicitly accessible or has specific info
                            if "accessible" in details["accessibility"].lower() or "ramp" in details["accessibility"].lower() or "elevator" in details["accessibility"].lower():
                                display_name = loc_key.replace(f"F{get_floor(loc_key)}_", '').replace('_', ' ') if get_floor(loc_key) else loc_key.replace('_', ' ')
                                found_accessible_locations.append(f"{display_name} ({details['accessibility']})")
                    
                    if found_accessible_locations:
                        response_text = "Here are some accessible locations: " + ", ".join(found_accessible_locations)
                    else:
                        response_text = f"Sorry, I don't have specific accessibility information for '{accessibility_query_location}' or cannot find accessible locations of that type."


            elif match_info:
                # --- Handle General Location Information Query ---
                location_info_query = match_info.group(1).strip() # Re-extract for clarity
                normalized_location = normalize_location_name(location_info_query)
                print(f"DEBUG: Normalized Info Query Location: '{normalized_location}'")
                if normalized_location and normalized_location in location_info:
                    response_text = location_info[normalized_location]["description"] # Access description field
                else:
                    response_text = f"Sorry, I don't have information about '{location_info_query}'. Please try a different location."
            else:
                print("Agent: I couldn't understand your request. Please state your query in the format 'From [start] to [end]', '[start] to [end]', 'Tell me about [location]', or ask about accessibility like 'Is [location] accessible?'.")
                continue # Ask for input again if format is unclear

            print(f"Agent: {response_text}")

            # --- Speech Output (ElevenLabs) ---
            if response_text:
                try:
                    # Check if the API key is set before attempting generation
                    if not ELEVENLABS_API_KEY or ELEVENLABS_API_KEY == "sk_8f5482590cd5c2861397ea7932b19ebe23c106f87a241385": # Using your actual key as placeholder
                        print("ERROR: ElevenLabs API key is not set or is still the default placeholder. Please update ELEVENLABS_API_KEY in the script.")
                        continue

                    # Corrected call: Use the ElevenLabs client's text_to_speech.generate method
                    audio = elevenlabs_client.text_to_speech.generate( # Corrected method call
                        text=response_text,
                        voice=Voice(
                            voice_id='EXAVITQu4vr4xnSDxMaL', # Default Adam voice ID. You can change this.
                                                              # Find other voice IDs on ElevenLabs website.
                            settings=VoiceSettings(stability=0.75, similarity_boost=0.75, style=0.0, use_speaker_boost=True)
                        )
                    )
                    # In Colab, play() might not work directly for all users.
                    # You might need to download the audio or use Colab's Audio widget.
                    # For local script, play() should work.
                    play(audio)
                except Exception as elevenlabs_e:
                    print(f"ERROR: ElevenLabs voice generation failed: {elevenlabs_e}")
                    print("Please ensure your ElevenLabs API key is correct and you have sufficient credits.")
                    # If it's an API key issue, ElevenLabs might return specific error messages
                    if "authentication" in str(elevenlabs_e).lower() or "api key" in str(elevenlabs_e).lower():
                        print("Double-check your ELEVENLABS_API_KEY for typos or missing characters.")

        except Exception as e:
            print(f"An unexpected error occurred: {e}")
            print("Please try again or refine your query.")

# This ensures the run_campus_navigator() function is called when the script is executed.
if __name__ == '__main__':
    run_campus_navigator()
