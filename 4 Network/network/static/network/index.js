document.addEventListener("DOMContentLoaded", function () {
    // Event listener for new post button
    const newPostButton = document.querySelector("#input-newpost-submit");
    if (newPostButton) newPostButton.addEventListener("click", newPost);

    // eventListener for edit buttons
    const editButtonsList = document.querySelectorAll(".a-post-edit");
    for (let i = 0; i < editButtonsList.length; i++) {
        m_button = editButtonsList[i];
        m_button.addEventListener("click", edit_post);
    }

    // eventListener for Like buttons
    const likeButtonsList = document.querySelectorAll(".favorite");
    for (let i = 0; i < likeButtonsList.length; i++) {
        m_button = likeButtonsList[i];
        m_button.addEventListener("click", toggle_like)

    }
});

function toggle_like (e) {
    try {
        // Get post id
        postId = e.target.dataset.postid;

        // Check post id
        if (!postId || postId < 1) throw "Missing or wrong postId";

        // Make query for db update
        fetch(`/favorite-toggle-post/${postId}`, {
            method: 'PUT',
            body: JSON.stringify({
                favorite: e.target.innerText
            })
        }).then(response => {
            if (response.status === 204) {
                // Edit ended succesfully
                e.target.classList.toggle("red");

                // Toggle favorite sign and counter
                const counterElement = e.target.parentElement.querySelector(".post-like-counter");
                if (e.target.innerText === "favorite") {
                    e.target.innerText = "favorite_border";
                    counterElement.innerText = parseInt(counterElement.innerText) - 1;
                }
                else {
                    e.target.innerText = "favorite";
                    counterElement.innerText = parseInt(counterElement.innerText) + 1;
                }
            }
            else {
                throw "error while editing";
            }
        }).catch(err => console.log("Server error. ", err));

    } catch (err) {
        console.log("Js Error: ", err);
    }
}

function edit_post (e) {
    try {
        // Get post id
        postId = e.target.dataset.postid;
        
        // Check post id
        if (!postId || postId < 1) throw "Missing or wrong postId";

        // Show / hide edit form
        const editDiv = e.target.parentElement.querySelector(".div-edit-post");
        if (editDiv.classList.contains("hidden")) editDiv.classList.remove("hidden");
        else editDiv.classList.add("hidden");
        
        // Add event listener for edit button
        editDiv.querySelector(".button-edit-post").addEventListener("click", edit_post_click);
    } catch (err) {
        console.log("Js Error: ", err);
    }

    e.preventDefault();
}

function edit_post_click (e) {
    try {
        // Get post id
        const postId = e.target.dataset.postid;

        // Check postId
        if (!postId || postId < 1) throw "Missing or wrong postId";

        const editDiv = e.target.parentElement;
        // Get edited text
        const editedText = editDiv.querySelector(`#textarea-edit-post${ postId }`).value;

        // Check edited text
        if (!editedText || editedText.length < 1) throw "Missing or wrong text";

        // Make query for db update

        fetch(`/edit-post/${postId}`, {
            method: 'PUT',
            body: JSON.stringify({
                text: editedText
            })
          }).then(response => {
            console.log("response status ", response.status);
            if (response.status === 204) {
                // Edit ended succesfully

                const postDiv = editDiv.parentElement;
                postDiv.querySelector(".div-edit-post").classList.add("hidden");
                postDiv.querySelector(".post-text").innerHTML = editedText;
            }
            else {
                throw "error while editing";
            }
          }).catch(err => console.log("Server error. ", err));
    } catch (err) {
        alert(`Program error: ${err}`);
        console.log(`Js error. ${err}`);
    }
    e.preventDefault();
}

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