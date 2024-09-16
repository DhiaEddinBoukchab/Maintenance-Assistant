***Maintenance Assistant***

Maintenance Assistant is a Streamlit web application that allows users to ask questions related to maintenance documents (in PDF format) and get responses based on the content of the document.

**Features**
Upload a PDF file containing maintenance information.
Ask questions related to the content of the PDF.
Get responses based on the document content.
View chat history for previous questions and answers.

**Prerequisites**
Docker installed on your machine.
An OpenAI API key to enable the language model features.

**Setup Guide**
### 1. Clone the Repository
First, clone the repository to your local machine:

git clone https://github.com/s-bessaies/maintenance.git
cd dhia
cd docker

### 2. Add Environment Variables
Create a .env file in the root of the project and add your OpenAI API key:


### 3. Build the Docker Image

docker-compose  build  

### 4. Run the Docker Container
 docker-compose up


### 5. Access the Application

http://localhost:8500