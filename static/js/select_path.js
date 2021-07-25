function selectRoute(number){
    const xhr = new XMLHttpRequest();

    method = "GET";
    url = 'http://127.0.0.1:5000/select_path?path_num=' + number ;

    console.log('url = ' + url);
    window.top.location.href = url;
}