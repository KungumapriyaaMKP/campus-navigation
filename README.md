Sri Eshwar's Campus Navigator
Project Description
The Campus Navigator is an interactive, voice-enabled Python agent designed to assist students and visitors in navigating the Sri Eshwar College of Engineering (SECE) campus. It provides step-by-step directions between locations, offers detailed information about various campus facilities, and includes accessibility details for an inclusive experience.

Features
Intelligent Pathfinding: Utilizes a Breadth-First Search (BFS) algorithm to find the shortest routes between any two points on the campus map.

Location Information: Provides descriptive details about specific campus locations (e.g., "What is the Library?").

Accessibility Information (Unique Feature): Offers details on the accessibility features of various locations (e.g., "Is the Main Block accessible?", "Show me accessible labs.").

Voice Interaction: Integrates with ElevenLabs for Text-to-Speech (TTS) to provide spoken responses, making the interaction more natural (requires a working audio setup).

Natural Language Understanding: Employs robust string normalization and regex-based intent detection to understand varied user queries for directions, general information, and accessibility.

Modular Design: The campus map data, location descriptions, and accessibility information are easily configurable within Python dictionaries.

Technologies Used
Python 3.x: The core programming language.

ElevenLabs API: For Text-to-Speech (TTS) voice generation.

Deepgram API: (Integrated in concept for Speech-to-Text, but simulated with text input in the current script for simplicity).

Regular Expressions (re module): For parsing user input and extracting key information.

Setup and Installation
Prerequisites
Python 3.8 or higher installed.

pip (Python package installer).

API Keys from:

ElevenLabs: For Text-to-Speech.

Deepgram: For Speech-to-Text (though currently simulated with text input).

Lyzr: (Optional, for Lyzr Agent integration if uncommented and configured).

Installation Steps
Clone or Download the Project:
(If you have a Git repository, you'd provide the clone command here. Otherwise, instruct the user to download the agent.py file.)

Install Required Python Packages:
Open your terminal or command prompt and run:

pip install elevenlabs deepgram-sdk lyzr

(Note: lyzr is installed, but LyzrAgent is commented out in the current script. deepgram-sdk is installed for completeness, though direct audio input isn't implemented in this version.)

Configure API Keys:
Open the agent.py file and replace the placeholder API keys with your actual keys:

LYZR_API_KEY = "YOUR_LYZR_API_KEY"
DEEPGRAM_API_KEY = "YOUR_DEEPGRAM_API_KEY"
ELEVENLABS_API_KEY = "YOUR_ELEVENLABS_API_KEY"

Make sure os.environ["ELEVEN_LABS_API_KEY"] is also set correctly with your ElevenLabs key.

How to Run
Open your terminal or command prompt.

Navigate to the directory where you saved agent.py.

Execute the script:

python agent.py

The agent will start and prompt you for input.

How to Use
Once the agent is running, you can interact with it by typing your queries. The agent will respond in text and, if your system's audio is configured correctly, via voice.

Examples of Queries:
Getting Directions:

How do I get from Floor 1 Main Block to Floor 3 Library?

Directions from Reception to Cafeteria.

I'm at the IT Centre, how do I go to the Dean's Office?

Path from Boys Hostel to Fitness Centre.

Getting Location Information:

Tell me about the Main Gate.

What is the IT Centre?

Info on the Library.

Describe the Auditorium.

Asking about Accessibility (New Feature!):

Is the Library accessible?

Show me accessible labs.

What is the accessibility of the Main Block?

Exiting the Agent:

Type exit, quit, or bye to end the conversation.

Future Enhancements
Full Voice Input: Integrate Deepgram's streaming API for real-time microphone input.

Graphical User Interface (GUI): Develop a web-based (e.g., React) or desktop GUI for a more intuitive user experience, potentially using a backend API for the Python logic.

Dynamic Map Visualization: Display the path on an interactive campus map.

Database Integration: Store campus data (locations, descriptions, accessibility) in a database for easier management and scalability.

Advanced NLP: Integrate a full LLM (like Lyzr Agent or Gemini API) for more sophisticated intent recognition and conversational flow.

Real-time Location Tracking: (More complex, requires GPS/indoor positioning).
