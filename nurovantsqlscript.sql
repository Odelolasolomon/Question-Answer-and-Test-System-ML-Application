-- Create Document Table

CREATE TABLE Document (
    id SERIAL PRIMARY KEY, -- A unique identifier for each document, automatically generated
    content TEXT NOT NULL -- A text field that stores the content of the document.
);

-- Create TestQuestion Table
CREATE TABLE TestQuestion (
    id SERIAL PRIMARY KEY,
    question VARCHAR(255) NOT NULL, -- A string field that stores the test question
    correct_answer TEXT NOT NULL, -- A text field that stores the correct answer associated with the test question.
    document_id INT REFERENCES Document(id) ON DELETE CASCADE -- A foreign key that references the id field in the Document table, ensuring that each test question is linked to a document.
);

select * from Document
select * from TestQuestion

-- Check the current user--
select current_user,now()



