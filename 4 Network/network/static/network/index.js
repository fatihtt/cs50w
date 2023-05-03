document.addEventListener("DOMContentLoaded", function () {
    // Even listener for new post button
    const newPostButton = document.querySelector("#input-newpost-submit");
    newPostButton.addEventListener("click", newPost);
});

function newPost (e) {
    try {
        // Take inputs
        const title = document.querySelector("#input-newpost-title").value;
        const text = document.querySelector("#input-newpost-text").value;
        
        // Check inputs
        if (title.length < 1 || text.length < 1) throw "No title or text";

        // Add new post
        fetch("new-post", {
            method: "POST",
            body: JSON.stringify({
                title: title,
                text: text
            })
        }).then(response => {
            if (response.status === 201) window.location.href = "./";
            else throw `Server side error.`;
        }).then(result => {
            // API newpost result
            window.location.href = "./";
        }).catch(err => {
            console.log("Error while adding post!");
            console.log(err);
            alert(err);
        })
    } catch (err) {
        console.log("Error while adding post!");
        console.log(err);
        alert(err);
    }
    e.preventDefault();
}