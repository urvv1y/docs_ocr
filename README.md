# OCR Scanner for documents
- using **Python - FastAPI** for image processing
- using **Java - Spring Boot** for backend
- **PostgreSQL** database
- entire project containerized with **Docker**

---


### A project whose purpose was mainly to develop my skills in Java, SpringBoot, Docker, and database.

---

### Installation
- Clone the repository
- Build the containers using **Docker Compose**

`` docker-compose up -d --build ``

- Check the status of containers

`` docker ps ``

To view the application logs:

``docker-compose logs -f``

To stop the application:

``docker-compose down``

## API Documentation

The Java backend exposes REST endpoints on `http://localhost:8080`.

### 1. Upload an Invoice
Extracts data from an invoice image and saves it to the database.
*   **URL:** `/api/upload-invoice`
*   **Method:** `POST`
*   **Parameters (Query):** 
    *   `lang` (optional) - Language of the document (default: `ces`, options: `ces`, `eng`).
*   **Body (form-data):**
    *   `file` - The image file (PNG/JPG).
*   **Example Response:**
    ```json
    "Invoice saved 1"
    ```

### 2. Upload a Receipt
Extracts data from a receipt image and saves it to the database.
*   **URL:** `/api/upload`
*   **Method:** `POST`
*   **Parameters (Query):** 
    *   `lang` (optional) - Language of the document (default: `ces`).
*   **Body (form-data):**
    *   `file` - The image file (PNG/JPG).
*   **Example Response:**
    ```json
    "Document read successfully - doc_id: 1"
    ```

### 3. Get All Invoices
Retrieves a list of all processed invoices from the PostgreSQL database, sorted by ID.
*   **URL:** `/api/invoices`
*   **Method:** `GET`
*   **Example Response:**
    ```json
    [
      {
        "id": 1,
        "invoiceNumber": "2600253",
        "invoiceDate": "12.03.2026",
        "dueDate": "26.03.2026",
        "seller": "Firma s.r.o.",
        "customer": "Odběratel a.s.",
        "description": null,
        "goods": {},
        "totalPrice": "3202315.00",
        "paymentMethod": "příkazem",
        "bank": "1234567891/0321"
      }
    ]
    ```

### 4. Get All Receipts
Retrieves a list of all processed receipts.
*   **URL:** `/api/receipts`
*   **Method:** `GET`

---

##  Development & Database Access

*   **FastAPI Swagger UI:** `http://localhost:8000/docs` (Direct access to the OCR microservice)
*   **PostgreSQL Database:**
    *   **Host:** `localhost`
    *   **Port:** `5432`
    *   **Database:** `ocrdb`
    *   **Username:** `postgres`
    *   **Password:** `heslo123`
    *(Use clients like DBeaver, pgAdmin, or DataGrip to inspect the tables).*
