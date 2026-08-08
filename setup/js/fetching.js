console.log("fetching.js loaded");
function refresh() 
{
    fetch("/")
			.then(res => { // mind that .then dont execute immediatly cuz , it wail unitl the request si ready 
                            if (! res.ok)
                                throw new Error("No Response");
                            return res.text();
                         }) 

			.then(html => { 
                const parser = new DOMParser();
                const newDoc = parser.parseFromString(html, "text/html");
                document.getElementById("body").innerHTML = newDoc.getElementById("body").innerHTML;        
            })
            .catch (err => {
                                console.error("Dashboard refresh failed:", err);
                              })
            .finally (() => {
                                setTimeout(refresh, 4000);
                            });
} 
refresh();