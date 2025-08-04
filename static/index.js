function checkS(){
    if ({{ logged }}){
        alert('logged in as '+{{ user }})
    } else{
        alert('please sign in')
    }
}
window.onload = checkS();