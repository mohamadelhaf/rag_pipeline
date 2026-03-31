
import os

docs = {
    'data/documents/tech/infrastructure_guide.txt': '''EnergyCo Technical Infrastructure Guide

Server Management:
All production servers run on Linux Ubuntu 22.04 LTS.
To restart a server: sudo systemctl restart <service_name>
To check server status: sudo systemctl status <service_name>
SSH access requires VPN connection and a valid SSH key registered with IT.

Docker: 
All microservices are containerized using Docker.
To start all services: docker-compose up -d
To stop all services: docker-compose down
To view logs: docker logs <container_name> -f
Images are stored in the internal registry at registry.energyco.internal

Kubernetes:
Production workloads run on Kubernetes cluster k8s-prod-01.
To deploy: kubectl apply -f deployment.yaml
To check pods: kubectl get pods -n production
To view pod logs: kubectl logs <pod_name> -n production

Database Access:
PostgreSQL production DB: db-prod.energyco.internal:5432
Read-only replica for analytics: db-replica.energyco.internal:5432
All credentials are stored in Azure Key Vault.
Never hardcode database credentials in code.

Incident Response:
P1 incidents must be reported within 15 minutes to the on-call team.
On-call rotation is managed via PagerDuty.
Incident channel: Teams #incidents-prod
Post-mortem required for all P1 and P2 incidents within 48 hours.
''',

    'data/documents/tech/api_standards.txt': '''EnergyCo API Development Standards

REST API Guidelines:
All APIs must follow RESTful conventions.
Use plural nouns for endpoints: /employees not /employee
HTTP methods: GET (read), POST (create), PUT (update), DELETE (delete)
All responses must return JSON with Content-Type: application/json
API versioning is mandatory: /api/v1/resource

Authentication:
All APIs must use OAuth2 with Azure AD.
JWT tokens expire after 1 hour.
Refresh tokens are valid for 24 hours.
Never pass tokens in URL parameters, always use Authorization header.

Error Handling:
400 Bad Request: invalid input
401 Unauthorized: missing or invalid token
403 Forbidden: insufficient permissions
404 Not Found: resource does not exist
500 Internal Server Error: unexpected server error
All error responses must include a message and error_code field.

Performance Standards:
API response time must be under 200ms for 95% of requests.
Maximum payload size: 10MB
Rate limiting: 1000 requests per minute per client
Pagination required for endpoints returning more than 100 items.

Documentation:
All APIs must be documented using OpenAPI 3.0 (Swagger).
Documentation must be kept up to date with every release.
''',

    'data/documents/compliance/gdpr_policy.txt': '''EnergyCo GDPR Compliance Policy

Data Classification:
Personal data includes: names, email addresses, phone numbers, location data.
Sensitive personal data includes: health data, biometric data, political opinions.
All personal data must be classified before processing.

Data Retention:
Employee data: retained for 5 years after employment ends.
Customer data: retained for 3 years after last interaction.
Log files containing personal data: maximum 90 days retention.
Financial records: 10 years as required by French law.

Data Subject Rights:
Employees and customers have the right to access their personal data.
Data access requests must be fulfilled within 30 days.
Right to erasure requests must be evaluated by the Legal team.
Data portability requests must provide data in machine-readable format.

Data Breach Procedure:
Any suspected data breach must be reported to the DPO within 24 hours.
CNIL must be notified within 72 hours of confirmed breach.
Affected individuals must be notified without undue delay.
All breaches must be documented in the breach register.

Third Party Processing:
All third-party processors must sign a Data Processing Agreement.
Cloud providers must have EU data residency or adequate protection.
Annual audit of third-party processors is mandatory.
''',

    'data/documents/compliance/security_policy.txt': '''EnergyCo Information Security Policy

Password Policy:
Minimum password length: 12 characters.
Must contain uppercase, lowercase, numbers, and special characters.
Passwords must be changed every 90 days.
Password reuse is prohibited for the last 12 passwords.
Multi-factor authentication is mandatory for all systems.

Access Control:
Access to systems follows the principle of least privilege.
Access requests must be approved by the employee manager and IT security.
Access reviews are conducted every 6 months.
Terminated employee accounts must be disabled within 24 hours.

Device Security:
All company devices must have full disk encryption enabled.
Antivirus software must be installed and kept up to date.
Personal devices may not access production systems.
Lost or stolen devices must be reported to IT within 1 hour.

Network Security:
VPN is mandatory when accessing company resources remotely.
Public WiFi must not be used without VPN.
All network traffic is logged and monitored.
Firewall rules must be reviewed and approved by IT Security.

Incident Reporting:
Security incidents must be reported to security@energyco.com immediately.
Phishing emails must be forwarded to phishing@energyco.com.
Never click suspicious links or open unexpected attachments.
''',

    'data/documents/pm/project_management_guide.txt': '''EnergyCo Project Management Guidelines

Project Lifecycle:
All projects follow a 5-phase approach: Initiation, Planning, Execution, Monitoring, Closure.
Projects above 50k euros require a formal business case and executive sponsor.
Project charter must be approved before kickoff.
Lessons learned session is mandatory at project closure.

Agile Methodology:
Development teams use 2-week sprints.
Sprint planning occurs every other Monday at 9:00 AM.
Daily standups are 15 minutes maximum at 9:30 AM.
Sprint retrospectives are held on the last Friday of each sprint.
Product backlog must be groomed weekly by the Product Owner.

Reporting:
Weekly status report must be submitted every Friday by 5 PM.
Status colors: Green (on track), Amber (at risk), Red (delayed).
Project dashboard must be updated in real time in SharePoint.
Steering committee meeting held monthly for projects above 100k euros.

Risk Management:
All risks must be logged in the risk register.
Risk probability and impact scored 1-5.
Risks with score above 15 require immediate escalation.
Risk register must be reviewed weekly during project execution.

Budget Management:
Budget variance above 10% requires formal change request.
All expenses above 5000 euros require two approvals.
Monthly budget review with finance team is mandatory.
Contingency reserve of 15% must be included in all project budgets.
''',

    'data/documents/pm/meeting_templates.txt': '''EnergyCo Meeting Standards and Templates

Meeting Best Practices:
All meetings must have a clear agenda sent 24 hours in advance.
Maximum meeting duration: 2 hours without a break.
Meetings should have a designated facilitator and note-taker.
Action items must be assigned with owner and due date.
Meeting minutes must be shared within 24 hours.

Standup Template:
1. What did I complete yesterday?
2. What will I work on today?
3. Are there any blockers?
Duration: 15 minutes maximum. No problem-solving during standup.

Sprint Planning Template:
1. Review sprint goal (5 min)
2. Review velocity from last sprint (10 min)
3. Select backlog items (45 min)
4. Break items into tasks (30 min)
5. Confirm sprint commitment (10 min)
Duration: 2 hours for 2-week sprint.

Steering Committee Template:
1. Executive summary (10 min)
2. Progress against milestones (15 min)
3. Budget status (10 min)
4. Risk and issues update (10 min)
5. Decisions required (15 min)
Duration: 1 hour.

Retrospective Template:
1. What went well?
2. What could be improved?
3. What will we commit to change next sprint?
Duration: 1 hour for 2-week sprint.
''',

    'data/documents/general/company_overview.txt': '''EnergyCo Company Overview

About EnergyCo:
EnergyCo is a leading energy company operating across France and Europe.
Founded in 1945, EnergyCo employs over 150,000 people worldwide.
Headquarters: Paris, France.
EnergyCo is committed to the energy transition and carbon neutrality by 2050.

Organizational Structure:
EnergyCo is divided into 5 main divisions:
- Generation: nuclear, renewable, and thermal energy production
- Distribution: electricity grid management and maintenance
- Digital (DIGIT): IT systems, digital transformation, and AI
- Finance: financial planning, accounting, and treasury
- HR: human resources, talent management, and training

DIGIT Division:
The DIGIT division is responsible for all IT and digital initiatives.
DIGIT employs over 5000 IT professionals across France.
Key focus areas: cloud migration, AI/ML, cybersecurity, and data platforms.
DIGIT operates under the CIO who reports directly to the CEO.

Values:
Safety first: no compromise on safety in any operation.
Integrity: transparency and honesty in all interactions.
Innovation: continuous improvement and adoption of new technologies.
Sustainability: commitment to reducing environmental impact.

Contact:
General inquiries: info@energyco.com
IT support: helpdesk@energyco.com
HR inquiries: hr@energyco.com
Security incidents: security@energyco.com
'''
}

for path, content in docs.items():
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w') as f:
        f.write(content)
    print(f'✅ Created {path}')

print('\\n🎉 All documents created!')
