console.log("fetching.js loaded");
setInterval(() => {
    console.log("interval loaded");
    fetch("/")
			.then(res => res.text())
			.then(html => { 
                const parser = new DOMParser();
                const newDoc = parser.parseFromString(html, "text/html");
                document.getElementById("body").innerHTML = newDoc.getElementById("body").innerHTML;        
            });
        } , 4000); 