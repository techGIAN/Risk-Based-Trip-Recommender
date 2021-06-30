window.onload = setListeners;

setTimeout(function(){  }, 4000);
var paths =  document.getElementsByTagName("path");
var current_path = 0; // from values 0 to n-1

function setListeners () {
    console.log('paths = '+paths.length)

    for (let i = 0; i < paths.length; i++) {
        paths[i].addEventListener('click', event => {
            // console.log("event listener with i = " + i);
            // console.log("\twith opacity " + paths[i].getAttribute('stroke-opacity'));

            current_path = i;
            paths[i].setAttribute("stroke-opacity", 1);

            var j;

            // console.log('paths = '+paths.length)
            // console.log('current path = ' + current_path)
            // console.log("event listener with i = " + i + " with opacity " + paths[i].getAttribute('stroke-opacity'));

            for (j = 0; j < paths.length; j ++){
                if (j != current_path)
                    paths[j].setAttribute("stroke-opacity", 0.3);
            }
        });
    }
}