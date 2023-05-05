document.addEventListener("DOMContentLoaded", function () {

    // Event listener for fallow/unfallow button

    const fallowButton = document.querySelector(".a-user-fallow");

    if (fallowButton) {
        fallowButton.addEventListener("click", fallow_clicked);
    }
});

function fallow_clicked (e) {
    // Get user id
    const userId = e.target.dataset.fallowing;
    // Send api the user id for toggle

     // Make query for db update
    fetch(`/edit-fallow/${userId}`, {
        method: 'PUT'
    }).then(response => {
    if (response.status === 204) {
        // Edit ended succesfully
        window.location.href =  window.location.href;
    }
    else {
        console.log("API error.");
    }
    }).catch(err => console.log(err));

    // If result successfull change the fallowing situation or renew page
    e.preventDefault();
}