

tippy('.lisa', {
    followCursor: true,
    content:'This is Lisa'
  });
tippy('.yuki', {
    followCursor: true,
    content:'This is Yuki'
  });
tippy('.ceo', {
    followCursor: true,
    content:'This is CEO'
  });

document.querySelector(".openTasks").addEventListener('click',()=>{
  document.querySelector(".tasksMenu").style.display = "block";
})

document.querySelector(".closebtn").addEventListener('click',()=>{
  document.querySelector(".tasksMenu").style.display = "none";
})


document.addEventListener("DOMContentLoaded", () => {
  const socket = io("http://localhost:5000");

  socket.on("connect", () => {
      console.log("Connected to the server!");
  });

  socket.on("connect_error", (error) => {
      console.error("Connection error:", error);
  });

  socket.on("update", (data) => {
      const { model, status, content } = data;
      console.log(`Received update for ${model}: ${status} - ${content}`);
      setCharacterState(model, status, content);
  });


  
  document.getElementById("assign").addEventListener("click", async () => {
      const taskInput = document.getElementById("taskInput").value;
      if (!taskInput) {
          alert("Please enter a task for the CEO!");
          return;
      }

      setCharacterState("ceo", "working", "Task Assigned !");
      setCharacterState("yuki", "working", "Working on it..");
      setCharacterState("lisa", "working", "Working on it..");

      try {
          const response = await assignTaskToBackend(taskInput);
          if (response && response.results) {
              displayResults(response.results);
          } else {
              console.error("Invalid response format from server:", response);
              setCharacterState("yuki", "error", "Error processing task");
              setCharacterState("lisa", "error", "Error processing task");
              alert("Error processing task. Please check the server logs.");
          }
      } catch (error) {
          console.error("Error assigning task:", error);
          setCharacterState("yuki", "error", "Error assigning task");
          setCharacterState("lisa", "error", "Error assigning task");
          alert("An error occurred while assigning the task.");
      }
  });

  async function assignTaskToBackend(task) {
      try {
          const response = await fetch("http://127.0.0.1:5000/assign-task", {
              method: "POST",
              headers: {
                  "Content-Type": "application/json",
              },
              body: JSON.stringify({ task }),
              mode: "cors",
          });

          if (!response.ok) {
              const errorText = await response.text();
              
              throw new Error(`Server returned ${response.status}: ${errorText || 'Failed to assign task'}`);
          }

          try {
              setCharacterState("yuki", "working", "Idle");
              setCharacterState("lisa", "working", "Idle");
              return await response.json();
          } catch (jsonError) {
              console.error("Error parsing JSON response:", jsonError, await response.text());
              throw new Error("Invalid JSON response from server.");
          }


      } catch (error) {
          console.error("Error in assignTaskToBackend:", error);
          throw error;
      }

  }

  function displayResults(results) {
    const resultsContainer = document.getElementById("task_results");
    resultsContainer.innerHTML = ""; // Clear previous results

    if (typeof results !== 'object' || results === null) {
        console.error("Invalid results format:", results);
        const errorMsg = document.createElement('p');
        errorMsg.textContent = "Error: Invalid data received from server.";
        resultsContainer.appendChild(errorMsg);
        return; // Important: Exit the function to prevent further errors
    }

    const ul = document.createElement('ul');
    ul.classList.add('task-list');

    for (const model in results) {
        if (results.hasOwnProperty(model)) { // Check if it's an own property
            const resultText = results[model];
            const li = document.createElement('li');
            li.textContent = `${model} : ${resultText}`;
            ul.appendChild(li);
        }
    }

    resultsContainer.appendChild(ul);
}

  document.getElementById("automate").addEventListener("click", async () => {
    try {
      const response = await startAutomation();
      if (response.status === "Automation started") {
        alert("Automation started successfully!");
      } else {
        console.error("Failed to start automation:", response);
        alert("Failed to start automation. Please check server logs.");
      }
    } catch (error) {
      console.error("Error starting automation:", error);
      alert("An error occurred while starting automation.");
    }
  });

  async function startAutomation() {
    setCharacterState("ceo", "working", "Automated !!");
    setCharacterState("yuki", "working", "Working on it..");
    setCharacterState("lisa", "working", "Working on it..");
    try {
      const response = await fetch("http://127.0.0.1:5000/automate", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        mode: "cors",
      });

      if (!response.ok) {
        const errorText = await response.text();
        throw new Error(`Server returned ${response.status}: ${errorText || "Failed to start automation"}`);
      }

      return await response.json();
    } catch (error) {
      console.error("Error in startAutomation:", error);
      throw error;
    }
  }
  function setCharacterState(character, state, taskMessage) {
      const gif = document.getElementById(`${character}Idle`);
      const taskText = document.getElementById(`${character}Task`);

      if (state === "working") {
          gif.classList.add("working");
          taskText.textContent = taskMessage || `${character} is working...`;
      } else if (state === "error") {
          gif.classList.add("error");
          taskText.textContent = taskMessage || "Error occurred";
      } else {
          gif.classList.remove("working", "error");
          taskText.textContent = taskMessage || `${character} is idle`;
      }
  }
});
