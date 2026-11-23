import mysql.connector
from fastapi.security import OAuth2PasswordBearer
from fastapi import Depends
from jose import jwt, JWTError
from app.auth import SECRET_KEY, ALGORITHM
from fastapi import FastAPI, UploadFile, File, HTTPException

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/auth/token"
)
def get_connection():
    connection = mysql.connector.connect(
        host="localhost",
        user="root",
        password="9717106487",
        database="medassist"
    )

    return connection

def create_user(name, email, password_hash):
    connection = get_connection()

    cursor = connection.cursor()

    query = """
        INSERT INTO users (name, email, password_hash)
        VALUES (%s, %s, %s)
    """

    cursor.execute(query, (name, email, password_hash))

    connection.commit()

    cursor.close()
    connection.close()

def get_user_by_email(email):
    connection = get_connection()
    cursor = connection.cursor()

    query = """
        SELECT id, name, email, password_hash
        FROM users
        WHERE email = %s
    """

    cursor.execute(query, (email,))

    user = cursor.fetchone()

    cursor.close()
    connection.close()

    return user



def create_document(
    user_id,
    file_name,
    file_type,
    extracted_text
):
    connection = get_connection()
    cursor = connection.cursor()

    query = """
        INSERT INTO documents
        (user_id, file_name, file_type, extracted_text)
        VALUES (%s, %s, %s, %s)
    """

    cursor.execute(
        query,
        (
            user_id,
            file_name,
            file_type,
            extracted_text
        )
    )

    connection.commit()

    document_id = cursor.lastrowid

    cursor.close()
    connection.close()

    return document_id

def get_documents_by_user(user_id):
    connection = get_connection()
    cursor = connection.cursor()

    query = """
        SELECT id, file_name, file_type, uploaded_at
        FROM documents
        WHERE user_id = %s
        ORDER BY uploaded_at DESC
    """

    cursor.execute(query, (user_id,))

    documents = cursor.fetchall()

    cursor.close()
    connection.close()

    return documents

def get_current_user(
    token: str = Depends(oauth2_scheme)
):
    try:
        payload = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[ALGORITHM]
        )

        user_id = payload.get("user_id")

        if user_id is None:
            raise HTTPException(
                status_code=401,
                detail="Invalid token"
            )

        return user_id

    except JWTError:
        raise HTTPException(
            status_code=401,
            detail="Invalid token"
        )


def create_conversation(user_id, title):

    connection = get_connection()
    cursor = connection.cursor()

    query = """
        INSERT INTO conversations
        (user_id, title)
        VALUES (%s, %s)
    """

    cursor.execute(
        query,
        (user_id, title)
    )

    connection.commit()

    conversation_id = cursor.lastrowid

    cursor.close()
    connection.close()

    return conversation_id

def create_message(
    conversation_id,
    role,
    content
):

    connection = get_connection()
    cursor = connection.cursor()

    query = """
        INSERT INTO messages
        (conversation_id, role, content)
        VALUES (%s, %s, %s)
    """

    cursor.execute(
        query,
        (
            conversation_id,
            role,
            content
        )
    )

    connection.commit()

    cursor.close()
    connection.close()



def get_messages(conversation_id):

    connection = get_connection()
    cursor = connection.cursor()

    query = """
        SELECT role, content, timestamp
        FROM messages
        WHERE conversation_id = %s
        ORDER BY timestamp ASC
    """

    cursor.execute(
        query,
        (conversation_id,)
    )

    messages = cursor.fetchall()

    cursor.close()
    connection.close()

    return messages


def create_chunks(document_id, user_id, chunk_rows):
    """
    chunk_rows: list of (chunk_text, embedding_bytes), in chunk order.
    """
    connection = get_connection()
    cursor = connection.cursor()

    query = """
        INSERT INTO document_chunks
        (document_id, user_id, chunk_index, chunk_text, embedding)
        VALUES (%s, %s, %s, %s, %s)
    """

    rows = [
        (document_id, user_id, i, text, emb)
        for i, (text, emb) in enumerate(chunk_rows)
    ]

    cursor.executemany(query, rows)

    connection.commit()

    cursor.close()
    connection.close()


def get_chunks_by_user(user_id):
    connection = get_connection()
    cursor = connection.cursor()

    query = """
        SELECT chunk_text, embedding
        FROM document_chunks
        WHERE user_id = %s
        ORDER BY document_id, chunk_index
    """

    cursor.execute(query, (user_id,))

    chunks = cursor.fetchall()

    cursor.close()
    connection.close()

    return chunks


if __name__ == "__main__":
    

    print("User created!")

