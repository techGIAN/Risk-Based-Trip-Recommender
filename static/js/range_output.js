window.onload = setTextInputs;

function setTextInputs(){
    document.getElementById('radius_text').innerText = document.getElementById('radius').value;
    document.getElementById('places_text').innerText = document.getElementById('K_poi').value;
    getTodaysDate();
}

function updateRadiusTextInput(val) {
    document.getElementById('radius_text').innerText=val;
}

function updatePlacesTextInput(val) {
    document.getElementById('places_text').innerText=val;
}

function getTodaysDate(){
    var today = new Date();
    var dd = today.getDate();
    var mm = today.getMonth()+1; //As January is 0.
    var yyyy = today.getFullYear();

    if(dd<10) dd='0'+dd;
    if(mm<10) mm='0'+mm;

    var HH = today.getHours();
    var min = today.getMinutes();

    if(HH<10) HH='0'+HH;
    if(min<10) min='0'+min;

    document.getElementById('date_time').min =  yyyy + '-' + mm + '-' + dd + 'T' + HH + ':' + min; //YYYY-MM-DDThh:mm
}

function select_query(type){
    const xhr = new XMLHttpRequest();

    method = "GET";
    url = 'http://127.0.0.1:5000/setType?type=' + type;

    xhr.open(method, url, true);

    xhr.setRequestHeader("Content-Type", "application/json");

    xhr.onreadystatechange = function () {
        // In local files, status is 0 upon success in Mozilla Firefox
        if(xhr.readyState === XMLHttpRequest.DONE) {
            var status = xhr.status;
            if (status === 0 || (status >= 200 && status < 400)) {
                // The request has been completed successfully
                console.log(xhr.responseText);
            } else {
                // Oh no! There has been an error with the request!
            }
        }
    };
    xhr.send();
}