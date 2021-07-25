window.onload = setListeners;

setTimeout(function(){  }, 4000);
var paths =  document.getElementsByTagName("path");
var current_path = 0; // from values 0 to n-1

function setListeners () {
    console.log('paths = '+paths.length)

    for (let i = 0; i < paths.length; i++) {
        paths[i].addEventListener('click', event => {

            current_path = i;
            paths[i].setAttribute("stroke-opacity", 1);

            var j;

            for (j = 0; j < paths.length; j ++){
                if (j != current_path)
                    paths[j].setAttribute("stroke-opacity", 0.3);
            }
        });
    }
}

