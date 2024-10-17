# Feedback Portal - Advanced Faculty & Student Evaluation System

The Feedback Portal is a professional, data-driven platform designed for higher education institutions to streamline the feedback loop between students, faculty, and administration. By providing structured evaluation tools and automated reporting, the system facilitates continuous improvement in pedagogical methods and institutional effectiveness.

## Core Objectives

The primary goal of this platform is to transform raw student feedback into actionable insights. It addresses the challenges of traditional paper-based or unstructured feedback systems by providing a centralized, secure, and intuitive environment for all stakeholders.

## Stakeholder Roles and Functional Flows

### Students
Students are the primary source of feedback. The system simplifies their experience through:
*   **Structured Questionnaires**: Evaluations are broken down into specific domains such as course content, delivery methods, communication, and overall effectiveness.
*   **Anonymity Control**: Depending on institutional policy, students can submit feedback anonymously to ensure honesty without fear of reprisal.
*   **Submission Tracking**: Students can see which courses they have yet to evaluate, ensuring high participation rates.

### Faculty
Faculty members receive feedback as a tool for professional growth:
*   **Performance Dashboards**: Real-time visualizations of feedback metrics, allowing for immediate identification of strengths and areas for improvement.
*   **Trend Analysis**: Historical data comparison to track progress over multiple semesters.
*   **Communication Bridge**: Faculty can respond to overarching themes in feedback, fostering a culture of transparency and mutual respect.

### Feedback Management Cycle
The platform operates on a structured feedback cycle that ensures all parties are informed and engaged:
1.  **Cycle Initiation**: Administrators define the feedback window and select the active courses/faculty for evaluation.
2.  **Student Notification**: Automatic alerts are generated for students via the web interface.
3.  **Secure Submission**: Students complete evaluations through a responsive, multi-step form designed to minimize survey fatigue.
4.  **Automatic Aggregation**: As submissions arrive, the system calculates average scores and compiles qualitative feedback.
5.  **Insight Generation**: Encrypted reports are generated and released to faculty members upon cycle completion.

### Reporting and Analytics Engine
The core value of the platform lies in its ability to synthesize data:
*   **Visual Dashboards**: Interactive charts (Polar/Radar/Bar) displaying performance across various pedagogical domains.
*   **PDF Generation Strategy**: Utilizing `xhtml2pdf` and `WeasyPrint` to transform HTML templates into professional, printable PDF documents. This allows for offline review and institutional archiving.
*   **Anonymity Layer**: A specialized logic ensures that qualitative feedback is presented in a way that protects student identity while maintaining the integrity of the message.

## Technical Architecture

The platform is built on a robust modern stack to ensure scalability, security, and performance:

*   **Framework**: Django 5.0 (Python-based), providing a secure and scalable backend.
*   **Database**: Designed for PostgreSQL in production with SQLite supported for development.
*   **Real-time Features**: Integration with Django Channels for live updates and notifications.
*   **Document Generation**: Utilizes xhtml2pdf and WeasyPrint to generate professional-grade PDF reports for faculty and administration.
*   **Static Management**: WhiteNoise is implemented for efficient serving of static assets.
*   **Environment Security**: Sensitivity-aware configuration using environment variables for all critical settings.

## Installation and Deployment

### Prerequisites
*   Python 3.8 or higher
*   pip (Python package manager)
*   Virtual environment (venv)

### Setup Instructions

1.  **Clone the Repository**
    ```bash
    git clone https://github.com/HarshavardhanVemali/Feedback.git
    cd Feedback
    ```

2.  **Environment Preparation**
    Create and activate a virtual environment:
    ```bash
    python3 -m venv venv
    source venv/bin/activate  # Windows: venv\Scripts\activate
    ```

3.  **Install Dependencies**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Configuration**
    Create a `.env` file in the root directory:
    ```env
    SECRET_KEY=your-secure-secret-key
    DEBUG=False
    ALLOWED_HOSTS=yourdomain.com,localhost,127.0.0.1
    ```

5.  **Database Migration**
    ```bash
    python manage.py makemigrations
    python manage.py migrate
    ```

6.  **Static Files**
    ```bash
    python manage.py collectstatic
    ```

7.  **Run Development Server**
    ```bash
    python manage.py runserver
    ```

## Development and Contributions

We encourage institutional developers and open-source contributors to help evolve the platform. Please refer to the [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines on code standards and pull request processes. All participants are expected to adhere to our [Code of Conduct](CODE_OF_CONDUCT.md).

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Contact and Support

**Vemali Harshavardhan**
- Email: vemalivardhan@gmail.com
- Website: https://harshavardhanvemali.netlify.app

Project Repository: [https://github.com/HarshavardhanVemali/Feedback](https://github.com/HarshavardhanVemali/Feedback)
