document.addEventListener("DOMContentLoaded", function () {
    // Even listener for new post button
    const newPostButton = document.querySelector("#input-newpost-submit");
    newPostButton.addEventListener("click", newPost);
});

function newPost (e) {
    // Take inputs
    e.preventDefault();
}