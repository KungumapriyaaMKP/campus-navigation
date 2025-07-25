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
LYZR_API_KEY = "sk-default-UVwrao9HeTWXAk5gb3d0cf1VWSZ304Bv"  # Your Lyzr API Key
DEEPGRAM_API_KEY = "7f45437a1cdd0a8d860d1e04f78a3639f77d1"  # Your Deepgram API Key
ELEVENLABS_API_KEY = "sk_0fa00a8b899e41cfb471bd1a912982fe68208934c1b26de1"


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
