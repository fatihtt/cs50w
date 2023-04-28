document.addEventListener('DOMContentLoaded', function() {

  // Use buttons to toggle between views
  document.querySelector('#inbox').addEventListener('click', () => load_mailbox('inbox'));
  document.querySelector('#sent').addEventListener('click', () => load_mailbox('sent'));
  document.querySelector('#archived').addEventListener('click', () => load_mailbox('archive'));
  document.querySelector('#compose').addEventListener('click', compose_email);

  // Other event listeners
  document.querySelector("#send-mail").addEventListener('click', function(event){
    send_mail(event);
    event.preventDefault();
  });

  // By default, load the inbox
  load_mailbox('inbox');
});

function send_mail(e) {
  // Take inputs
  // Check inputs
  // If no err  -> send data to API
  // Else       -> show err
  // If no err  -> show send box
  // Else       -> show err
  try {
    const i_subject = document.querySelector("#compose-subject").value;
    const i_recipients = document.querySelector("#compose-recipients").value;
    const i_body = document.querySelector("#compose-body").value;

    // if any needed infos blank -> throw error
    if (i_subject.length < 1 || i_recipients.length < 1 || i_body.length < 1) {
      throw "Error. Missing information!";
    }

    const ii_recipients = i_recipients.split(",");
    
    // Send to API
    fetch('/emails', {
      method: 'POST',
      body: JSON.stringify({
          recipients: i_recipients,
          subject: i_subject,
          body: i_body
      })
    })
    .then(response => response.json())
    .then(result => {
        // Result

        // If error -> alert
        if (result.error) throw result.error;

        // If successful message received, go to sent box
        if (result.message && result.message === "Email sent successfully.") {
          load_mailbox('sent')
        }

    }).catch(error => {

      console.log("Error in Promise: ", error);
      alert(error);
    });
  } catch (err) {

    console.log("Error", err);
  }
}

function compose_email() {

  // Show compose view and hide other views
  document.querySelector('#emails-view').style.display = 'none';
  document.querySelector('#compose-view').style.display = 'block';

  // Clear out composition fields
  document.querySelector('#compose-recipients').value = '';
  document.querySelector('#compose-subject').value = '';
  document.querySelector('#compose-body').value = '';
}

function load_mailbox(mailbox) {
  
  // Show the mailbox and hide other views
  document.querySelector('#emails-view').style.display = 'block';
  document.querySelector('#compose-view').style.display = 'none';

  // Show the mailbox name
  document.querySelector('#emails-view').innerHTML = `<h3>${mailbox.charAt(0).toUpperCase() + mailbox.slice(1)}</h3>`;
}