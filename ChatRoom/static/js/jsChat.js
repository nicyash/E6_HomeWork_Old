const divProfil = document.querySelector('.div_profil');
const divRooms = document.querySelector('.div_rooms');
const divUsers = document.querySelector('.div_users');
const divChat = document.querySelector('.div_chat');
const domain = ('http://127.0.0.1:8000/api/');
const userId = window.userID;
let currentRoomId = "";

//функция получения токена
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length +

    1));break;}}}return cookieValue;
}
//записываем токен в переменную
const csrftoken = getCookie('csrftoken');


// формируем случайный номер для WS для возможности одновременного открытия на разных вкладках
let sockNum =  'sn' + Math.floor(Math.random() * 100 + 1);


const socket = new WebSocket('ws://localhost:8000/ws/command/' + sockNum); // командный канал
const socketForChat = new WebSocket('ws://localhost:8000/ws/chat/' + sockNum); //для сообщений
socket.onclose = async (event) => {
    console.error(event);
    window.alert('запустите сервер и обновите страницу!');
};

socket.onopen = () => load_userCard();
function load_userCard() {
    viewProfil(userId);
    viewRooms();
};

socket.onmessage = function(event) {
    let data = JSON.parse(event.data);
    console.log(data);

    if ('MessageList' in data) {
        showChat(data);
    };
};

// Запрос данных пользователя
function viewProfil(userId) {
    fetch(domain + 'user/' + userId +'/')
        .catch(err => console.log(err))
        .then(response => response.json())
        .then(result => showProfil(result));
};

function viewUsers() {
    console.log('Пользователи могут быть показаны');
    fetch(domain + 'user/')
        .catch(err => console.log(err))
        .then(response => response.json())
        .then(result => showUsers(result));
};

// Запрос списка комнат
function viewRooms() {
    fetch(domain + 'rooms/')
        .catch(err => console.log(err))
        .then(response => response.json())
        .then(result => showRooms(result));
};

// Вывод профиля в браузер
function showProfil(item) {
    console.log(item);
    divProfil.innerHTML = `
    <div class="div_profil">
        <img class="img_avatar" src="${item.avatar}">
        <br>
        <strong>Сменить аватарку:</strong>
        <br>
        <input class="btn" id="avatar-input" type="file" accept="image/*"><br>
        <button class="btn" onclick="changeAvatar(${item.user})">отправить</button>
        <p style="text-align: left;">ID: ${item.user}</p>
        <p style="text-align: left;">
        Имя: ${item.first_name}
        <button class="btn" onclick="changeFirstName(${item.user})">изменить</button>
        </p>
        <h4 class="message" id="message"></h4>
    </div>
    `;
};

// Вывод Пользователей в браузер
 function showUsers(item) {
    let listUser = '';
    for (let key in item) {
        if (item[key].user != userId) {
            const newStringOnUser = `<tr><td><img class="img_avatar" width="22" height="22" src="${item[key].avatar}"><b><button style="width: 200px;" class="btn" onclick="jampInUser('${item[key].first_name}')">${item[key].first_name}</button></b></td></tr>`;
            listUser = listUser + newStringOnUser;
            };
    };
    listUser = '<table>' + listUser + '</table><br>'
    divUsers.innerHTML = listUser;
};

// Вывод комнат в браузер
function showRooms(item) {
//    delete item.RoomList;
    let listRoom = '';
    for (let key in item) {
        const newStringOnRoom = `<tr><td><b><button style="width: 200px;" class="btn" onclick="jampInRoom(${item[key].id})">${item[key].name}</button></b></td>
        <td><button class="btn" onclick="deleteRoom(${item[key].id})">🗑</button></td>
        <td><button class="btn" onclick="changeRoom(${item[key].id})">🔄</button></td></tr>`;
        listRoom = listRoom + newStringOnRoom;
    };
    listRoom = '<table>' + listRoom + '</table><br>'
    listRoom = listRoom + `<input type="text" id="input_room" name="name_new_room" size="32" placeholder="Введите имя новой комнаты"><br>`
    listRoom = listRoom + `<button style="width: 275px;" class="btn btn_new_room">Создать комнату</button>`
    divRooms.innerHTML = listRoom;

    // Создание новой комнаты
    document.querySelector('.btn_new_room').addEventListener('click', () => {
        let name = document.getElementById("input_room");
        if (name.value !== "") {
            socket.send(JSON.stringify({'create_room': name.value}));
            console.log({'create_room': name.value});
            name.value = "";
            viewRooms();
        };
    });
};

// замена аватара
async function changeAvatar(userId) {
    const formData = new FormData();
    let fileField = document.querySelector('#avatar-input');
    if (fileField.files[0]) {
        formData.append('avatar', fileField.files[0]);
        try {
            const response = await fetch(domain + 'user/' + userId +'/', {
                method: 'PATCH',
                headers: {'X-CSRFToken': csrftoken},    //записываем токен в загаловок для прохождения безопасности
                body: formData
            });
            const result = await response.json();
            console.log('Результат сохранения:', JSON.stringify(result));
        } catch (error) {
            console.log('Все пропало!!!');
            console.error('Ошибка:', error);
        }
        viewProfil(userId);
        viewUsers();;
    } else {
        document.querySelector('#message').innerText = 'выберите файл!';
    };
};

//замена имени
function changeFirstName(userId) {
    let name = prompt('Введите новое имя');
    socket.send(JSON.stringify({'replacement': 'changeFirstName', 'id': userId, 'name': name }));
    console.log({'replacement': 'changeFirstName', 'id': userId, 'name': name })
    viewProfil(userId);
};
// удаление комнаты
function deleteRoom(item) {
    socket.send(JSON.stringify({'delete_room': item}));
    console.log(item, " комната удалена")
    viewRooms();
};
// изменение названия
function changeRoom(item) {
    let name = prompt('Введите новое имя');
    socket.send(JSON.stringify({'change_room': item, 'name': name }));
    console.log(item)
    viewRooms();
};
//переход вчат комнату
function jampInRoom(item) {
    viewUsers();
    delete item.RoomList;
    console.log("перешел на комноту", item)
    // Запрашиваем список сообщений комнаты в !!! командном канале
    socket.send(JSON.stringify({'load': 'messageList', 'room_id': item}));
    currentRoomId = item;
    console.log({'load': 'messageList', 'room_id': item});
    console.log(currentRoomId);
     // Запрос на сервер на подключение к чту и отключение от предыдущей
    socketForChat.send(JSON.stringify({'usersendcommandroom': 'roomselect', 'newroom_id': item, 'oldroom_id': currentRoomId}));
    currentRoomId = item; // обновляем ID текущей комнаты
};
// переход в чат с пользователем
function jampInUser(item) {
    let inputMessage = document.querySelector('.message_box');
    inputMessage.value += (item + ", ");

    console.log("Обращаюсь к пользователю с ID ", item)
};

// выводим чат в браузер
function showChat(item) {
    divChat.innerHTML = `<h3 style="text-align: center;">Комната: ${item['MessageList']}</h3>
    <textarea class="textarea" name="textarea"></textarea><br>
    <input class="message_box" type="text" id="input_message" name="input_message" placeholder="Введите сообщение"><br>
    <button class="btn btn_message">Отправить</button>`;
    delete item.MessageList;
    let textarea = document.querySelector('.textarea');
   // currentRoomId = 9;
    for (let messageElement in item) {
        for (let key in item[messageElement]) {
            let newString = `${key}: ${item[messageElement][key]}\n`;
            textarea.value += newString;
        };
    };

    // Отправка сообщения
    document.querySelector('.btn_message').addEventListener('click', () => {
        let message = document.getElementById("input_message");
        if (message.value !== "") {
            socketForChat.send(JSON.stringify({'usersendcommandroom': 'message', 'room_id': currentRoomId, 'userid': userId, 'message': message.value}));
            console.log({'usersendcommandroom': 'message', 'room_id': currentRoomId, 'user': userId, 'message': message.value});
            message.value = "";
        };
    });

    // слушаем сокет и принимаем входящие сообщения от подключенной комнаты
    socketForChat.onmessage = function(event) {
        console.log(event.data);
        let data = JSON.parse(event.data);
        console.log(data);
        textarea.value += `${data['name']}: ${data['message']}\n`;
    };
};
