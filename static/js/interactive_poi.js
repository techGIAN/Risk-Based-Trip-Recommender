function create_trip(query){
    const xhr = new XMLHttpRequest();

    method = "GET";
    url = 'http://127.0.0.1:5000/?' + query;

    console.log('url = ' + url);
    window.top.location.href = url;
}