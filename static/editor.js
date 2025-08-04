const editor = ace.edit("editor");
editor.setTheme("ace/theme/monokai");
editor.session.setMode("ace/mode/html");
function loadCode(){
    
}
function run(){
    const dc = document.getElementById('output').contentDocument;
    dc.open()
    dc.write(editor.getValue())
    dc.close()
}
function save(){
    fetch("/addsite", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({
            "code":editor.getValue()
        })
    })
    .then(response => response.json())
    .then(data => {
        alert(data.message);
    })
    .catch(error => {
        alert('Failed to save: Try again or make a copy somewhere.');
    });
}
function del(){
    location.href = '/delete';
}
function clr(){
    editor.setValue("");
}
