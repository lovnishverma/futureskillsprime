# FutureSkills PRIME - NIELIT Chandigarh

**Demo:** https://www.lovnishverma.in/futureskillsprime/

**Live:** https://futureskillsprime.onrender.com/

A responsive, single-page web application designed for the FutureSkills PRIME initiative at NIELIT Chandigarh. This landing page serves as a central hub for discovering upcoming courses, viewing distinguished speakers, browsing alumni batches, and submitting program nominations.

## Features

*   **Modern, Responsive UI:** Built with a mobile-first approach, featuring a collapsible mobile menu and sticky glass-morphism navigation bar.
*   **Dynamic Hero Carousel:** Auto-advancing image slider with manual dot/arrow navigation to highlight key programs.
*   **Data-Driven Content:** Courses, speakers, and alumni data are separated from the HTML structure using JavaScript objects, making it incredibly easy to update content without touching the UI layout.
*   **Interactive Course Modules:** Expandable accordion-style course cards detailing daily theory and practical lab schedules.
*   **Multi-Level Alumni Dropdown:** Categorized by track (BDDS, ARVR), level, and batch, dynamically generating links to specific batch pages.
*   **Integrated Nomination Form:** A comprehensive registration form with conditional logic (e.g., hiding education/experience fields for Bootcamps) that seamlessly submits data to a Google Sheets backend via Apps Script.
*   **Custom 404 Page:** A branded, cohesive error page (`404.html`) guiding users safely back to the main site.

## 📁 File Structure

```text
├── index.html       # Main landing page (Home, Courses, Speakers, Form)
├── 404.html         # Custom error page for broken links
└── README.md        # Project documentation

```

## 🛠️ Technologies Used

* **HTML5:** Semantic markup and structure.
* **CSS3 (Vanilla):** Custom CSS variables (`:root`), flexbox, CSS grid, scroll-behavior, and keyframe animations. No external CSS frameworks were used, ensuring a lightweight footprint.
* **JavaScript (Vanilla):** DOM manipulation, event listeners, dynamic HTML rendering, and asynchronous form submission (`Fetch API`).

## 💻 Local Setup & Installation

Since this project uses entirely vanilla frontend technologies with no build steps or dependencies, setup is instantaneous:

1. Clone or download the repository to your local machine.
2. Open `index.html` directly in any modern web browser.
3. *Optional:* For the best development experience, use a local server like the **Live Server** extension in VS Code to test the form submission and routing.

## ⚙️ Configuration & Content Management

To update the content on the website, scroll to the `<script>` tag at the bottom of `index.html`. You can modify the following JavaScript arrays/objects:

### 1. Updating Courses

Add or edit objects in the `courses` array. The UI will automatically generate the accordion cards.

```javascript
{
  course: 7,
  title: "New Course Title",
  objective: "Course objective description.",
  speakers: ["Speaker 1", "Speaker 2"],
  days: [ ... ] // Add daily modules here
}

```

### 2. Updating Speakers

Add new speaker profiles to the `speakers` array. The grid will automatically adjust.

```javascript
{ 
  name: "New Speaker", 
  role: "Designation", 
  institution: "NIELIT", 
  topic: "Topic Name", 
  bio: "Short biography." 
}

```

### 3. Google Form Webhook

The nomination form currently submits to a Google Apps Script deployment. To link this to your own Google Sheet:

1. Create a Google Sheet and attach an Apps Script.
2. Deploy the script as a Web App.
3. Replace the `WEB_APP_URL` variable in `index.html` with your new deployment link:

```javascript
const WEB_APP_URL = "YOUR_NEW_GOOGLE_APPS_SCRIPT_URL";

```

## 👨‍💻 Author & Maintainer

**Lovnish Verma**

Project Engineer, AI/ML

NIELIT Chandigarh / Ropar

*An Initiative by the Ministry of Electronics and Information Technology (MeitY), Government of India.*

