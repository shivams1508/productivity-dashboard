AI-Powered Worker Productivity Dashboard
A Full-Stack Solution for Real-Time Factory Analytics

PROJECT OVERVIEW
This project was developed as a technical assessment to demonstrate a production-style pipeline for manufacturing analytics. The system ingests structured event data from AI-powered CCTV cameras, processes those events in a backend API, and visualizes key productivity metrics through a clean, intuitive dashboard.

As a developer, my goal was to create a "warm" experience where the system is ready to use immediately upon deployment, while maintaining the flexibility to scale into a real-world factory environment.

 THE ARCHITECTURE
I designed the system using a decoupled architecture to ensure the frontend remains fast even as the database grows.

Edge Layer: Simulates CCTV systems generating JSON events (Working, Idle, Product Count).

Backend (Flask): A RESTful API that validates incoming data and manages the business logic for productivity calculations.

Database (SQLite): A portable, relational database that persists worker and workstation metadata along with all historical events.

Frontend (Tailwind CSS & JS): A responsive dashboard that uses short-polling to provide near real-time updates without the overhead of WebSockets for this scale.

 METRIC DEFINITIONS AND LOGIC
To provide actionable insights, I implemented the following logic:

Utilization %: Calculated as (Working Events / Total Activity Logs) * 100. This provides a snapshot of how effectively time is being used on the floor.

Throughput: Aggregated product_count events per worker and workstation to identify high-performers and potential bottlenecks.

Factory-Level Averages: Consolidated metrics to give floor managers a "bird's-eye view" of total production health.

Strategic Thinking (Theoretical Questions)
How do you handle connectivity and out-of-order events?
In a factory setting, Wi-Fi is rarely perfect. I recommend an Edge-side Buffer. Events should be timestamped at the source (the camera) and stored in a local queue (like Redis or local storage) if the connection drops. When back online, the API processes these in batches based on their original timestamps to maintain data integrity.

How do you detect and handle "Model Drift"?
AI models can lose accuracy if factory lighting changes or cameras shift. I've included a confidence field in the event schema. By monitoring this metric, we can set automated alerts: if the average confidence falls below a set threshold (e.g., 85%), it triggers a notification for a manual audit or a model retraining cycle.

How does this scale from 5 to 100+ cameras?
For a multi-site rollout, I would transition from a single-threaded SQLite database to PostgreSQL or a distributed SQL solution. To prevent the API from becoming a bottleneck, I would introduce a message broker like Apache Kafka to handle the high-frequency ingestion asynchronously.

Quick Start
Environment: python -m venv venv and activate it.

Dependencies: pip install -r requirements.txt.

Run: python app.py.

View: Navigate to http://127.0.0.1:5000.

Assumptions & Tradeoffs
SQLite for Portability: I chose SQLite to ensure the evaluators can run the project instantly without complex database configuration.

Short Polling: I implemented a 3-second refresh rate on the frontend. This balances the need for "real-time" data with minimal server strain for a 6-worker setup.

Next Step
Would you like me to help you write a GitHub "About" section or a LinkedIn post to share this project once you have the Vercel link?