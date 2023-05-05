let list = document.querySelector('ul');
list.classList.add('hidden')
function func(e) {
    let list = document.querySelector('ul');
    e.name === 'menu' ? (e.name = "close", list.classList.add('hidden')) : (e.name = "menu", list.classList.remove('hidden'));
    
}


setTimeout( function myfunctionh() {
    console.log("Hello");
    let div = document.querySelector('#foo');
    div.classList.add('mytxt');
},5000);
