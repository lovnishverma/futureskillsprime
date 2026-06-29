# FutureSkills PRIME - NIELIT Chandigarh Nomination System

A complete web-based nomination and registration portal developed for the **FutureSkills PRIME** initiative by **NIELIT Chandigarh**. The platform allows government officials and participants to register for emerging technology training programs (such as Big Data & Data Science and AR/VR), seamlessly generating standardized PDF and DOCX nomination forms from their submissions.

## Features

- **Dynamic Landing Page**: Detailed information on courses, speakers, and the FutureSkills PRIME program.
- **Dynamic Course Scheduling**: Administrators can dynamically configure multiple simultaneous batches for courses with custom start/end dates via the `/admin/dates` panel.
- **Smart Form Guidance**: The public nomination form features an "Ongoing Courses" banner and intelligently prevents users from selecting course batches that are not currently active.
- **Cohort WhatsApp Integration**: Participants are automatically provided with the exact WhatsApp group link corresponding to their uniquely selected course batch upon successful submission.
- **Online Nomination Form**: Interactive, multi-step form to collect participant details, educational qualifications, professional experience, and Institute details. Features an integrated **Signature Pad** canvas for Bootcamp applicants, allowing them to draw their signature via mouse/touch or upload an image directly during submission.
- **100% Cloud-Native Document Storage**: Secure handling of dynamically generated PDFs and images. All final generated nomination PDFs and captured signatures/photos are uploaded directly to **Cloudinary**, making the application entirely stateless and resilient to ephemeral server restarts.
- **Automated Document Generation**: Automatically injects form data into an official DOCX template and generates a polished, 1-page print-ready PDF using ReportLab that perfectly mimics the official grid layout. Form formatting mathematically scales user-uploaded signatures to precisely fit document constraints without layout spillovers.
- **Automated Email Notifications**: Automatically dispatches confirmation emails, follow-ups, and generated PDF attachments directly to participants using a custom **Google Apps Script HTTP API** to securely bypass cloud server SMTP blocks.
- **Participant Dashboard & Search**: Generates a unique tracking token for each submission. Participants can search via Aadhar, Phone, Email, or Token. The system intelligently retrieves **multiple applications** if a user has applied for more than one track, presenting them in a consolidated dashboard where they can preview and download their DOCX and PDF documents.
- **Advanced Admin Portal**: A secure dashboard (`/admin`) powered by DataTables that allows administrators to:
  - Instantly Search, Sort, and Paginate through all submitted nominations.
  - Manage **Course Dates** and WhatsApp Links.
  - Export all data to a CSV file.
  - **Download All PDFs (ZIP)**: Generates and packages every individual PDF submission into a downloadable `.zip` archive.
  - **Download All DOCXs (ZIP)**: Generates and packages every editable DOCX submission into a downloadable `.zip` archive.
  - Generate a bulk all-in-one merged PDF containing all submitted nominations.
  - Safely **Delete All Nominations** with strict confirmation locks, or delete individual entries.

## Tech Stack

- **Backend**: Python, Flask, `requests` (for HTTP API interactions)
- **Database**: MongoDB (via `pymongo`)
- **Cloud Storage**: Cloudinary (for secure storage of photos and signatures)
- **Document Processing**: `python-docx` (for Word documents), `reportlab` & `pypdf` (for PDF generation), `zipfile` (for bulk archives)
- **Image Processing**: `Pillow` (PIL) for intelligent aspect-ratio constraint resizing
- **Frontend**: HTML5, Vanilla JavaScript, CSS3 (Custom responsive design with modern styling), jQuery + DataTables (Admin Panel), `signature_pad` (Digital Signature Capture)

## Directory Structure

```text
.
├── .env                        # Environment variables (Create this file locally)
├── app.py                      # Main Flask application and routes
├── requirements.txt            # Python dependencies for deployment
├── docxtemplates/              
│   ├── GOT_Nomination_Form.docx      # Base Word template for GOT documents
│   └── Bootcamp_Nomination_Form.docx # Base Word template for Bootcamp documents
├── static/                     # Static assets (CSS, images)
├── templates/
│   ├── index.html              # Main landing page and nomination form
│   ├── success.html            # Success page with PDF/DOCX download links
│   ├── search.html             # Multi-record search dashboard for applicants
│   ├── admin_login.html        # Admin authentication page
│   └── admin.html              # Admin dashboard with DataTables
└── README.md                   # Project documentation
```

## Local Setup & Installation

### 1. Prerequisites

Ensure you have **Python 3.10+** installed. You will also need access to a MongoDB cluster (like MongoDB Atlas) and a Cloudinary account.

### 2. Install Dependencies

Install the required Python packages using pip:

```bash
pip install -r requirements.txt
```

### 3. Environment Variables

Create a `.env` file in the root directory and configure it with your credentials:

```env
FLASK_SECRET_KEY=your_secret_key_here
ADMIN_PASSWORD=nielit@admin
CLOUDINARY_API_KEY=your_cloudinary_api_key
CLOUDINARY_API_SECRET=your_cloudinary_api_secret
MONGO_URI=your_mongo_connection_string
SENDER_EMAIL=your_email@gmail.com
```

### 4. Running the Application

Run the application locally using Python:

```bash
python app.py
```

The application will start on `http://127.0.0.1:5000/`. 
- The public nomination form is available at `/`
- The admin dashboard is available at `/admin`

## Deploying on Render

To deploy this Flask application live to the internet using [Render.com](https://render.com), follow these steps:

### 1. Prepare your Repository
Make sure all your files (including `requirements.txt`) are pushed to a GitHub, GitLab, or Bitbucket repository.

### 2. Create a Web Service on Render
1. Log in to Render and click **New +** > **Web Service**.
2. Connect your GitHub/GitLab repository.
3. Configure the following settings:
   - **Name**: `futureskillsprime`
   - **Environment**: `Python`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn app:app`

### 3. Set Environment Variables
In the Render dashboard under your Web Service settings, go to the **Environment** tab and add the variables from your `.env` file:
- `FLASK_SECRET_KEY` (Set a strong random string)
- `ADMIN_PASSWORD`
- `CLOUDINARY_API_KEY`
- `CLOUDINARY_API_SECRET`
- `MONGO_URI`
- `SENDER_EMAIL`

### 4. Deploy
Click **Deploy**. Render will automatically build your environment, install the dependencies, and launch your Flask app using `gunicorn`. Once the deployment is live, your application will be accessible via a `*.onrender.com` URL.

## License

&copy; 2026 NIELIT Chandigarh &mdash; FutureSkills PRIME. All rights reserved. 
An Initiative by Ministry of Electronics and Information Technology (MeitY), Government of India.
