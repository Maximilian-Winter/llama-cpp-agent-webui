async function completeText() {

    const aiPersonality = document.getElementById('aiPersonality').value;
    const scenario = document.getElementById('scenario').value;
    const location = document.getElementById('location').value;
    const emotional_state = document.getElementById('emotional-state').value;
    const objectives = document.getElementById('objectives').value;
    const maxTokens = document.getElementById('maxTokens').value;
    const temperature = document.getElementById('temperature').value;
    const topK = document.getElementById('topK').value;
    const topP = document.getElementById('topP').value;
    const repeatPenalty = document.getElementById('repeatPenalty').value;

    const textarea = document.getElementById('userInput');
    const userName = document.getElementById('yourName').value;
    const aiName = document.getElementById('aiName').value;
    const prompt = textarea.value;
    // Create a new list item for the current request
    const responsesList = document.getElementById('chatHistory');
    let listItems = responsesList.getElementsByTagName('li');
    let dialogHistory = [];

    let t = 0;
    for (let i = 0; i < listItems.length; i += 2) {
        dialogHistory[t] += listItems[i].innerText + '\n' + listItems[i + 1].innerText;
        t++;
    }
    if (dialogHistory.length === 0) {
        dialogHistory[0] = ""
    }
    const listItemUser = document.createElement('li');
    const listItemUserTA = document.createElement('p');
    listItemUserTA.className = 'message';
    listItemUserTA.textContent = userName + ": " + prompt;
    listItemUser.appendChild(listItemUserTA);

    const listItemResponse = document.createElement('li');
    const listItemResponseTA = document.createElement('p');
    listItemUserTA.className = 'message';
    listItemResponseTA.textContent = aiName + ": ";
    listItemResponse.appendChild(listItemResponseTA);


    const editBtn = document.createElement('button');
    editBtn.textContent = 'Edit';
    editBtn.className = 'editBtn';

    const deleteBtn = document.createElement('button');
    deleteBtn.textContent = 'Delete';
    deleteBtn.className = 'deleteBtn';

    listItemUser.appendChild(editBtn);
    listItemResponse.appendChild(editBtn.cloneNode(true));

    listItemUser.appendChild(deleteBtn);
    listItemResponse.appendChild(deleteBtn.cloneNode(true));

    responsesList.appendChild(listItemUser);
    responsesList.appendChild(listItemResponse);
    // Connect to the server
    const source = new EventSource(`/llama/complete?personality=${encodeURIComponent(aiPersonality)}&scenario=${encodeURIComponent(scenario)}&location=${encodeURIComponent(location)}&emotion=${encodeURIComponent(emotional_state)}&objectives=${encodeURIComponent(objectives)}&message=${encodeURIComponent(prompt)}&chat_history=${encodeURIComponent(JSON.stringify(dialogHistory))}&max_tokens=${maxTokens}&temperature=${temperature}&top_k=${topK}&top_p=${topP}&repeat_penalty=${repeatPenalty}&stop=${encodeURIComponent(userName + ":")}`);

    source.onmessage = (event) => {
        // Update the text content of the list item with the received text
        listItemResponseTA.textContent += event.data;
    };

    source.onerror = (error) => {
        console.error('Error:', error);
        source.close();
    };

    source.addEventListener('complete', () => {
        // Close the connection when the request is completed
        source.close();
    });


}

function loadCharacter() {
    fetch('/roleplay/get_character')
        .then(response => response.json())
        .then(data => setCharacter(data));
}

function setCharacter(char) {
    const aiPersonality = document.getElementById('aiPersonality');
    const scenario = document.getElementById('scenario');
    const location = document.getElementById('location');
    const emotional_state = document.getElementById('emotional-state');
    const objectives = document.getElementById('objectives');

    aiPersonality.value = char.personality;
    scenario.value = char.scenario;
    location.value = char.location;
    emotional_state.value = char.emotional_state;
    objectives.value = char.objectives;
}

function createCharacter() {
    const aiPersonality = document.getElementById('aiPersonality').value;
    const scenario = document.getElementById('scenario').value;
    const location = document.getElementById('location').value;
    const emotional_state = document.getElementById('emotional-state').value;
    const objectives = document.getElementById('objectives').value;
    const userName = document.getElementById('yourName').value;
    const aiName = document.getElementById('aiName').value;
    const folder = document.getElementById('safe_name').value;
    const serverUrl = '/roleplay/create';
    const params = {
        folder: folder,
        ai_name: aiName,
        user_name: userName,
        personality: aiPersonality,
        scenario: scenario,
        location: location,
        emotional_state: emotional_state,
        objectives: objectives
    }

    // Create a query string from params object
    let query = Object.keys(params)
        .map(k => encodeURIComponent(k) + '=' + encodeURIComponent(params[k]))
        .join('&');

    fetch(`${serverUrl}?${query}`, {
        method: 'GET', // or 'POST'
        headers: {
            'Content-Type': 'application/json',
            // 'Content-Type': 'application/x-www-form-urlencoded',
        },
    })
        .then(response => response.json())
        .then(data => console.log(data))
        .catch((error) => {
            console.error('Error:', error);
        });
}

function clearChatHistory() {
    const chatHistory = document.getElementById('chatHistory');
    while (chatHistory.firstChild) {
        chatHistory.removeChild(chatHistory.firstChild);
    }
}

function openLoadAIBasicSettingsFileDialog() {
    const input = document.createElement('input');
    input.type = 'file';
    input.accept = '.json';
    input.onchange = (e) => loadAIBasicSettingsFromFile(e);
    input.click();
}


function openLoadChatHistoryFileDialog() {
    const input = document.createElement('input');
    input.type = 'file';
    input.accept = '.json';
    input.onchange = (e) => loadChatHistoryFromFile(e);
    input.click();
}

function openLoadGenerationParametersFileDialog() {
    const input = document.createElement('input');
    input.type = 'file';
    input.accept = '.json';
    input.onchange = (e) => loadGenerationParametersFromFile(e);
    input.click();
}

function loadAIBasicSettingsFromFile(e) {
    const file = e.target.files[0];
    if (!file) {
        return;
    }

    const reader = new FileReader();
    reader.onload = function (e) {
        const contents = e.target.result;
        const settings = JSON.parse(contents);

        document.getElementById('yourName').value = settings.yourName || 'You';
        document.getElementById('aiName').value = settings.aiName || 'Assistant';
        document.getElementById('aiPersonality').value = settings.aiPersonality || 'Assistant is a highly intelligent language model trained to comply with user requests.';
        document.getElementById('aiFirstMessage').value = settings.aiFirstMessage || 'Hello! How may I help you today?';
    };
    reader.readAsText(file);
}

function saveAIBasicSettingsToFile() {
    const settings = {
        yourName: document.getElementById('yourName').value,
        aiName: document.getElementById('aiName').value,
        aiPersonality: document.getElementById('aiPersonality').value,
        aiFirstMessage: document.getElementById('aiFirstMessage').value
    };
    const json = JSON.stringify(settings, null, 2);
    const blob = new Blob([json], {type: 'application/json'});
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');

    a.href = url;
    a.download = 'ai-basic-settings.json';
    a.style.display = 'none';
    document.body.appendChild(a);
    a.click();

    setTimeout(() => {
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
    }, 0);
}

function loadGenerationParametersFromFile(e) {
    const file = e.target.files[0];
    if (!file) {
        return;
    }

    const reader = new FileReader();
    reader.onload = function (e) {
        const contents = e.target.result;
        const settings = JSON.parse(contents);

        document.getElementById('maxTokens').value = settings.maxTokens || 1200;
        document.getElementById('temperature').value = settings.temperature || 0.65;
        document.getElementById('topK').value = settings.topK || 40;
        document.getElementById('topP').value = settings.topP || 0.9;
        document.getElementById('repeatPenalty').value = settings.repeatPenalty || 1.3;
    };
    reader.readAsText(file);
}

function saveGenerationParametersToFile() {
    const settings = {
        maxTokens: document.getElementById('maxTokens').value,
        temperature: document.getElementById('temperature').value,
        topK: document.getElementById('topK').value,
        topP: document.getElementById('topP').value,
        repeatPenalty: document.getElementById('repeatPenalty').value
    };
    const json = JSON.stringify(settings, null, 2);
    const blob = new Blob([json], {type: 'application/json'});
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');

    a.href = url;
    a.download = 'generation-parameters.json';
    a.click();

    URL.revokeObjectURL(url);
}

function saveChatHistoryToFile() {
    const chatHistory = document.getElementById('chatHistory');
    const messages = Array.from(chatHistory.querySelectorAll('li')).map(li => li.textContent);
    const json = JSON.stringify(messages, null, 2);
    const blob = new Blob([json], {type: 'application/json'});
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');

    a.href = url;
    a.download = 'chat-history.json';
    a.click();

    URL.revokeObjectURL(url);
}

function loadChatHistoryFromFile(e) {
    const file = e.target.files[0];
    if (!file) {
        return;
    }

    const reader = new FileReader();
    reader.onload = function (e) {
        const contents = e.target.result;
        const messages = JSON.parse(contents);
        const chatHistory = document.getElementById('chatHistory');
        chatHistory.innerHTML = '';

        messages.forEach(message => {
            const li = document.createElement('li');
            li.textContent = message;
            chatHistory.appendChild(li);
        });
    };
    reader.readAsText(file);
}

function adjustTextareaRows(textarea, maxRows) {
    textarea.rows = 1; // Reset rows to 1 before calculating the needed rows
    const lines = textarea.value.split('\n').length;
    textarea.rows = Math.min(lines, maxRows);
}

document.addEventListener('DOMContentLoaded', function () {
    const userInput = document.getElementById('userInput');
    const maxRows = 5;

    userInput.addEventListener('input', function () {
        adjustTextareaRows(userInput, maxRows);
    });
});

document.addEventListener('click', function (e) {
    // Check if the Delete button was clicked and remove the parent node if true
    if (e.target && e.target.className === 'deleteBtn') {
        e.target.parentNode.remove();
    }
    // Check if the Edit button was clicked
    else if (e.target && e.target.className === 'editBtn') {
        const parent = e.target.parentNode;
        const messageNode = parent.querySelector('.message'); // Assuming messages have a 'message' class
        if (messageNode) {
            const currentText = messageNode.textContent;
            const input = document.createElement('textarea');
            input.type = 'text';
            input.value = currentText;
            input.className = 'editInput'; // Assign a class for styling if needed

            // Replace the message with the input field
            parent.replaceChild(input, messageNode);

            // Focus the input field and select its content
            input.focus();
            input.select();

            // Function to handle replacing the input with the updated message text
            function saveEditedMessage() {
                const updatedText = input.value.trim();
                if (updatedText) { // Check if the updated text is not empty
                    messageNode.textContent = updatedText;
                    parent.replaceChild(messageNode, input); // Replace the input with the updated message
                } else {
                    parent.remove(); // Optionally remove the message if the input is empty
                }
                // Remove event listeners to prevent memory leaks
                input.removeEventListener('blur', saveEditedMessage);
                input.removeEventListener('keypress', handleKeypress);
            }

            // Save the edited message when the input field loses focus
            input.addEventListener('blur', saveEditedMessage);

            // Also save the edited message when the Enter key is pressed
            function handleKeypress(e) {
                if (e.key === 'Enter') {
                    saveEditedMessage();
                }
            }
            input.addEventListener('keypress', handleKeypress);
        }
    }
});


document.addEventListener("DOMContentLoaded", function () {
    var tablinks = document.querySelectorAll(".tablinks");

    tablinks.forEach(function (btn) {
        btn.addEventListener("click", function () {
            // Use the data-tab attribute to get the corresponding tab content ID
            var tabName = this.getAttribute("data-tab");
            openTab(this, tabName);
        });
    });

    // Automatically open the first tab when the page loads
    if (tablinks.length > 0) {
        tablinks[0].click();
    }
});

function openTab(sender, tabName) {
    var i, tabcontent, tablinks;
    tabcontent = document.getElementsByClassName("tabcontent");
    for (i = 0; i < tabcontent.length; i++) {
        tabcontent[i].style.display = "none";
    }
    tablinks = document.getElementsByClassName("tablinks");
    for (i = 0; i < tablinks.length; i++) {
        tablinks[i].className = tablinks[i].className.replace(" active", "");
    }
    document.getElementById(tabName).style.display = "block";
    sender.className += " active";
}