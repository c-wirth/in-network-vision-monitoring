DATABASE MODULE README

============================================================
1. WHAT THIS MODULE IS
============================================================

This module is responsible for handling all database-related functionality in the system.

It defines:
- how data is structured
- how the application connects to the database
- how data is read and written
- how incoming data is validated

This module uses the SQLAlchemy ORM to interact with the database.


============================================================
2. WHERE IT FITS IN THE SYSTEM
============================================================

The system is organized into layers:

    UI / Routes (FastAPI)
            ↓
        Service Layer
            ↓
        Database Module

The database module is a TOOL layer.

- It does not make decisions
- It does not control workflows
- It simply provides functionality for storing and retrieving data

The service layer sits above it and controls how and when these tools are used.


============================================================
3. WHAT’S INSIDE THIS MODULE
============================================================

models.py
---------
Defines the structure of the database.

- Each class represents a table
- Defines columns and relationships between tables
- No logic, no queries

connection.py
-------------
Handles how the application connects to the database.

- Creates the database engine
- Manages sessions (how we interact with the DB)
- Provides a safe way to access the database

repositories.py
---------------
Contains all database operations.

- Functions for creating, reading, and deleting data
- Only interacts with the database
- Does NOT commit transactions

schemas.py
----------
Defines the shape of data entering and leaving the system.

- Validates incoming data
- Ensures correct data types and constraints
- Defines what data is returned to the frontend


============================================================
4. CORE DESIGN IDEAS
============================================================

Separation of Concerns
---------------------
Each part of the system has one job.

- Models → define structure
- Connection → manage access
- Repositories → handle database operations
- Schemas → validate data
- Services → control workflows

Single Responsibility
---------------------
Each file is focused on one responsibility.

No Business Logic in the DB Module
---------------------------------
This module does not decide what should happen.
It only provides tools to store and retrieve data.

Repositories Do Not Commit
-------------------------
Repositories prepare changes, but do not finalize them.

The service layer is responsible for committing or rolling back transactions.


============================================================
5. DATA FLOW (EXAMPLES)
============================================================

Create a Clip
-------------
1. The service layer handles file creation and determines a file path
2. The service calls the repository to create a clip record in the database
3. The service commits the transaction

Delete a Clip
-------------
1. The service retrieves the clip from the database
2. The service deletes the file from disk
3. The service deletes the database record
4. The service commits the transaction

These examples show that the database module does not control the process.
It only provides the operations used by the service layer.


============================================================
6. DATA OWNERSHIP
============================================================

The database module:
- Owns how data is structured and stored
- Provides access to that data

The service layer:
- Owns the lifecycle of data
- Decides when data is created, updated, or deleted
- Coordinates between database and other parts of the system (like file storage)

This separation prevents confusion and keeps the system organized.


============================================================
7. KEY RULES
============================================================

- Models define structure only (no logic)
- Repositories handle database operations only
- Repositories do NOT call commit()
- Schemas validate all incoming data
- The service layer controls all workflows and transactions


============================================================
END OF DOCUMENT
============================================================