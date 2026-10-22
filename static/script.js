// Communication + presentation. Python owns the answer key and scoring.
const heading = document.querySelector("#question");
const choices = document.querySelector("#choices");
const feedback = document.querySelector("#feedback");
const retry = document.querySelector("#retry");
let busy = false;

async function api(path, body) {
  const response = await fetch(path, {
    method: body === undefined ? "GET" : "POST",
    headers: body === undefined ? {} : { "Content-Type": "application/json" },
    body: body === undefined ? undefined : JSON.stringify(body),
  });
  const data = await response.json();
  if (!response.ok) throw new Error(data.error || "Something went wrong. Reload to continue.");
  return data;
}

function showError(error) {
  feedback.className = "incorrect";
  feedback.textContent = error.message || "Connection lost. Reload to continue.";
  // Never blindly resend an answer: the server may already have received it.
  retry.hidden = false;
}

function render(data) {
  busy = false;
  choices.replaceChildren();
  feedback.textContent = "";
  feedback.className = "";
  retry.hidden = true;
  document.querySelector("#progress").hidden = data.complete;
  if (data.complete) {
    heading.textContent = "Quiz Complete";
    const score = document.createElement("p");
    score.className = "final-score";
    score.textContent = `${data.score} / ${data.total}`;
    const percentage = document.createElement("p");
    percentage.className = "percentage";
    percentage.textContent = `${data.percentage}%`;
    choices.append(score, percentage);
  } else {
    heading.textContent = data.question;
    document.querySelector("#number").textContent = `Question ${data.number} of ${data.total}`;
    document.querySelector("#score").textContent = `Score: ${data.score}`;
    data.choices.forEach((choice) => {
      const button = document.createElement("button");
      button.textContent = choice; // Text, not HTML: file contents cannot inject markup.
      button.addEventListener("click", () => submit(choice, data.token, button));
      choices.append(button);
    });
  }
  heading.focus();
}

async function submit(selected, token, button) {
  if (busy) return;
  busy = true;
  choices.querySelectorAll("button").forEach((item) => { item.disabled = true; });
  button.classList.add("selected");
  try {
    const result = await api("/api/answer", { selected, token });
    feedback.textContent = result.correct ? "Correct" : "Incorrect";
    feedback.className = result.correct ? "correct" : "incorrect";
    document.querySelector("#score").textContent = `Score: ${result.score}`;
    setTimeout(async () => {
      try { render(await api("/api/question")); } catch (error) { showError(error); }
    }, 1000);
  } catch (error) { showError(error); }
}

async function initialize() {
  try {
    const response = await fetch("/api/question");
    if (response.status === 409) render(await api("/api/start", {}));
    else if (response.ok) render(await response.json());
    else throw new Error("Unable to load the quiz. Reload to try again.");
  } catch (error) { showError(error); }
}

retry.addEventListener("click", () => window.location.reload());
initialize();
