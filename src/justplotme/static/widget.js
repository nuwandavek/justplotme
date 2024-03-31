async function loadScript(href) {
  if (document.querySelector(`script[src='${href}']`)) {
      return;
  }
  return new Promise((resolve, reject) => {
    let script = Object.assign(document.createElement("script"), {
      src: href,
      onload: resolve,
      onerror: reject,
    });
    document.body.append(script);
  })
}   
await loadScript("https://cdn.plot.ly/plotly-2.30.0.min.js");

function createElement(DOMtype, id, classNames){
  let ele = document.createElement(DOMtype);
  if (id!=null){
    ele.id = id
  }
  classNames.forEach(className => ele.classList.add(className));
  return ele
}

function populateChats(chats){
  let chatContainer = document.getElementById("chat-list-container");
  if (chatContainer == null){
    setTimeout(() => populateChats(chats), 10);
    return;
  }
  chatContainer.innerHTML = "";
  chats.forEach(chat => {
    let chatDiv = createElement("div", null, ["role-" + chat.role, "chat-div"]);
    let messageDiv = createElement("div", null, ["role-chat-" + chat.role, "message-div"]);

    messageDiv.innerHTML = chat.html;

    chatDiv.appendChild(messageDiv);
    chatContainer.appendChild(chatDiv);
  });
  chatContainer.scrollTop = chatContainer.scrollHeight;
}

function displayPlot(plot_html){
  let plotContainer = document.getElementById("plot-container");
  if (plotContainer == null){
    return;
  }
  plotContainer.innerHTML = "";

  let script = document.createElement('script');
  script.textContent = plot_html;
  plotContainer.appendChild(script);
}

function initComponents(model, el){
  let mainContainer = createElement("div", "main-container", []);
  let chatContainer = createElement("div", "chat-container", []);
  let plotContainer = createElement("div", "plot-container", []);
  let chatListContainer = createElement("div", "chat-list-container", []);
  let inputContainer = createElement("div", "input-container", []);
  let inputBox = createElement("input", "input-box", []);
  let inputButton = createElement("button", "input-button", []);
  let plotMeP = createElement("p", "justplotme-p", []);
  
  chatListContainer.innerHTML = "";
  plotContainer.innerHTML = "<p id='justplotme'>justplotme</p>";
  plotMeP.innerHTML = "justplotme";
  inputButton.innerHTML = "<i class='bx bxs-send'></i>";
  inputButton.onclick = () => {
    let message = document.getElementById("input-box").value;
    console.log(message);
    document.getElementById("input-box").value = "";
    model.send({ content: message, type: "chat" });
  };
  
  inputContainer.appendChild(inputBox);
  inputContainer.appendChild(inputButton);
  
  chatContainer.appendChild(chatListContainer);
  chatContainer.appendChild(inputContainer);
  mainContainer.appendChild(chatContainer);
  mainContainer.appendChild(plotContainer);
  mainContainer.appendChild(plotMeP);
  el.appendChild(mainContainer);

  populateChats(model.get("chat"));
}


function render({ model, el }) {
  model.on("change:chat", () => {
    populateChats(model.get("chat"));
  });

  model.on("change:plot_html", () => {
    displayPlot(model.get("plot_html"));
  });

  initComponents(model, el);
}

export default { render };