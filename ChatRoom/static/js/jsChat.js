const divProfil = document.querySelector('.div_profil');
const domain = ('http://127.0.0.1:8000/api/');
const user_id = window.userID;

// формируем случайный номер для WS для возможности одновременного открытия на разных вкладках
let sockNum =  Math.floor(Math.random() * 100 + 1);


const socket = new WebSocket('ws://localhost:8000/ws/command/' + sockNum); // командный канал
socket.onclose = async (event) => {
    console.error(event);
    window.alert('запустите сервер и обновите страницу!');
};

socket.onopen = () => load_userCard();
function load_userCard() {
    viewProfil(user_id);
};

socket.onmessage = function(event) {
    let data = JSON.parse(event.data);
    console.log(data);

    if ('message' in data) {

    };


};

// Запрос данных пользователя
function viewProfil(userId) {
    console.log(userId);
    fetch(domain + 'user/' + userId +'/')
        .catch(err => console.log(err))
        .then(response => response.json())
        .then(result => showProfile(result));
};

// Вывод профиля в браузер
function showProfile(item) {
    console.log(item);
    divProfil.innerHTML = `
    <div class="div_profil">
        <img class="img_avatar" src="${item.avatar}">
        <br>
        <strong>Сменить аватарку:</strong><br>
        <input id="avatar-input" type="file" accept="image/*"><br>
        <button onclick="changeAvatar(${item.user})">отправить</button>
        <p>ID: ${item.user}</p>
        <p>Имя: ${item.first_name} <button onclick="changeFirstName(${item.user})">изменить</button></p>
        <h4 class="message" id="message"></h4>
    </div>
    `;
};

// замена аватара
async function changeAvatar(user_id) {
    const formData = new FormData();
    let fileField = document.querySelector('#avatar-input');
    if (fileField.files[0]) {
        formData.append('avatar', fileField.files[0]);
        try {
            const response = await fetch(domain + 'user/' + user_id +'/', {
                method: 'PATCH',
                body: formData
            });
            const result = await response.json();
            console.log('Результат сохранения:', JSON.stringify(result));
        } catch (error) {
            console.log('Все пропало!!!');
            console.error('Ошибка:', error);
        }
        viewProfil(user_id);
    } else {
        document.querySelector('#message').innerText = 'выберите файл!';
    };
};

//замена имени
function changeFirstName(user_id) {
    let name = prompt('Введите новое имя');
    socket.send(JSON.stringify({'order': 'changeFirstName', 'id': user_id, 'name': name }));
    console.log({'order': 'changeFirstName', 'id': user_id, 'name': name })
    viewProfil(user_id);
};
