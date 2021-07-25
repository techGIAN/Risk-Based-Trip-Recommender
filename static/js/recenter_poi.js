function recenter_poi(center){
    const xhr = new XMLHttpRequest();

    method = "GET";
    url = 'http://127.0.0.1:5000/recenter?center=[' + center + ']';

    console.log('url = ' + url);
    window.top.location.href = url;
}