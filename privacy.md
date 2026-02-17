Privacy Policy – Azure & M365 Change Digest Agent

Last updated: 17 February 2026

1. Purpose

This service provides automated summaries of Microsoft Azure and Microsoft 365 change announcements using a locally hosted change collector and n8n webhook integration.

2. Data Processed

The service processes the following data:
	•	Public Microsoft change announcements (Azure, Microsoft 365, Defender, Intune, Entra)
	•	Metadata such as title, summary, source URL, release stage, timestamps
	•	Query parameters sent to the webhook (hours, ga_only, security_only)

No personal data of end users is collected or stored.

3. Data Storage
	•	Change data is stored locally within a self-hosted container environment.
	•	Storage backend: local SQLite database.
	•	No data is shared with third parties beyond Microsoft Graph APIs used for ingestion.

4. Data Transmission

When the OpenAI agent calls the webhook:
	•	Only request parameters are transmitted.
	•	No user-identifiable content is forwarded.
	•	The webhook requires an API key header for authentication.
	•	IP Whitelisting is active

5. Security Measures
	•	HTTPS enforced via reverse proxy.
	•	API key authentication for webhook access.
	•	Local container network isolation.
	•	No public database exposure.
	•	All data is public available.
	
7. Third-Party Services

This system interacts with:
	•	Microsoft Graph API
	•	OpenAI platform (for agent interaction)

Each operates under their respective privacy policies.

7. Contact

For questions regarding this service see the Github profile details
