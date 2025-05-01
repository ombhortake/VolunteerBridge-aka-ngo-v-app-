# VolunteerBridge (NGO-Volunteer Connect)

[![Python Version](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/)
[![Framework](https://img.shields.io/badge/Framework-Flask-brightgreen.svg)](https://flask.palletsprojects.com/)
[![Frontend](https://img.shields.io/badge/Frontend-Bootstrap%205-purple.svg)](https://getbootstrap.com/)
[![Database](https://img.shields.io/badge/Database-SQLite-blue.svg)](https://www.sqlite.org/)

VolunteerBridge is a web application built with Flask designed to connect Non-Governmental Organizations (NGOs) with potential volunteers. It provides a platform for NGOs to post tasks they need help with and for volunteers to find opportunities, accept tasks, track their progress, and view their contribution history.

## Overview

The core purpose of this application is to streamline the process of matching volunteer skills and availability with NGO needs. NGOs can manage their tasks and volunteer assignments, while volunteers get a clear view of available opportunities and their completed work.

## Features

**General:**

*   **User Authentication:** Secure registration and login for distinct NGO and Volunteer user types.
*   **Session Management:** Keeps users logged in using Flask's session handling.
*   **Role-Based Access:** Ensures NGOs and Volunteers can only access their respective dashboards and features.
*   **Flash Messaging:** Provides user feedback for actions (success, error, warnings).
*   **Responsive Design:** Adapts to various screen sizes using Bootstrap 5.

**For NGOs:**

*   **Dashboard:** View all created tasks, their status, and assigned volunteers.
*   **Task Creation:** Post new volunteering opportunities with titles and descriptions.
*   **Profile Management:** Update organization description, mission, and contact details.

**For Volunteers:**

*   **Dashboard:** View assigned tasks, available opportunities, and quick links.
*   **View Opportunities:** Browse all available tasks posted by NGOs.
*   **Accept Tasks:** Claim available tasks to volunteer for.
*   **Complete Tasks:** Mark assigned tasks as completed.
*   **Volunteering History:** View a record of all completed tasks, including dates and NGOs helped.
*   **Profile Management:** Update contact info, availability, skills, and interests.

## Technology Stack

*   **Backend Framework:** [Flask](https://flask.palletsprojects.com/) (Python)
*   **Programming Language:** [Python](https://www.python.org/) (3.10+)
*   **Database:** [SQLite 3](https://www.sqlite.org/index.html) (File-based relational database)
*   **Frontend Framework:** [Bootstrap 5.3](https://getbootstrap.com/) (CSS & JS Components)
*   **Templating Engine:** [Jinja2](https://jinja.palletsprojects.com/)
*   **Version Control:** [Git](https://git-scm.com/) & [GitHub](https://github.com/)
*   **Libraries:** Standard Python libraries (`os`, `sqlite3`, `datetime`, `functools`)

## Setup and Installation

Follow these steps to set up the project locally:

1.  **Prerequisites:**
    *   [Git](https://git-scm.com/downloads) installed.
    *   [Python 3.10](https://www.python.org/downloads/) or later installed.
    *   `pip` (Python package installer, usually included with Python).

2.  **Clone the Repository:**
    ```bash
    git clone https://github.com/ombhortake/VolunteerBridge-aka-ngo-v-app-.git
    cd VolunteerBridge-aka-ngo-v-app-
    ```
    *(Replace the URL if your repository URL is different)*

3.  **Create and Activate a Virtual Environment:** (Recommended)
    *   **Windows:**
        ```bash
        python -m venv venv
        .\venv\Scripts\activate
        ```
    *   **macOS / Linux:**
        ```bash
        python3 -m venv venv
        source venv/bin/activate
        ```

4.  **Install Dependencies:**
    *   Currently, the main dependency is Flask.
    ```bash
    pip install Flask
    ```
    *   *(Optional but Recommended: Create a `requirements.txt` file)*
        ```bash
        pip freeze > requirements.txt
        ```
        *   *(If `requirements.txt` exists, you can install using: `pip install -r requirements.txt`)*

5.  **Database Setup:**
    *   The SQLite database (`database/ngo_volunteer.db`) and its tables will be created automatically the first time you run the application if the file doesn't exist.

## Running the Application

1.  Make sure your virtual environment is activated.
2.  Navigate to the project's root directory (where `app.py` is located).
3.  Run the Flask development server:
    ```bash
    python app.py
    ```
    *(Or potentially `python3 app.py` depending on your system setup)*
4.  Open your web browser and go to: `http://127.0.0.1:5001` (or the address shown in the terminal).

## Usage

1.  **Register:** Create an account as either an "NGO" or a "Volunteer".
2.  **Login:** Log in using your registered credentials and selected user type.
3.  **Navigate:** Use the navigation bar (once logged in) to access your dashboard, profile, or other relevant sections.
4.  **NGOs:** Create tasks, view task status on the dashboard.
5.  **Volunteers:** Browse opportunities, accept tasks, mark tasks as complete on the dashboard, view history.
6.  **Update Profile:** Both user types can update their profile information.
7.  **Logout:** Click the user dropdown in the navbar and select "Logout".

## Database Schema

The application uses an SQLite database with the following main tables:

*   `ngos`: Stores NGO information (name, email, password\*, details).
*   `volunteers`: Stores Volunteer information (name, email, password\*, details).
*   `tasks`: Stores task details (title, description, status, linked NGO, assigned Volunteer).
*   `volunteering_history`: Records completed tasks (linking volunteer, NGO, task, and completion date).

*\* **Note:** Passwords are currently stored insecurely.*

## Security Considerations & Disclaimer

*   **Password Security:** **CRITICAL WARNING!** This application currently stores user passwords in **plain text**, which is highly insecure. **DO NOT use this in a production environment or with real user data without implementing proper password hashing** (e.g., using `werkzeug.security`'s `generate_password_hash` and `check_password_hash`).
*   **Development Status:** This application is intended as a demonstration or portfolio piece. It lacks robust security features like CSRF protection, comprehensive input validation/sanitization (XSS prevention), and HTTPS enforcement needed for production deployment.
*   **Debug Mode:** The application runs with `debug=True` for development convenience. **This MUST be set to `False` in any production scenario.**

## Contributing

Contributions, issues, and feature requests are welcome. Please feel free to fork the repository, make changes, and submit a pull request, or open an issue to report bugs or suggest improvements.

## License

*(Optional: Choose a license if you want to make your code open source)*

Example: This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details (you would need to create this file and add the MIT license text).

Or: This project is currently not licensed for open distribution.

## Contact

[ombhortake] - [(https://github.com/ombhortake)]

Project Link: [https://github.com/ombhortake/VolunteerBridge-aka-ngo-v-app-](https://github.com/ombhortake/VolunteerBridge-aka-ngo-v-app-)
