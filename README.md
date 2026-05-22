# FutureSkills PRIME - NIELIT Chandigarh Nomination System

A complete web-based nomination and registration portal developed for the **FutureSkills PRIME** initiative by **NIELIT Chandigarh**. The platform allows government officials and participants to register for emerging technology training programs (such as Big Data & Data Science and AR/VR), seamlessly generating standardized PDF and DOCX nomination forms from their submissions.

## Features

- **Dynamic Landing Page**: Detailed information on courses, speakers, and the FutureSkills PRIME program.
- **Online Nomination Form**: Interactive, multi-step form to collect participant details, educational qualifications, and professional experience.
- **100% Cloud-Native File Storage**: Secure handling of passport photos, signatures, and dynamically generated PDFs. All files are uploaded directly to **Cloudinary**, making the application entirely stateless and resilient to ephemeral server restarts.
- **Automated Document Generation**: Automatically injects form data into an official DOCX template and generates a polished, print-ready PDF using ReportLab.
- **Participant Dashboard**: Generates a unique tracking token for each submission and allows the user to immediately download their filled DOCX and PDF documents.
- **Admin Portal**: A secure dashboard (`/admin`) that allows administrators to:
  - View all submitted nominations.
  - Export all data to a CSV file.
  - Generate a bulk all-in-one PDF containing all submitted nominations.
  - Download individual PDFs or delete entries.

## Tech Stack

- **Backend**: Python, Flask
- **Database**: MongoDB (via `pymongo`)
- **Cloud Storage**: Cloudinary (for secure storage of photos, signatures, and PDFs)
- **Document Processing**: `python-docx` (for Word documents), `reportlab` & `pypdf` (for PDF generation)
- **Image Processing**: `Pillow` (PIL)
- **Frontend**: HTML5, Vanilla JavaScript, CSS3 (Custom responsive design with modern styling)

## Directory Structure

```text
.
├── .env                        # Environment variables (Create this file locally)
├── app.py                      # Main Flask application and routes
├── requirements.txt            # Python dependencies for deployment
├── docxtemplates/              
│   └── GOT_Nomination_Form.docx # Base Word template for generating documents
├── static/                 # Static assets (CSS, images)
├── templates/
│   ├── index.html              # Main landing page and nomination form
│   ├── success.html            # Success page with PDF/DOCX download links
│   ├── admin_login.html        # Admin authentication page
│   └── admin.html              # Admin dashboard
└── README.md                   # Project documentation
```

## Local Setup & Installation

### 1. Prerequisites

Ensure you have **Python 3.8+** installed. You will also need access to a MongoDB cluster (like MongoDB Atlas) and a Cloudinary account.

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
# Optional: PORT=5000
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
   - **Name**: `nielit-nominations` (or your preferred name)
   - **Environment**: `Python`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn app:app`

### 3. Set Environment Variables
In the Render dashboard under your Web Service settings, go to the **Environment** tab and add the variables from your `.env` file:
- `FLASK_SECRET_KEY` (Set a strong random string)
- `ADMIN_PASSWORD`
- `CLOUDINARY_API_KEY`
- `CLOUDINARY_API_SECRET`

### 4. Deploy
Click **Deploy**. Render will automatically build your environment, install the dependencies, and launch your Flask app using `gunicorn`. Once the deployment is live, your application will be accessible via a `*.onrender.com` URL.

## Usage

1. **Submit a Nomination**: Visit the homepage, scroll to the Nomination section, fill out all required details including uploading a photo and signature, and click Submit.
2. **Download Documents**: Upon successful submission, you will receive a unique tracking token. Use the provided buttons to download your finalized PDF or DOCX form.
3. **Admin Actions**: Navigate to `/admin` and log in (default password: `nielit@admin`). From here, you can view all applicants, export data to CSV, or download a bulk PDF of all nominations.

## License

&copy; 2026 NIELIT Chandigarh &mdash; FutureSkills PRIME. All rights reserved. 
An Initiative by Ministry of Electronics and Information Technology (MeitY), Government of India.
