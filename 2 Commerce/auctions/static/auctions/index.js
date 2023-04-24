document.addEventListener("DOMContentLoaded", function() {
    const listing_items = document.querySelectorAll(".div-listing-item");

    for (let i = 0; i < listing_items.length; i++) {
        listing_items[i].addEventListener("click", listing_item_clicked)
    }
});

function listing_item_clicked (e) {
    let target = e.target;
    if (target.tagName != "DIV") target = target.parentNode;

    window.location.href = `listing?l=${target.dataset.id}`

}