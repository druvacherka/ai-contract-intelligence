\# AI Contract Intelligence API Documentation



\## Health Check



\### GET /health



Response:



```json

{

&#x20; "status": "healthy"

}

```



\---



\## Upload Contract



\### POST /upload



Supported Formats:



\* PDF

\* DOCX

\* TXT



Response:



```json

{

&#x20; "filename": "contract.pdf",

&#x20; "saved\_to": "uploads/contract.pdf"

}

```



\---



\## Analyze Contract Text



\### POST /analyze



Request:



```json

{

&#x20; "text": "This Agreement terminates upon breach."

}

```



Response:



```json

{

&#x20; "clause": "Termination",

&#x20; "confidence": 92.4,

&#x20; "risk\_score": 70,

&#x20; "risk\_level": "High"

}

```



\---



\## Analyze Contract File



\### POST /analyze-file



Response:



```json

{

&#x20; "filename": "contract.pdf",

&#x20; "clause": "Payment Terms",

&#x20; "confidence": 27.21,

&#x20; "risk\_score": 50,

&#x20; "risk\_level": "Medium",

&#x20; "entities": \[]

}

```



