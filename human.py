from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_socketio import SocketIO, emit
import ollama
import asyncio
import logging
import traceback
import random
import json 

app = Flask(__name__)
CORS(app, origins="http://localhost:3000")
socketio = SocketIO(app, cors_allowed_origins="*")

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

def emit_status(model, status, content):
    logging.debug(f"Emitting: {model} - {status} - {content}")
    socketio.emit(
        "update",
        {"model": model, "status": status, "content": content},
        namespace="/"
    )

class Human:
    async def chat_with_model(self, model_name, user_message):
        try:
            logging.debug(f"Starting chat with {model_name}: {user_message}")
            client = ollama.AsyncClient()  # Create the client
            full_response = ""
            try:
                response = await client.chat(
                    model=model_name,
                    messages=[{"role": "user", "content": user_message}],
                    stream=True,
                )
                async for part in response:
                    content_part = part['message']['content']
                    full_response += content_part
                    emit_status(model_name, "working", content_part)
                    logging.debug(f"Received part from {model_name}: {content_part}")
            except Exception as stream_err:
                logging.error(f"Error during streaming with {model_name}: {stream_err}")
                emit_status(model_name, "error", f"Streaming Error: {stream_err}")
            
            return {"message": {"content": full_response}}
        except ollama.ResponseError as e:
            logging.error(f"Ollama Response Error with {model_name}: {e}")
            emit_status(model_name, "error", f"Ollama Error: {e}")
            return {"message": {"content": f"Ollama Error: {e}"}}
        except Exception as e:
            logging.exception(f"Unexpected Error in chat_with_model with {model_name}:")
            emit_status(model_name, "error", f"Unexpected Error: {e}")
            return {"message": {"content": f"Unexpected Error: {e}"}}

class CEO:
    def break_down_task(self, task):
        return [sub_task.strip() for sub_task in task.split('.') if sub_task.strip()]

class Manager:
    def __init__(self, models):
        self.models = models
        self.human = Human()

    async def assign_tasks(self, sub_tasks):
        tasks = []
        for i, sub_task in enumerate(sub_tasks):
            employee = self.models[i % len(self.models)]
            tasks.append(self.human.chat_with_model(employee, sub_task))

        results = await asyncio.gather(*tasks)
        return {self.models[i % len(self.models)]: results[i] for i in range(len(sub_tasks))}

async def process_task(task):
    ceo = CEO()
    manager = Manager(["Lisa", "Yuki"])  # Use your model names

    sub_tasks = ceo.break_down_task(task)
    logging.debug(f"Subtasks: {sub_tasks}")

    emit_status("ceo", "working", task)
    for model in manager.models:
        emit_status(model, "working", "Analyzing task...")

    results = await manager.assign_tasks(sub_tasks)
    logging.debug(f"Results: {results}")

    final_results = {model: result["message"]["content"] for model, result in results.items()}

    emit_status("ceo", "finished", "All tasks completed.")
    for model, result in final_results.items():
        emit_status(model, "finished", result)

    return final_results

@app.route('/assign-task', methods=['POST'])
async def assign_task():
    task_data = request.get_json()
    task = task_data.get('task', 'No task provided')
    logging.debug(f"Received task: {task}")
    try:
        results = await process_task(task)
        return jsonify({"results": results}), 200
    except Exception as e:
        logging.exception("Error in /assign-task route:")
        return jsonify({"error": "An error occurred."}), 500


async def automate_tasks():
    try:
        # Load tasks from the JSON file
        with open("tasks.json", "r") as f:
            tasks = json.load(f)

        while True:
            # Pick a random task
            task_data = random.choice(tasks)
            generated_task = task_data["task"]
            logging.debug(f"Selected Task: {generated_task}")

            # Process the selected task
            results = await process_task(generated_task)
            logging.debug(f"Task Results: {results}")

            # Write results to another JSON file
            with open("automate_tasks_results.json", "a") as f:
                f.write(json.dumps({"task": generated_task, "results": results}) + "\n")

            # Add a small delay between tasks
            await asyncio.sleep(5)

    except Exception as e:
        logging.error("Error during automate_tasks loop:", exc_info=e)

@app.route('/automate', methods=['POST'])
def automate():
    try:
        # Run the automate_tasks coroutine asynchronously
        asyncio.run(automate_tasks())
        return jsonify({"status": "Automation started"}), 200
    except Exception as e:
        logging.error("Error starting automation:", exc_info=e)
        return jsonify({"error": "Failed to start automation"}), 500




if __name__ == "__main__":
    socketio.run(app, debug=True, host="127.0.0.1", port=5000)