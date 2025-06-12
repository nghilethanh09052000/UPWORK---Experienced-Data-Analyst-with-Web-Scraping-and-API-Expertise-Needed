import requests

# Actual content URL (from `links.document`)
document_content_url = "https://document-api.company-information.service.gov.uk/document/hIgBkq_0mJF4l8olza1REqzZwtGmS43eCLZ7oyhOosw/content"

# Your API key
API_KEY = "b2aec4fb-1d43-4b79-9a59-0aedb50e2225"

# Send GET request to the content URL with authentication
response = requests.get(document_content_url, auth=(API_KEY, ''))

# Check for success
if response.status_code == 200:
    with open("document.pdf", "wb") as f:
        f.write(response.content)
    print("✅ PDF downloaded successfully as 'document.pdf'")
else:
    print(f"❌ Failed to download PDF: {response.status_code} - {response.text}")
