const sound = name => {
    return new Audio(`/static/${name}.mp3`);
};

const errSnd = sound('error');
const openSnd = sound('open');

const clickHouse = e => {
    sound('button').play();
    socket.send(e.target.value);    
};

const msgHouse = e => {
    data = e.data.split(':');
    console.log(data);
    if (data.length == 2) {
        switch(data[0]) {
        case 'E':
            err(data[1]);
            break;
        case 'D':
            display(data[1]);
            break;
        case 'F':
            display("OPEN,");
            openSnd.play();
            document.querySelector('.body').classList.add('body-open');
            document.querySelector('.behind').classList.add('behind-visible');
            document.getElementById('text').innerHTML = data[1];
        }
    }
};

const err = (code, e = {}) => {
    if (!e.wasClean) {
        errSnd.currentTime = 0;
        errSnd.play();
        display('Err0' + code);
        if (code == '4')
            alert('Обрыв линии. Обновите страницу');
    }
};

const display = s => {
    const text = s.length > 5 ? s.slice(0, 5) : s;
    document.getElementById('display').textContent = text;
};

document.querySelectorAll('button')
    .forEach(button => button.addEventListener('mousedown', clickHouse));

const socket = new WebSocket(`${window.location.href.replace('http', 'ws')}ws`);

socket.onclose = e => err('4', e);
socket.onerror = e => err('4', e);
socket.onmessage = msgHouse;
