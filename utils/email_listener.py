# Import necessary database classes
import imaplib
import logging
import os
import email
from datetime import datetime
from email.header import decode_header
from time import sleep
from utils.config import IMAP_SERVER, MAIL_USERNAME, MAIL_PASSWORD, attachments_dir, SEARCH_CRITERIA

# Set to store processed email IDs
processed_emails = set()


def connect_to_imap_server():
    """Connects to the IMAP server and handles potential exceptions."""
    try:
        mail = imaplib.IMAP4_SSL(IMAP_SERVER)
        mail.login(MAIL_USERNAME, MAIL_PASSWORD)
        return mail
    except imaplib.IMAP4_SSL.error as e:
        logging.error(f"Error connecting to IMAP server: {e}")
        return None


def extract_email_information(msg):
    """Extracts information from an email message."""
    subject = decode_header(msg["Subject"])[0][0]
    sender = decode_header(msg["From"])[0][0]
    receiver = decode_header(msg["To"])[0][0]
    date = msg["Date"]
    # Convert the date string to a datetime object
    date = datetime.strptime(date, "%a, %d %b %Y %H:%M:%S %z")
    # Assuming "type" and "project" are also extracted from the subject
    request_type = subject.split()[0]  # Modify if type location changes
    project = subject.split()[1]  # Modify if type location changes
    return subject, request_type, project, sender, receiver, date


def extract_email_contents(msg, num):
    """Extracts all body content and stores attachments."""
    body_parts = []
    attachments = []
    for part in msg.walk():
        content_type = part.get_content_type()
        content_disposition = str(part.get("Content-Disposition"))
        if content_type in ["text/plain", "text/html"]:
            try:
                body = part.get_payload(decode=True).decode("utf-8")
            except UnicodeDecodeError:
                try:
                    body = part.get_payload(decode=True).decode(part.get_content_charset())
                except (LookupError, UnicodeDecodeError) as e:
                    logging.error(f"Error decoding body: {e}")
                    body = ""
            body_parts.append(body)  # Append plain text parts
        elif content_disposition and "attachment" in content_disposition:
            filename = part.get_filename()
            if filename:
                decoded_filename = decode_filename(filename)
                if not os.path.exists(attachments_dir):
                    os.makedirs(attachments_dir)  # Create the attachments directory if it doesn't exist
                filepath = os.path.join(attachments_dir,
                                        os.path.splitext(decoded_filename)[0] + "_" + num.decode("utf-8") +
                                        os.path.splitext(decoded_filename)[1])
                with open(filepath, "wb") as f:
                    f.write(part.get_payload(decode=True))
                attachments.append(filepath)
    return body_parts, attachments


def decode_filename(filename):
    """Decode a filename string."""
    decoded_parts = decode_header(filename)
    decoded_filename = []
    for part, charset in decoded_parts:
        if isinstance(part, bytes):
            if charset:
                decoded_filename.append(part.decode(charset))
            else:
                decoded_filename.append(part.decode('utf-8'))
        else:
            decoded_filename.append(part)
    return ''.join(decoded_filename).replace(" ", "_")


def process_email(msg, num):
    """Processes a single email message and prints information."""
    subject, request_type, project, sender, receiver, date = extract_email_information(msg)
    body, attachments = extract_email_contents(msg, num)
    # Logging and printing information
    logging.info(f"Num: {num}")
    logging.info(f"Request Type: {request_type}")
    logging.info(f"Project: {project}")
    logging.info(f"Subject: {subject}")
    logging.info(f"From: {sender}")
    logging.info(f"To: {receiver}")
    logging.info(f"Date: {date}")
    logging.info("Body:")
    for part in body:
        logging.info(part)  # Print

    # Create and store Request object in the database
    # request = Request(
    #     num=num,
    #     type=type,
    #     subject=subject,
    #     sender=sender,
    #     receiver=receiver,
    #     date=date,
    #     body="\n".join(body),  # Join multiple body parts
    #     attachments=", ".join(attachments)  # Join attachment paths
    # )
    # db.session.add(request)
    # db.session.commit()

    # Logging and printing information
    logging.info(f"Processed email: {num}")
    # ... (other logging/printing)


def listen_for_new_emails():
    try:
        mail = connect_to_imap_server()
        mail.select("inbox")
        while True:
            status, messages = mail.search(None, SEARCH_CRITERIA)
            # ... (existing code and error handling)

            # Process new emails
            if messages[0]:
                for num in messages[0].split():
                    # Add check for processed emails if desired
                    if num not in processed_emails:
                        status, data = mail.fetch(num, "(RFC822)")
                        # Access the raw email data as bytes directly
                        raw_email = data[0][1]  # No need to decode here
                        msg = email.message_from_bytes(raw_email)
                        process_email(msg, num)  # Process the new email
                        processed_emails.add(num)  # Add email ID to processed set

            mail.noop()
            sleep(5 * 60)  # Check for new emails every 5 minutes
    except Exception as e:
        logging.error(f"Error listening for emails: {e}")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    listen_for_new_emails()
