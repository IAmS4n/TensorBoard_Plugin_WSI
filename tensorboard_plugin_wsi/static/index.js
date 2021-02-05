export async function render() {
    (function(){
    var libs = [
    'static/jquery.js',
    'static/openseadragon.js',
    'static/openseadragon-scalebar.js',
    'static/slide.js',
    ];

    var injectLibFromStack = function(){
      if(libs.length > 0){

            //grab the next item on the stack
            var nextLib = libs.shift();
            var headTag = document.getElementsByTagName('head')[0];

            //create a script tag with this library
            var scriptTag = document.createElement('script');
            scriptTag.src = nextLib;

            //when successful, inject the next script
            scriptTag.onload = function(e){
              console.log("---> loaded: " + e.target.src);
              injectLibFromStack();
            };

            //append the script tag to the <head></head>
            headTag.appendChild(scriptTag);
            console.log("injecting: " + nextLib);
          }
          else return;
      }

      //start script injection
      injectLibFromStack();
    })();

    const runToTags = await fetch('./tags').then((response) => response.json());
    const data = await Promise.all(
    Object.entries(runToTags).flatMap(([run, tagToDescription]) =>
      Object.keys(tagToDescription).map((tag) =>
        fetch('./slide_prop?' + new URLSearchParams({run, tag}))
          .then((response) => response.json())
          .then((slide_prop) => ({
            run,
            tag,
            slide_prop,
          }))
      )
    )
    );

    var ids = {};
    var mpps = {};
    function set_wsi_trigger(){
        const runtag = document.getElementById("select").value;
        console.log(runtag);
        set_wsi(ids[runtag], mpps[runtag]);
    };

    var select_list = document.createElement("select");
    select_list.addEventListener("change", set_wsi_trigger);
    select_list.style = 'width: 100%;';
    select_list.id = 'select';
    document.body.appendChild(select_list);

    for (const wsi of data) {
        var option = document.createElement("option");
        const runtag = wsi["run"].concat("_").concat(wsi["tag"]);
        option.text = runtag;
        ids[runtag] = wsi["slide_prop"]["id"];
        mpps[runtag] = wsi["slide_prop"]["mpp"];
        select_list.add(option);
    };

    var slide_div = document.createElement('div');
    slide_div.id = 'view';
    slide_div.style = 'position: absolute;left: 0;width: 100%;height: 90%;background-color: black;color: white;';
    document.body.appendChild(slide_div);

}