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
  try {
    // Take inputs
    const i_subject = document.querySelector("#compose-subject").value;
    const i_recipients = document.querySelector("#compose-recipients").value;
    const i_body = document.querySelector("#compose-body").value;

    // Check inputs
    // if any needed infos blank -> throw error
    if (i_subject.length < 1 || i_recipients.length < 1 || i_body.length < 1) {
      throw "Error. Missing information!";
    }

    const ii_recipients = i_recipients.split(",");
    // If no err  -> send data to API
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
    alert(err);
    console.log(err);
  }
}

function compose_email(isReply, subject, recipient) {

  // Show compose view and hide other views
  document.querySelector('#emails-view').style.display = 'none';
  document.querySelector('#compose-view').style.display = 'block';
  document.querySelector('#email-view').style.display = 'none';

  // Clear out composition fields
  document.querySelector('#compose-recipients').value = '';
  document.querySelector('#compose-subject').value = '';
  document.querySelector('#compose-body').value = '';

  if (isReply) {
    const recipientInput = document.querySelector('#compose-recipients');
    recipientInput.value = recipient;
    recipientInput.readOnly = true;
    document.querySelector('#compose-subject').value = `Reply to: "${subject}"`;
    document.querySelector('#compose-body').focus();
  }
}

function load_mail(mail_id) {
  // Show the mailbox and hide other views
  document.querySelector('#emails-view').style.display = 'none';
  document.querySelector('#compose-view').style.display = 'none';
  document.querySelector('#email-view').style.display = '';

  // Get mail informations
  // Write mail informations
  try {
    fetch(`/emails/${mail_id}`).then(response => response.json()).then(email => {
    // Print email
    console.log(email);
    
    let recipientsHtml = "";
    for (let i = 0; i < email.recipients.length; i++) {
      recipientsHtml += email.recipients[i];
      if (i < email.recipients.length - 1) recipientsHtml += "; ";
    }
    
    // Mark email as read
    fetch(`/emails/${mail_id}`, {
      method: 'PUT',
      body: JSON.stringify({
          read: true
      })
    });

    // Reply and Archive Buttons
    const isReceived = email.sender != userName ? true : false;

    let replyButtonHtml = "";
    let archiveButtonHtml = "";
    if (isReceived) {
      archiveButtonHtml = `<button id="button-archive">${email.archived ? "Unarchive": "Archive"}</button>`;
      replyButtonHtml = `<button id="button-reply">Reply</button>`;
    }
    
    const emailHtml = `
      <div id="email-view-in">
        <div>
          ${replyButtonHtml}
          ${archiveButtonHtml}
        </div>
        <div><div>Sender:</div><div id="div-sender">${email.sender}</div></div>
        <div><div>Recipients:</div><div id="div-recipients">${recipientsHtml}</div></div>
        <div><div>Subject:</div><div id="div-subject">${email.subject}</div></div>
        <div><div>Sent:</div><div id="div-timestamp">${email.timestamp}</div></div>
        <div><div>Message:</div><div id="div-body">${email.body}</div></div>
      </div>
    `;
    
    // Write html text to email view
    document.querySelector("#email-view").innerHTML = emailHtml;

    if (isReceived) {
      // Archive button eventListener
      document.querySelector("#button-archive").addEventListener("click", function (event) {
        console.log("bakalım", event.target.innerHTML);
        toggleArchive(event.target.innerHTML, email.id);
  
        event.preventDefault();
      });

      // Reply button eventListener
      document.querySelector("#button-reply").addEventListener("click", function (event) {
        compose_email(true, email.subject , email.sender);
        event.preventDefault();
      });
    }
    
});         
  } catch (err) {
    console.log("Error. ", err);
  }
}

// Archive button archive or unarchive then, load inbox or archive page
function toggleArchive(toggle, email_id) {
  fetch(`/emails/${email_id}`, {
    method: 'PUT',
    body: JSON.stringify({
        archived: (toggle === "Unarchive" ? false : true)
    })
  }).then(r => load_mailbox(toggle === "Unarchive" ? "inbox" : "archive"));
}

function load_mailbox(mailbox) {
  
  // Show the mailbox and hide other views
  document.querySelector('#emails-view').style.display = 'block';
  document.querySelector('#compose-view').style.display = 'none';
  document.querySelector('#email-view').style.display = 'none';

  // Show the mailbox name
  document.querySelector('#emails-view').innerHTML = `<h3>${mailbox.charAt(0).toUpperCase() + mailbox.slice(1)}</h3>`;

  // Get emails by mailbox

  fetch(`/emails/${mailbox}`).then(response => response.json()).then(emails => {
    
    // Mailbox header
    htmlMails = `<h3>${mailbox.charAt(0).toUpperCase() + mailbox.slice(1)}</h3>`;

    // If no email in mailbox, inform user
    if(emails.length < 1) {
      htmlMails += `No email in ${mailbox} yet.`;
    }

    // Email listing
    for (let i = 0; i < emails.length; i++) {
      let email = emails[i]
      htmlMails += `
        <div data-id="${email.id}" class="div-email-main${email.read ? ' read' : ''}">
          <div>${email.subject}</div>
          <div>${email.recipients[0]}</div>
          <div>${email.timestamp}</div>
        </div>
      `;
    }
    
    // Insert html to view
    document.querySelector("#emails-view").innerHTML = htmlMails;
    
    // Add event listeners to email elements
    email_elements = document.querySelectorAll(".div-email-main");

    for (let i=0; i<email_elements.length; i++) {
      element = email_elements[i];
      let m_target;
      element.addEventListener("click", function(event) {
        if (event.target.classList.contains("div-email-main")) m_target = event.target;
        else m_target = event.target.parentElement;
        
        email_id = m_target.dataset.id;

        load_mail(email_id);
      })
    }

  }).catch(err => {
    console.log(`Error while fetching: ${err}`);
  });
}