# My Django Feedback Application

This project is a feedback application built with Django, enabling users to provide and manage feedback.

## Features

# Feedback Portal: Empowering College Feedback and Faculty Development

Feedback Portal is a comprehensive feedback platform designed specifically for colleges, streamlining the feedback process and fostering a culture of continuous improvement for faculty.

## Key Features

**For Students:**

* **Anonymous or Identified Feedback:**  Students can provide feedback on faculty anonymously or with their names attached, depending on college policy.
* **Structured Feedback Forms:** Pre-defined forms guide students to provide specific and actionable feedback on teaching methods, course content, communication, and overall effectiveness.
* **Categorization:** Feedback can be categorized (e.g., teaching style, course material, workload) for easier analysis.

**For Faculty:**

* **Personalized Dashboard:** Faculty members can easily access and review feedback related to their courses.
* **Detailed Insights:** Visualizations and reports provide insights into feedback patterns, strengths, and areas for improvement.
* **Feedback Response Tools:** Faculty can respond to feedback directly, fostering a dialogue and showing their commitment to continuous growth.

**For College Administrators:**

* **Centralized Feedback Management:** College administrators have a dashboard to oversee feedback collection, review submissions, and generate reports.
* **Faculty Performance Tracking:** Analyze feedback trends across departments and faculty members to support faculty development initiatives.
* **Policy Customization:** Configure feedback settings (anonymity, form templates, reporting) to align with the college's specific needs.

## Benefits for Colleges

* **Improved Faculty Development:** Feedback data provides valuable insights into teaching effectiveness, empowering faculty to refine their practices and enhance student learning experiences.
* **Enhanced Student Voice:** A robust feedback system provides a platform for students to share valuable insights and contribute to improving the educational environment.
* **Data-Driven Decisions:** College administrators can leverage feedback data to make informed decisions about faculty development programs, curriculum adjustments, and overall program improvement.
* **Transparent Communication:** Open communication about feedback fosters a culture of transparency and continuous improvement.

## Target Audience

* **Colleges and Universities:** Institutions seeking a reliable and user-friendly feedback platform to improve faculty performance and student experiences.
* **Faculty Members:** Faculty seeking a platform to access student feedback, gain insights, and engage in professional growth.
* **Students:** Students seeking a secure and convenient way to share constructive feedback with their professors.

## Call to Action

Feedback Portal can transform the way colleges collect, manage, and leverage feedback. https://harshavardhanvemali.netlify.app to learn more about how our platform can empower your institution.

## Screenshots / Mockups

<img width="1470" alt="Screenshot 2024-07-28 at 10 36 35 AM" src="https://github.com/user-attachments/assets/56a87a51-fa69-441d-83cc-900975db85be">

## Installation and Setup

1. **Prerequisites:**
   - **Python:** Ensure you have Python 3.8 or higher installed. [https://www.python.org/downloads/](https://www.python.org/downloads/)
2. **Virtual Environment:**
   - **Installation:**
      - Windows: `python -m pip install virtualenv`
      - macOS: `python3 -m pip install virtualenv`
      - Linux (Debian/Ubuntu): `sudo apt-get update && sudo apt-get install python3-virtualenv`
      - Linux (Fedora): `sudo dnf install python3-virtualenv`
   - **Creation:**
      - Windows/macOS/Linux: `python -m venv myenv` (Replace `myenv` with your desired environment name)
   - **Activation:**
      - Windows: `myenv\Scripts\activate`
      - macOS/Linux: `source myenv/bin/activate`
3. **Dependencies:**
   - Install the project's dependencies: `pip install -r requirements.txt`
4. **Database Setup (if necessary):**
   - If your project uses a database (e.g., PostgreSQL, MySQL), follow the database-specific instructions to create and configure the database.
5. **Migrations:**
   - Ensure the database schema is up-to-date:
      - `python manage.py makemigrations`
      - `python manage.py migrate`

## Running the Application

1. **Development Server:**
   - Start the development server: `python manage.py runserver`
   - Access the application in your web browser: `http://127.0.0.1:8000`
2. **Network Access:**
   - To allow access from other devices on your network: `python manage.py runserver 0.0.0.0:8000` 
   - Replace `0.0.0.0` with your system's IP address if necessary.
3. **Software Firewall:**
   - sudo ufw allow 8000/tcp

## Contributing

Contributions are welcome! Please follow these steps:

1. **Fork** the repository.
2. **Create** a new branch for your feature or bug fix.
3. **Commit** your changes with clear and concise messages.
4. **Push** your branch to your forked repository.
5. **Submit** a pull request to the original repository.

## License

This software is provided for informational purposes only. You may not modify,
reproduce, distribute, or use this software for any other purpose without the 
express written permission of Vemali Harshavardhan.

## Contact

- **Email:** vemalivardhan@gmail.com
- **Website** https://harshavardhanvemali.netlify.app

---
