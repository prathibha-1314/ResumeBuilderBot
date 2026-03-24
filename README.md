# ResumeBuilderBot 📄✨

**ResumeBuilderBot** is a Smart ATS-Friendly Resume Generator built with Python and Flask. It helps users quickly generate professional resumes and tailored cover letters by analyzing job descriptions and matching key skills.

## ✨ Features

- **User Authentication:** Secure sign-up, login, and session management.
- **Smart ATS Optimization:** Extracts keywords from the provided Job Description to ensure your resume gets past Applicant Tracking Systems.
- **Auto-Generated Cover Letters:** Dynamically creates a customized cover letter based on your top skills, the company name, and the job role you are applying for.
- **Three Unique Templates:** Choose between ATS-Friendly, Balanced, and Creative resume styles.
- **Profile Photo Support:** Easily upload and include a profile picture on your creative resumes.
- **Dashboard Management:** View, preview, and delete your previously generated resumes from your account dashboard.
- **Responsive Web Interface:** Built with clean HTML/CSS for an intuitive user experience.

## 🛠️ Technology Stack

- **Backend:** Python, Flask
- **Database:** SQLite
- **Security:** Werkzeug password hashing, Secure Uploads
- **Frontend:** HTML5, CSS3, Jinja2 Templates

## 🚀 Getting Started Locally

### Prerequisites
- Python 3.8+ installed on your system.

### Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/prathibha-1314/ResumeBuilderBot.git
   cd ResumeBuilderBot
   ```

2. **Create a virtual environment (optional but recommended):**
   ```bash
   python -m venv venv
   # On Windows
   venv\Scripts\activate
   # On Mac/Linux
   source venv/bin/activate
   ```

3. **Install the dependencies:**
   *(Assuming requirements.txt exists; if not, you just need Flask and Werkzeug)*
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the application:**
   ```bash
   python app.py
   ```
   *The database (`database.db`) will be automatically initialized on the first run.*

5. **Open your browser:**
   Navigate to https://myresumebuilder.pythonanywhere.com to view the app!

## 📂 Project Structure

- `app.py`: Main application logic, database helpers, and routing.
- `templates/`: Contains all the HTML pages (`login.html`, `create_resume.html`, `resume_preview.html`, etc.).
- `static/`: Contains static assets like `style.css` and the `uploads/` directory for user profile photos.
- `database.db`: SQLite database file for storing user and resume data.

## 🤝 Contributing

Contributions, issues, and feature requests are welcome! Feel free to check the issues page or submit a Pull Request if you'd like to improve the project.

## 📝 License

This project is licensed under the MIT License.
