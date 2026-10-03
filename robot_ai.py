from flask import Flask, request, jsonify
import ollama
import os

app = Flask(__name__)

@app.route('/think', methods=['POST'])
def think():
    if 'image' not in request.files:
        return jsonify({"error": "No image provided"}), 400
    
    image_file = request.files['image']
    image_path = "/tmp/robot_view.jpg"
    image_file.save(image_path)

    # THE EXPLORER & HUMAN FOLLOWER PROMPT
    # system_prompt = """
    # You are the endless thinking brain of an autonomous mobile robot. 
    # You are constantly exploring your environment. 
    # Your priorities are:
    # 1. HUMAN FOLLOWING: If you see a human in the image, prioritize moving toward them. If they are to the left, say LEFT. If straight ahead, say FORWARD.
    # 2. CURIOSITY: If no human is present, act like a curious explorer. Seek open space and interesting objects. 
    # 3. OBSTACLE AVOIDANCE: If there is an obstacle or wall directly ahead, but an open path to the left, say LEFT. If left is blocked but right is open, say RIGHT.
    # 4. SAFETY: Only say STOP if you are completely trapped in a corner and cannot move.

    # You MUST reply with ONLY ONE of these four exact words: FORWARD, LEFT, RIGHT, STOP.
    # Do not add any punctuation. Do not explain yourself.
    # """
    system_prompt = """
    You are the brain of an autonomous mobile robot trying to exit a room.
    Look at the image carefully.
    1. Look for a doorway or an open hallway. Your goal is to navigate toward the door.
    2. If you see food boxes or obstacles on the floor blocking your path, do not go towards them. 
    3. If the door or open path is to the RIGHT, you MUST say RIGHT.
    4. If the door or open path is to the LEFT, you MUST say LEFT.
    5. If the path straight ahead is perfectly clear, say FORWARD.
    6. Only say STOP if you are completely trapped.
    Reply with ONLY ONE of these four exact words: FORWARD, LEFT, RIGHT, STOP. No punctuation.
    """
    try:
        response = ollama.chat(
            model='llava',
            messages=[
                {'role': 'user', 'content': system_prompt, 'images': [image_path]}
            ]
        )
        
        ai_decision = response['message']['content'].strip().upper()
        
        valid_commands = ['FORWARD', 'LEFT', 'RIGHT', 'STOP']
        if ai_decision not in valid_commands:
            ai_decision = 'STOP'

        if os.path.exists(image_path):
            os.remove(image_path)

        return jsonify({"command": ai_decision})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    print("Brain server starting on port 5000...")
    app.run(host='0.0.0.0', port=5001)
